using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.IO;
using System.Linq;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.VisualStudio.Imaging.Interop;
using Microsoft.VisualStudio.Language.Intellisense;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Utilities;

namespace KCppAssist
{
    /// <summary>
    /// 電球(Ctrl+.)に、このツールの機能を出す。カーソルの位置の関数や文を見て、使えるものだけを並べる。
    /// 判断はバックグラウンドで、保存済みのファイルを読んで行う(開いているだけの未保存の相手は見ない)。実行は、各コマンドと同じ処理を呼ぶ。
    /// </summary>
    [Export(typeof(ISuggestedActionsSourceProvider))]
    [Name("K-CppAssist Quick Fix")]
    [ContentType("C/C++")]
    internal sealed class QuickFixProvider : ISuggestedActionsSourceProvider
    {
        [Import] internal ITextDocumentFactoryService Documents { get; set; }

        public ISuggestedActionsSource CreateSuggestedActionsSource(ITextView textView, ITextBuffer textBuffer)
        {
            if (textView == null || textBuffer == null) return null;
            return new QuickFixSource(this, textView, textBuffer);
        }
    }

    internal sealed class QuickFixSource : ISuggestedActionsSource
    {
        private readonly QuickFixProvider provider;
        private readonly ITextView view;
        private readonly ITextBuffer buffer;

        public QuickFixSource(QuickFixProvider provider, ITextView view, ITextBuffer buffer)
        {
            this.provider = provider;
            this.view = view;
            this.buffer = buffer;
        }

        public event EventHandler<EventArgs> SuggestedActionsChanged { add { } remove { } }

        public Task<bool> HasSuggestedActionsAsync(ISuggestedActionCategorySet requestedActionCategories, SnapshotSpan range, CancellationToken cancellationToken)
        {
            return Task.Run(() => Collect(range).Count > 0, cancellationToken);
        }

        public IEnumerable<SuggestedActionSet> GetSuggestedActions(ISuggestedActionCategorySet requestedActionCategories, SnapshotSpan range, CancellationToken cancellationToken)
        {
            var actions = Collect(range);
            if (actions.Count == 0) return Enumerable.Empty<SuggestedActionSet>();
            return new[] { new SuggestedActionSet(PredefinedSuggestedActionCategoryNames.Any, actions, null, SuggestedActionSetPriority.Low, null) };
        }

        public bool TryGetTelemetryId(out Guid telemetryId) { telemetryId = Guid.Empty; return false; }

        public void Dispose() { }

        private readonly object cacheGate = new object();
        private ITextSnapshot cachedSnapshot;
        private int cachedPos = -1;
        private List<ISuggestedAction> cachedList;

        /// <summary>
        /// range の位置で使える機能の一覧。VS は、キャレットが動くたびに HasSuggestedActions と GetSuggestedActions の両方を呼ぶので、
        /// 同じ文字・同じ位置なら、前の結果を使う。
        /// </summary>
        private List<ISuggestedAction> Collect(SnapshotSpan range)
        {
            lock (cacheGate)
                if (cachedSnapshot == range.Snapshot && cachedPos == range.Start.Position && cachedList != null) return cachedList;
            var result = CollectCore(range);
            lock (cacheGate) { cachedSnapshot = range.Snapshot; cachedPos = range.Start.Position; cachedList = result; }
            return result;
        }

        /// <summary>電球の項目を決めるのに使う、カーソルの位置の情報。提供元(Offer...)が読む。</summary>
        private sealed class OfferContext
        {
            public OptionsPage Options;
            public string Path;
            public string Text;
            public int Caret;
            public string LineText;
            public int LineStart, LineEnd;
            public List<FunctionScan.Sig> Sigs;
            public FunctionScan.Sig Sig;          // カーソルの位置の関数(なければ null)
            public bool Header;
            public List<ISuggestedAction> List;

            // 「メンバーからコンストラクターを作る」は、書き換えの一覧のコンストラクターの項目のすぐ下に出す
            public ISuggestedAction CtorAction;
            public int CtorAt = -1;
        }

        // 同じ文字(スナップショット)なら、読み込んだ文字と、関数の一覧を使い回す。キャレットを動かすたびに、ファイル全体を読み直さない
        private ITextSnapshot scanSnapshot;
        private string scanText;
        private List<FunctionScan.Sig> scanSigs;

        private void TextAndSigs(ITextSnapshot snapshot, out string text, out List<FunctionScan.Sig> sigs)
        {
            lock (cacheGate)
                if (scanSnapshot == snapshot) { text = scanText; sigs = scanSigs; return; }
            text = snapshot.GetText();
            sigs = FunctionScan.Scan(text);
            lock (cacheGate) { scanSnapshot = snapshot; scanText = text; scanSigs = sigs; }
        }

        private List<ISuggestedAction> CollectCore(SnapshotSpan range)
        {
            var list = new List<ISuggestedAction>();
            try
            {
                var opt = SyncService.Options;
                if (opt == null || !opt.ShowQuickFix) return list;
                ITextDocument doc;
                if (!provider.Documents.TryGetTextDocument(buffer, out doc)) return list;
                var c = new OfferContext { Options = opt, Path = doc.FilePath, Caret = range.Start.Position, List = list };
                List<FunctionScan.Sig> sigs;
                TextAndSigs(range.Snapshot, out c.Text, out sigs);
                c.Sigs = sigs;
                var line = range.Snapshot.GetLineFromPosition(c.Caret);
                c.LineText = line.GetText();
                c.LineStart = line.Start.Position;
                c.LineEnd = line.End.Position;
                int caret = c.Caret;
                c.Sig = sigs.FirstOrDefault(s => (caret >= s.NameStart && caret <= s.Close + 1) || (s.Open >= c.LineStart && s.Open <= c.LineEnd));
                c.Header = IncludeService.IsHeader(c.Path);

                // 並べる順は、ここに書いた順。項目を足すときは、提供元の関数を作って、ここに足す
                OfferDeclarationDefinition(c);
                OfferForwardFromInclude(c);
                OfferMoveBody(c);
                OfferClassLine(c);
                OfferDeclareVariable(c);
                OfferAccessors(c);
                OfferForwardMember(c);
                OfferMissingInclude(c);
                OfferIncludeTidy(c);
                OfferRefactors(c);
            }
            catch (Exception ex) { KCppAssistPackage.Log("quickfix collect failed: " + ex.Message); }
            return list;
        }

        private static readonly System.Text.RegularExpressions.Regex IncludeQuoteLine = new System.Text.RegularExpressions.Regex(@"^\s*#\s*include\s*""");
        private static readonly System.Text.RegularExpressions.Regex ClassDerivedLine = new System.Text.RegularExpressions.Regex(@"^\s*(?:class|struct)\s+\w+[^;:]*:[^;]*$");
        private static readonly System.Text.RegularExpressions.Regex ClassLine = new System.Text.RegularExpressions.Regex(@"^\s*(?:class|struct)\s+\w+[^;]*$");
        private static readonly System.Text.RegularExpressions.Regex MemberDeclLine = new System.Text.RegularExpressions.Regex(@"^\s*(?:(?:static|mutable|const|inline)\s+)*[A-Za-z_][\w:<>,\s\*&]*?\s+[A-Za-z_]\w*\s*(?:=[^;]*|\{[^}]*\})?;\s*(?://.*)?$");
        private static readonly System.Text.RegularExpressions.Regex NotMemberLine = new System.Text.RegularExpressions.Regex(@"^\s*(?:return|using|typedef|friend|delete|goto)");
        private static readonly System.Text.RegularExpressions.Regex ForwardableMember = new System.Text.RegularExpressions.Regex(
            @"(?:(?:unique_ptr|shared_ptr|weak_ptr|ComPtr|observer_ptr)\s*<\s*(?:const\s+)?(?:[A-Za-z_]\w*::)*([A-Za-z_]\w*)\s*>|(?:const\s+)?(?:[A-Za-z_]\w*::)*([A-Za-z_]\w*)\s*[*&])\s*[A-Za-z_]\w*\s*(?:=[^;]*|\{[^}]*\})?;");

        /// <summary>ヘッダーの関数の宣言 ⇄ cpp の定義: 相手がなければ作る。あれば、引数が違うときだけ合わせる。</summary>
        private void OfferDeclarationDefinition(OfferContext c)
        {
            var sig = c.Sig;
            if (sig != null && !sig.HasBody && c.Header)
            {
                // 同じ名前の cpp に定義がなければ「定義を作る」。あれば、引数が違うときだけ「引数を合わせる」
                var def = Counterparts(c.Path, sig, c.Text, true);
                if (def == Counterpart.None && !sig.Name.StartsWith("~")) c.List.Add(Action("宣言から cpp に定義を作る", () => Invoke(p => p.RunCreate())));
                else if (def == Counterpart.Different) c.List.Add(Action("cpp の定義の引数を、この宣言に合わせる", () => Invoke(p => p.RunSync())));
            }
            else if (sig != null && sig.HasBody && !sig.InClass && sig.Class != null && !c.Header)
            {
                var decl = Counterparts(c.Path, sig, c.Text, false);
                if (decl == Counterpart.None) c.List.Add(Action("定義からヘッダーに宣言を作る", () => Invoke(p => p.RunCreate())));
                else if (decl == Counterpart.Different) c.List.Add(Action("ヘッダーの宣言の引数を、この定義に合わせる", () => Invoke(p => p.RunSync())));
            }
        }

        /// <summary>ヘッダーの #include "..." の行: 前方宣言にする。</summary>
        private void OfferForwardFromInclude(OfferContext c)
        {
            if (c.Header && IncludeQuoteLine.IsMatch(c.LineText)) c.List.Add(Action("#include を前方宣言にして、cpp に #include を移す", () => Invoke(p => p.RunForward())));
        }

        /// <summary>本体のある関数: ヘッダーなら cpp へ、cpp の Class::Func ならヘッダーへ、本体を移す。</summary>
        private void OfferMoveBody(OfferContext c)
        {
            var sig = c.Sig;
            if (sig == null || !sig.HasBody || sig.InTemplate) return;
            if (c.Header && sig.InClass && sig.Class != null) c.List.Add(Action("実装を cpp に移す", () => Invoke(p => p.RunMove())));
            else if (c.Header && !sig.InClass && sig.Class == null) c.List.Add(Action("実装を cpp に移す", () => Invoke(p => p.RunMove())));
            else if (!c.Header && !sig.InClass && sig.Class != null) c.List.Add(Action("実装をヘッダーに移す", () => Invoke(p => p.RunMove())));
        }

        /// <summary>class / struct の行: override・コンストラクターを作る。コンストラクターの項目は、あとで書き換えの一覧の位置に差し込む。</summary>
        private void OfferClassLine(OfferContext c)
        {
            if (ClassDerivedLine.IsMatch(c.LineText))
            {
                c.List.Add(Action("基底クラスの仮想関数を override する", () => Invoke(p => p.RunOverride())));
                c.CtorAction = Action("メンバーからコンストラクターを作る", () => Invoke(p => p.RunCtor()));
                c.CtorAt = c.List.Count;
            }
            else if (ClassLine.IsMatch(c.LineText) && !c.LineText.Contains("enum"))
            {
                c.CtorAction = Action("メンバーからコンストラクターを作る", () => Invoke(p => p.RunCtor()));
                c.CtorAt = c.List.Count;
            }
        }

        /// <summary>宣言していない変数への代入: ローカル変数にするか、メンバー変数・定数としてヘッダーに宣言する。</summary>
        private void OfferDeclareVariable(OfferContext c)
        {
            var assign = AssignScan.Find(c.Text, c.Caret);
            if (assign == null) return;
            if (!assign.HasThis) c.List.Add(Action(L.F("ローカル変数として型を付ける ({0})", assign.Name), () => Invoke(p => p.Run(false))));
            if (CppScan.EnclosingClassRef(c.Text, c.Caret) == null) return;
            // メンバーの 4 通り。定数は static constexpr で、値(右辺)を宣言に移して、この代入の文は消す
            c.List.Add(Action(L.F("private メンバー変数としてヘッダーに宣言する ({0})", assign.Name), () => Invoke(p => p.Run(KCppAssistPackage.DeclKind.PrivateMember))));
            c.List.Add(Action(L.F("public メンバー変数としてヘッダーに宣言する ({0})", assign.Name), () => Invoke(p => p.Run(KCppAssistPackage.DeclKind.PublicMember))));
            c.List.Add(Action(L.F("private 定数 (static constexpr) としてヘッダーに宣言する ({0})", assign.Name), () => Invoke(p => p.Run(KCppAssistPackage.DeclKind.PrivateConst))));
            c.List.Add(Action(L.F("public 定数 (static constexpr) としてヘッダーに宣言する ({0})", assign.Name), () => Invoke(p => p.Run(KCppAssistPackage.DeclKind.PublicConst))));
        }

        /// <summary>メンバー変数の宣言の行: Getter・Setter を作る(Alt+E)。</summary>
        private void OfferAccessors(OfferContext c)
        {
            if (!c.Header || c.LineText.Contains("(") || MemberScan.At(c.Text, c.Caret) == null) return;
            if (!MemberDeclLine.IsMatch(c.LineText) || NotMemberLine.IsMatch(c.LineText)) return;
            c.List.Add(Action("Getter・Setter を作る", () => Invoke(p => p.RunAccessor(true, true))));
            c.List.Add(Action("Getter を作る", () => Invoke(p => p.RunAccessor(true, false))));
            c.List.Add(Action("Setter を作る", () => Invoke(p => p.RunAccessor(false, true))));
        }

        /// <summary>
        /// メンバー変数の行で、型がポインター・参照・スマート ポインターの中身なら、その型の #include を前方宣言にする。
        /// その名前のヘッダーを #include していて、まだ前方宣言していないときだけ出す。
        /// </summary>
        private void OfferForwardMember(OfferContext c)
        {
            if (!c.Header || c.LineText.Contains("(") || MemberScan.At(c.Text, c.Caret) == null) return;
            var fm = ForwardableMember.Match(c.LineText);
            string ft = fm.Success ? (fm.Groups[1].Success ? fm.Groups[1].Value : fm.Groups[2].Value) : null;
            if (ft == null || !char.IsUpper(ft[0]) || CppText.IsForwardDeclared(CppText.Mask(c.Text), ft)) return;
            if (!System.Text.RegularExpressions.Regex.IsMatch(c.Text, @"#\s*include\s*[<""](?:[^"">]*/)?" + System.Text.RegularExpressions.Regex.Escape(ft) + @"\.(?:h|hpp|hh|hxx)["">]")) return;
            string name = ft;
            c.List.Add(Action(L.F("{0} を前方宣言にする (#include を cpp に移す)", name), () => Invoke(p => p.RunForward(name))));
        }

        /// <summary>足りない #include: カーソルの名前のヘッダーを足す(Alt+I)。</summary>
        private void OfferMissingInclude(OfferContext c)
        {
            var incWord = IncludeWordAt(c.Text, c.Caret);
            if (incWord != null && c.Header && CppText.IsForwardDeclared(CppText.Mask(c.Text), incWord)) incWord = null;   // 前方宣言で済ませている
            if (incWord == null || c.Options.IncludeMode == IncludeMode.Off) return;
            string stdh = StdHeaders.Lookup(incWord);
            bool missing;
            if (stdh != null) missing = !c.Text.Contains("#include " + stdh) && !System.Text.RegularExpressions.Regex.IsMatch(c.Text, @"#\s*include\s*" + System.Text.RegularExpressions.Regex.Escape(stdh));
            else
            {
                var files = IncludeService.Index.Lookup(incWord.Substring(incWord.LastIndexOf(':') + 1)).Where(f => !string.Equals(f, c.Path, StringComparison.OrdinalIgnoreCase)).ToList();
                missing = files.Count > 0 && !files.Any(f => c.Text.Contains(Path.GetFileName(f)));
            }
            if (missing) c.List.Add(Action(L.F("#include を足す ({0})", incWord), () => Invoke(p => p.RunInclude())));
        }

        /// <summary>#include の行: このファイルの #include を整理する・使っていないものを消す。</summary>
        private void OfferIncludeTidy(OfferContext c)
        {
            if (!System.Text.RegularExpressions.Regex.IsMatch(c.LineText, @"^\s*#\s*include")) return;
            c.List.Add(Action("このファイルの #include を整理する", () => Invoke(p => p.RunTidy(false, true))));
            c.List.Add(Action("このファイルの使っていない #include を消す", () => Invoke(p => p.RunTidy(true, true))));
        }

        /// <summary>書き換え・生成(NULL → nullptr、if の反転、formatter、入力レイアウト…)。最後に、コンストラクターの項目を差し込む。</summary>
        private void OfferRefactors(OfferContext c)
        {
            string eol = CppText.Eol(c.Text);
            int lastCtor = -1;      // コンストラクター・デストラクターの項目の最後の位置
            foreach (var o in KCppAssistPackage.OffersAt(c.Path, c.Text, c.Caret, eol))
            {
                string id = o.Id;
                c.List.Add(Action(o.Title, () => Invoke(p => p.RunRefactor(id))));
                if (id.StartsWith("ctordtor", StringComparison.Ordinal)) lastCtor = c.List.Count - 1;
            }
            if (c.CtorAction != null)
            {
                // .cpp の項目がない(cpp のファイルなど)ときは、コンストラクターの 2 通りのすぐ後ろ
                c.List.Insert(lastCtor >= 0 ? lastCtor + 1 : Math.Min(c.CtorAt, c.List.Count), c.CtorAction);
            }
        }

        /// <summary>カーソルの位置の識別子(std::vector のような修飾つき)。コメント・文字列・#include の行・予約語は除く。なければ null。</summary>
        private static string IncludeWordAt(string text, int caret)
        {
            if (caret < 0 || caret > text.Length) return null;
            int s = caret, e = caret;
            Func<int, bool> id = i => i >= 0 && i < text.Length && (char.IsLetterOrDigit(text[i]) || text[i] == '_' || text[i] == ':');
            while (s > 0 && id(s - 1)) s--;
            while (e < text.Length && id(e)) e++;
            if (e <= s) return null;
            string w = text.Substring(s, e - s).Trim(':');
            if (w.Length < 2 || char.IsDigit(w[0])) return null;
            int ls = text.LastIndexOf('\n', Math.Max(0, s - 1)) + 1;
            string before = text.Substring(ls, s - ls);
            if (before.TrimStart().StartsWith("#") || before.Contains("//") || before.Count(ch => ch == '"') % 2 == 1) return null;
            return w;
        }

        private enum Counterpart { None, Same, Different }

        /// <summary>
        /// 同じ名前のファイル(.h ⇔ .cpp)から、相手を探す。None: 相手のファイルはあるが関数がない(か、ファイルが見つからない)。
        /// Same: 引数も同じ。Different: 同じ名前の関数はあるが、引数の型が違う(1 つだけのとき)。
        /// </summary>
        private static Counterpart Counterparts(string path, FunctionScan.Sig sig, string text, bool wantDefinition)
        {
            string dir = Path.GetDirectoryName(path);
            string stem = Path.GetFileNameWithoutExtension(path);
            string[] exts = wantDefinition ? new[] { ".cpp", ".cc", ".cxx" } : new[] { ".h", ".hpp", ".hh", ".hxx" };
            var files = exts.Select(e => Path.Combine(dir, stem + e)).Where(File.Exists).ToList();
            if (files.Count == 0) return wantDefinition ? Counterpart.Same : Counterpart.None;   // 定義を足す .cpp がなければ、出さない
            var keys = SignatureSync.KeyVariants(sig.Inner(text));
            var found = new List<FunctionScan.Sig>();
            var foundText = new Dictionary<FunctionScan.Sig, string>();
            foreach (string f in files)
            {
                // 開いている文書は、エディターの文字(保存前の編集を含む)。閉じているものは、更新時刻つきで覚えたディスクの文字
                string t = CallCheckHub.OpenText(f) ?? SymbolService.ReadText(f);
                if (string.IsNullOrEmpty(t)) continue;
                foreach (var s in FunctionScan.Scan(t))
                    if (SyncPlan.Counterpart(s, sig, wantDefinition) > 0) { found.Add(s); foundText[s] = t; }
            }
            if (found.Count == 0) return Counterpart.None;
            if (found.Any(s => SyncPlan.SameKeysAny(SignatureSync.KeyVariants(s.Inner(foundText[s])), keys))) return Counterpart.Same;
            return found.Count == 1 && !SignatureSync.HasDirectives(sig.Inner(text)) ? Counterpart.Different : Counterpart.Same;
        }

        private static ISuggestedAction Action(string title, Action run) { return new QuickFixAction(L.T(title), run); }

        private static void Invoke(Action<KCppAssistPackage> run)
        {
            var pkg = KCppAssistPackage.Instance;
            if (pkg == null) return;
            ThreadHelper.JoinableTaskFactory.Run(async () =>
            {
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                run(pkg);
            });
        }
    }

    internal sealed class QuickFixAction : ISuggestedAction
    {
        private readonly string title;
        private readonly Action run;

        public QuickFixAction(string title, Action run) { this.title = title; this.run = run; }

        public string DisplayText { get { return title; } }
        public string DisplayTextSuffix { get { return ""; } }
        public ImageMoniker IconMoniker { get { return default(ImageMoniker); } }
        public string IconAutomationText { get { return null; } }
        public IEnumerable<SuggestedActionSet> ActionSets { get { return null; } }
        public bool HasActionSets { get { return false; } }
        public bool HasPreview { get { return false; } }
        public string InputGestureText { get { return null; } }

        public Task<IEnumerable<SuggestedActionSet>> GetActionSetsAsync(CancellationToken cancellationToken) { return Task.FromResult<IEnumerable<SuggestedActionSet>>(null); }
        public Task<object> GetPreviewAsync(CancellationToken cancellationToken) { return Task.FromResult<object>(null); }
        public void Invoke(CancellationToken cancellationToken) { run(); }
        public bool TryGetTelemetryId(out Guid telemetryId) { telemetryId = Guid.Empty; return false; }
        public void Dispose() { }
    }
}

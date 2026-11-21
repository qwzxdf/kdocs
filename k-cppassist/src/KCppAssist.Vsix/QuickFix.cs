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

        private List<ISuggestedAction> CollectCore(SnapshotSpan range)
        {
            var list = new List<ISuggestedAction>();
            try
            {
                var opt = SyncService.Options;
                if (opt == null || !opt.ShowQuickFix) return list;
                ITextDocument doc;
                if (!provider.Documents.TryGetTextDocument(buffer, out doc)) return list;
                string path = doc.FilePath;
                string text = range.Snapshot.GetText();
                int caret = range.Start.Position;
                var line = range.Snapshot.GetLineFromPosition(caret);
                var sigs = FunctionScan.Scan(text);
                var sig = sigs.FirstOrDefault(s => (caret >= s.NameStart && caret <= s.Close + 1) || (s.Open >= line.Start.Position && s.Open <= line.End.Position));
                bool header = IncludeService.IsHeader(path);

                if (sig != null && !sig.HasBody && header)
                {
                    // 同じ名前の cpp に定義がなければ「定義を作る」。あれば、引数が違うときだけ「引数を合わせる」
                    var def = Counterparts(path, sig, text, true);
                    if (def == Counterpart.None && !sig.Name.StartsWith("~")) list.Add(Action("宣言から cpp に定義を作る", () => Invoke(p => p.RunCreate())));
                    else if (def == Counterpart.Different) list.Add(Action("cpp の定義の引数を、この宣言に合わせる", () => Invoke(p => p.RunSync())));
                }
                else if (sig != null && sig.HasBody && !sig.InClass && sig.Class != null && !header)
                {
                    var decl = Counterparts(path, sig, text, false);
                    if (decl == Counterpart.None) list.Add(Action("定義からヘッダーに宣言を作る", () => Invoke(p => p.RunCreate())));
                    else if (decl == Counterpart.Different) list.Add(Action("ヘッダーの宣言の引数を、この定義に合わせる", () => Invoke(p => p.RunSync())));
                }

                // ヘッダーの #include "..." の行: 前方宣言にする
                if (header && System.Text.RegularExpressions.Regex.IsMatch(line.GetText(), @"^\s*#\s*include\s*""")) list.Add(Action("#include を前方宣言にして、cpp に #include を移す", () => Invoke(p => p.RunForward())));

                // 本体のある関数: ヘッダーなら cpp へ、cpp の Class::Func ならヘッダーへ、本体を移す
                if (sig != null && sig.HasBody && !sig.InTemplate)
                {
                    if (header && sig.InClass && sig.Class != null) list.Add(Action("関数の本体を cpp に移す", () => Invoke(p => p.RunMove())));
                    else if (header && !sig.InClass && sig.Class == null) list.Add(Action("関数の本体を cpp に移す", () => Invoke(p => p.RunMove())));
                    else if (!header && !sig.InClass && sig.Class != null) list.Add(Action("関数の本体をヘッダーに移す", () => Invoke(p => p.RunMove())));
                }

                // class / struct の行: override・コンストラクターを作る
                string lineText = line.GetText();
                if (System.Text.RegularExpressions.Regex.IsMatch(lineText, @"^\s*(?:class|struct)\s+\w+[^;:]*:[^;]*$")) { list.Add(Action("基底クラスの仮想関数を override する", () => Invoke(p => p.RunOverride()))); list.Add(Action("メンバーからコンストラクターを作る", () => Invoke(p => p.RunCtor()))); }
                else if (System.Text.RegularExpressions.Regex.IsMatch(lineText, @"^\s*(?:class|struct)\s+\w+[^;]*$") && !lineText.Contains("enum")) list.Add(Action("メンバーからコンストラクターを作る", () => Invoke(p => p.RunCtor())));

                // 宣言していない変数への代入: 型を付ける。メンバー関数の中なら、メンバー変数にもできる
                var assign = AssignScan.Find(text, caret);
                if (assign != null)
                {
                    if (!assign.HasThis) list.Add(Action("ローカル変数として型を付ける (" + assign.Name + ")", () => Invoke(p => p.Run(false))));
                    if (CppScan.EnclosingClassRef(text, caret) != null) list.Add(Action("メンバー変数としてヘッダーに宣言する (" + assign.Name + ")", () => Invoke(p => p.Run(true))));
                }

                // メンバー変数の宣言の行: ゲッター・セッターを作る(Alt+E)
                if (header && !lineText.Contains("(") && MemberScan.At(text, caret) != null
                    && System.Text.RegularExpressions.Regex.IsMatch(lineText, @"^\s*(?:(?:static|mutable|const|inline)\s+)*[A-Za-z_][\w:<>,\s\*&]*?\s+[A-Za-z_]\w*\s*(?:=[^;]*|\{[^}]*\})?;\s*(?://.*)?$")
                    && !System.Text.RegularExpressions.Regex.IsMatch(lineText, @"^\s*(?:return|using|typedef|friend|delete|goto)"))
                    list.Add(Action("ゲッター・セッターを作る", () => Invoke(p => p.RunAccessor())));

                // 足りない #include: カーソルの名前のヘッダーを足す(Alt+F)
                var incWord = IncludeWordAt(text, caret);
                if (incWord != null && opt.IncludeMode != IncludeMode.Off)
                {
                    string stdh = StdHeaders.Lookup(incWord);
                    bool missing = false;
                    if (stdh != null) missing = !text.Contains("#include " + stdh) && !System.Text.RegularExpressions.Regex.IsMatch(text, @"#\s*include\s*" + System.Text.RegularExpressions.Regex.Escape(stdh));
                    else
                    {
                        var files = IncludeService.Index.Lookup(incWord.Substring(incWord.LastIndexOf(':') + 1)).Where(f => !string.Equals(f, path, StringComparison.OrdinalIgnoreCase)).ToList();
                        missing = files.Count > 0 && !files.Any(f => text.Contains(Path.GetFileName(f)));
                    }
                    if (missing) list.Add(Action("#include を足す (" + incWord + ")", () => Invoke(p => p.RunInclude())));
                }

                // #include の行: このファイルの #include を整理する・使っていないものを消す
                if (System.Text.RegularExpressions.Regex.IsMatch(lineText, @"^\s*#\s*include"))
                {
                    list.Add(Action("このファイルの #include を整理する", () => Invoke(p => p.RunTidy(false, true))));
                    list.Add(Action("このファイルの使っていない #include を消す", () => Invoke(p => p.RunTidy(true, true))));
                }

                // 書き換え・生成(NULL → nullptr、if の反転、formatter、入力レイアウト…)
                string eol = CppText.Eol(text);
                foreach (var o in KCppAssistPackage.OffersAt(path, text, caret, eol))
                {
                    string id = o.Id;
                    list.Add(Action(o.Title, () => Invoke(p => p.RunRefactor(id))));
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("quickfix collect failed: " + ex.Message); }
            return list;
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

        private static ISuggestedAction Action(string title, Action run) { return new QuickFixAction(title, run); }

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

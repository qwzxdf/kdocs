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

        /// <summary>range の位置で使える機能の一覧。重い処理はしない。</summary>
        private List<ISuggestedAction> Collect(SnapshotSpan range)
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

                // 宣言していない変数への代入: 型を付ける。メンバー関数の中なら、メンバー変数にもできる
                var assign = AssignScan.Find(text, caret);
                if (assign != null)
                {
                    if (!assign.HasThis) list.Add(Action("ローカル変数として型を付ける (" + assign.Name + ")", () => Invoke(p => p.Run(false))));
                    if (CppScan.EnclosingClassRef(text, caret) != null) list.Add(Action("メンバー変数としてヘッダーに宣言する (" + assign.Name + ")", () => Invoke(p => p.Run(true))));
                }
            }
            catch (Exception ex) { KCppAssistPackage.Log("quickfix collect failed: " + ex.Message); }
            return list;
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
                string t;
                try { t = File.ReadAllText(f); } catch (Exception) { continue; }
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

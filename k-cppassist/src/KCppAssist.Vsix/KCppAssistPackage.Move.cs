using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using EnvDTE;
using Microsoft.VisualStudio.ComponentModelHost;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.Text.Operations;
using Microsoft.VisualStudio.TextManager.Interop;
using Task = System.Threading.Tasks.Task;

namespace KCppAssist
{
    /// <summary>関数の本体を、ヘッダー ⇄ cpp に移す(Alt+M)。計算は MoveGen、ここは VS とのつなぎ。</summary>
    public sealed partial class KCppAssistPackage
    {
        internal void RunMove()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunMoveAsync(); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        private async Task RunMoveAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<ITextUndoHistoryRegistry>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync("アクティブなエディターがありません", true); return; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null) { await ReportAsync("ファイルを開いていません", true); return; }

            string text = view.TextSnapshot.GetText();
            int caret = view.Caret.Position.BufferPosition.Position;
            var line = view.Caret.Position.BufferPosition.GetContainingLine();
            var sig = FunctionScan.Scan(text).FirstOrDefault(s => (caret >= s.NameStart && caret <= s.End + 1) || (s.Open >= line.Start.Position && s.Open <= line.End.Position));
            if (sig == null || !sig.HasBody) { await ReportAsync("カーソルの位置に、本体のある関数が見つかりません", true); return; }
            string label = (sig.Class == null ? "" : sig.Class + "::") + sig.Name;
            bool header = IncludeService.IsHeader(path);
            string eolHere = text.Contains("\r\n") ? "\r\n" : "\n";

            if (header)
            {
                // ---- ヘッダー → cpp ----
                var opt = SyncService.Options;
                string root = IncludeService.RootFor(path);
                List<string> files = await Task.Run(() => SyncService.Candidates(path, sig.Class, root, true, opt));
                await JoinableTaskFactory.SwitchToMainThreadAsync();
                var sources = files.Where(f => !IncludeService.IsHeader(f)).ToList();
                if (sources.Count == 0) { await ReportAsync(label + " を移す .cpp が見つかりません (" + Path.GetFileNameWithoutExtension(path) + ".cpp を作ってください)", true); return; }
                string cppFile = sources[0];
                if (sources.Count > 1)
                {
                    string pick = Choose(label + " の本体を移す .cpp を選んでください。", sources);
                    if (pick == null) { await ReportAsync("やめました", true); return; }
                    cppFile = pick;
                }
                ITextBuffer cppBuf = SyncService.OpenForEdit(cppFile, adapters);
                if (cppBuf == null) { await ReportAsync(Path.GetFileName(cppFile) + " を開けませんでした", true); return; }
                string cppText = cppBuf.CurrentSnapshot.GetText();
                string eol = cppText.Contains("\r\n") ? "\r\n" : cppText.Contains("\n") ? "\n" : eolHere;

                // すでに同じ定義が cpp にあれば、二重にしない
                var keys = SignatureSync.KeyVariants(sig.Inner(text));
                bool dup = FunctionScan.Scan(cppText).Any(s => s.HasBody && SyncPlan.Counterpart(s, sig, true) > 0 && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(s.Inner(cppText)), keys));
                if (dup) { await ReportAsync(label + " の定義は、すでに " + Path.GetFileName(cppFile) + " にあります", true); return; }

                string why;
                var plan = MoveGen.ToCpp(text, sig, cppText, eol, out why);
                if (plan == null) { await ReportAsync(label + ": " + why, true); return; }
                SyncService.ApplyEdits(cppBuf, plan.Target.Select(e => Tuple.Create(e.Position, e.Length, e.Text)).ToList(), undo, "K-CppAssist: 関数を cpp に移す");
                SyncService.ApplyEdits(view.TextBuffer, plan.Source.Select(e => Tuple.Create(e.Position, e.Length, e.Text)).ToList(), undo, "K-CppAssist: 関数を cpp に移す");
                await ReportAsync(label + " の本体を " + Path.GetFileName(cppFile) + " に移しました (必要な #include は足していません)", false);
                return;
            }

            // ---- cpp → ヘッダー ----
            if (sig.InClass || sig.Class == null) { await ReportAsync(label + ": Class::Func の形の定義ではありません", true); return; }
            {
                var opt = SyncService.Options;
                string root = IncludeService.RootFor(path);
                List<string> files = await Task.Run(() => SyncService.Candidates(path, sig.Class, root, false, opt));
                await JoinableTaskFactory.SwitchToMainThreadAsync();
                var keys = SignatureSync.KeyVariants(sig.Inner(text));
                var targets = SyncService.FindTargets(files, false, sig, adapters)
                    .Where(t => !t.Sig.HasBody && IncludeService.IsHeader(t.File) && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(t.Inner), keys)).ToList();
                if (targets.Count == 0) { await ReportAsync(label + " の宣言が、ヘッダーに見つかりません (先に Alt+R で宣言を作ってください)", true); return; }
                var t0 = targets[0];
                if (targets.Count > 1)
                {
                    var names = targets.ToDictionary(t => t.File + " (" + t.Sig.Open + ")", t => t);
                    string pick = Choose(label + " の宣言が複数あります。本体を移すヘッダーを選んでください。", names.Keys.ToList());
                    if (pick == null) { await ReportAsync("やめました", true); return; }
                    t0 = names[pick];
                }
                ITextBuffer hbuf = SyncService.OpenForEdit(t0.File, adapters);
                if (hbuf == null) { await ReportAsync(Path.GetFileName(t0.File) + " を開けませんでした", true); return; }
                string hText = hbuf.CurrentSnapshot.GetText();
                var decl = FunctionScan.Scan(hText).FirstOrDefault(s => !s.HasBody && s.Name == t0.Sig.Name && s.Open == t0.Sig.Open)
                    ?? FunctionScan.Scan(hText).FirstOrDefault(s => !s.HasBody && SyncPlan.Counterpart(s, sig, false) > 0 && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(s.Inner(hText)), keys));
                if (decl == null) { await ReportAsync(label + " の宣言を読み直せませんでした", true); return; }
                string eol = hText.Contains("\r\n") ? "\r\n" : hText.Contains("\n") ? "\n" : eolHere;

                string why;
                var plan = MoveGen.ToHeader(text, sig, hText, decl, eol, out why);
                if (plan == null) { await ReportAsync(label + ": " + why, true); return; }
                SyncService.ApplyEdits(hbuf, plan.Target.Select(e => Tuple.Create(e.Position, e.Length, e.Text)).ToList(), undo, "K-CppAssist: 関数をヘッダーに移す");
                SyncService.ApplyEdits(view.TextBuffer, plan.Source.Select(e => Tuple.Create(e.Position, e.Length, e.Text)).ToList(), undo, "K-CppAssist: 関数をヘッダーに移す");
                await ReportAsync(label + " の本体を " + Path.GetFileName(t0.File) + " に移しました (cpp の #include のうち、本体が使うものは、ヘッダーに足してください)", false);
            }
        }
    }
}

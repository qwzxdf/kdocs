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
                catch (Exception ex) { await ReportAsync(L.F("例外: {0}", ex.Message), true); Log(ex.ToString()); }
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
            if (view == null) { await ReportAsync(L.T("アクティブなエディターがありません"), true); return; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null) { await ReportAsync(L.T("ファイルを開いていません"), true); return; }

            // 候補を探す間と、選ぶ欄を出す間に、文字が変わることがある。位置は snap0 のもので計算して、適用するときに今の位置へ写す
            ITextSnapshot snap0 = view.TextSnapshot;
            string text = snap0.GetText();
            int caret = view.Caret.Position.BufferPosition.Position;
            var line = view.Caret.Position.BufferPosition.GetContainingLine();
            var sig = FunctionScan.Scan(text).FirstOrDefault(s => (caret >= s.NameStart && caret <= s.End + 1) || (s.Open >= line.Start.Position && s.Open <= line.End.Position));
            if (sig == null || !sig.HasBody) { await ReportAsync(L.T("カーソルの位置に、本体のある関数が見つかりません"), true); return; }
            string label = (sig.Class == null ? "" : sig.Class + "::") + sig.Name;
            bool header = IncludeService.IsHeader(path);
            string eolHere = CppText.Eol(text);

            if (header)
            {
                // ---- ヘッダー → cpp ----
                var opt = SyncService.Options;
                string root = IncludeService.RootFor(path);
                List<string> files = await Task.Run(() => SyncService.Candidates(path, sig.Class, root, true, opt));
                await JoinableTaskFactory.SwitchToMainThreadAsync();
                var sources = files.Where(f => !IncludeService.IsHeader(f)).ToList();
                if (sources.Count == 0) { await ReportAsync(L.F("{0} を移す .cpp が見つかりません ({1}.cpp を作ってください)", label, Path.GetFileNameWithoutExtension(path)), true); return; }
                string cppFile = sources[0];
                if (sources.Count > 1)
                {
                    string pick = Choose(label + " の本体を移す .cpp を選んでください。", sources);
                    if (pick == null) { await ReportAsync(L.T("やめました"), true); return; }
                    cppFile = pick;
                }
                ITextBuffer cppBuf = SyncService.OpenForEdit(cppFile, adapters);
                if (cppBuf == null) { await ReportAsync(L.F("{0} を開けませんでした", Path.GetFileName(cppFile)), true); return; }
                string cppText = cppBuf.CurrentSnapshot.GetText();
                string eol = CppText.Eol(cppText, eolHere);

                // すでに同じ定義が cpp にあれば、二重にしない
                var keys = SignatureSync.KeyVariants(sig.Inner(text));
                bool dup = FunctionScan.Scan(cppText).Any(s => s.HasBody && SyncPlan.Counterpart(s, sig, true) > 0 && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(s.Inner(cppText)), keys));
                if (dup) { await ReportAsync(L.F("{0} の定義は、すでに {1} にあります", label, Path.GetFileName(cppFile)), true); return; }

                string why;
                var plan = MoveGen.ToCpp(text, sig, cppText, eol, out why);
                if (plan == null) { await ReportAsync(label + ": " + why, true); return; }
                SyncService.ApplyEdits(cppBuf, plan.Target.Select(e => Tuple.Create(e.Position, e.Length, e.Text)).ToList(), undo, "K-Cpp: 関数を cpp に移す");
                SymbolService.ApplyEdits(snap0, plan.Source.Select(e => Tuple.Create(e.Position, e.Length, e.Text)).ToList(), undo, "K-Cpp: 関数を cpp に移す");
                await ReportAsync(L.F("{0} の本体を {1} に移しました (必要な #include は足していません)", label, Path.GetFileName(cppFile)), false);
                return;
            }

            // ---- cpp → ヘッダー ----
            if (sig.InClass || sig.Class == null) { await ReportAsync(L.F("{0}: Class::Func の形の定義ではありません", label), true); return; }
            {
                var opt = SyncService.Options;
                string root = IncludeService.RootFor(path);
                List<string> files = await Task.Run(() => SyncService.Candidates(path, sig.Class, root, false, opt));
                await JoinableTaskFactory.SwitchToMainThreadAsync();
                var keys = SignatureSync.KeyVariants(sig.Inner(text));
                var targets = SyncService.FindTargets(files, false, sig, adapters)
                    .Where(t => !t.Sig.HasBody && IncludeService.IsHeader(t.File) && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(t.Inner), keys)).ToList();
                if (targets.Count == 0) { await ReportAsync(L.F("{0} の宣言が、ヘッダーに見つかりません (先に Alt+R で宣言を作ってください)", label), true); return; }
                var t0 = targets[0];
                if (targets.Count > 1)
                {
                    var names = targets.ToDictionary(t => t.File + " (" + t.Sig.Open + ")", t => t);
                    string pick = Choose(label + " の宣言が複数あります。本体を移すヘッダーを選んでください。", names.Keys.ToList());
                    if (pick == null) { await ReportAsync(L.T("やめました"), true); return; }
                    t0 = names[pick];
                }
                ITextBuffer hbuf = SyncService.OpenForEdit(t0.File, adapters);
                if (hbuf == null) { await ReportAsync(L.F("{0} を開けませんでした", Path.GetFileName(t0.File)), true); return; }
                string hText = hbuf.CurrentSnapshot.GetText();
                var decl = FunctionScan.Scan(hText).FirstOrDefault(s => !s.HasBody && s.Name == t0.Sig.Name && s.Open == t0.Sig.Open)
                    ?? FunctionScan.Scan(hText).FirstOrDefault(s => !s.HasBody && SyncPlan.Counterpart(s, sig, false) > 0 && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(s.Inner(hText)), keys));
                if (decl == null) { await ReportAsync(L.F("{0} の宣言を読み直せませんでした", label), true); return; }
                string eol = CppText.Eol(hText, eolHere);

                string why;
                var plan = MoveGen.ToHeader(text, sig, hText, decl, eol, out why);
                if (plan == null) { await ReportAsync(label + ": " + why, true); return; }
                SyncService.ApplyEdits(hbuf, plan.Target.Select(e => Tuple.Create(e.Position, e.Length, e.Text)).ToList(), undo, "K-Cpp: 関数をヘッダーに移す");
                SymbolService.ApplyEdits(snap0, plan.Source.Select(e => Tuple.Create(e.Position, e.Length, e.Text)).ToList(), undo, "K-Cpp: 関数をヘッダーに移す");
                await ReportAsync(L.F("{0} の本体を {1} に移しました (cpp の #include のうち、本体が使うものは、ヘッダーに足してください)", label, Path.GetFileName(t0.File)), false);
            }
        }
    }
}

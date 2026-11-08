using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
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
    /// <summary>
    /// コードを作る機能: switch の足りない case を足す、コンストラクターを作る。
    /// 計算は SwitchGen と CtorGen。ここは、エディターとのつなぎ。
    /// </summary>
    public sealed partial class KCppAssistPackage
    {
        internal const int CmdSwitch = 0x0110;
        internal const int CmdCtor = 0x0111;

        private void RegisterGenCommands(OleMenuCommandService commands)
        {
            commands.AddCommand(new MenuCommand((s, e) => RunGen(true), new CommandID(CmdSet, CmdSwitch)));
            commands.AddCommand(new MenuCommand((s, e) => RunGen(false), new CommandID(CmdSet, CmdCtor)));
        }

        internal void RunSwitch() { RunGen(true); }
        internal void RunCtor() { RunGen(false); }

        private void RunGen(bool isSwitch)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunGenAsync(isSwitch); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        private async Task RunGenAsync(bool isSwitch)
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
            if (path == null) { await ReportAsync("ファイルが保存されていません", true); return; }

            string text = view.TextSnapshot.GetText();
            string eol = text.Contains("\r\n") ? "\r\n" : "\n";
            int caret = view.Caret.Position.BufferPosition.Position;
            string why;
            int pos;
            string ins, done;

            if (isSwitch)
            {
                // enum は、このファイルと、#include をたどった先(2 段まで)から探す
                var enums = SwitchGen.ParseEnums(text);
                string root = IncludeService.RootFor(path);
                var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { path };
                var queue = new List<Tuple<string, string, int>> { Tuple.Create(path, text, 0) };
                var extra = await Task.Run(() =>
                {
                    var found = new List<SwitchGen.EnumDef>();
                    for (int qi = 0; qi < queue.Count && qi < 60; qi++)
                    {
                        var cur = queue[qi];
                        if (cur.Item3 >= 2) continue;
                        foreach (var inc in IncludeTidy.Parse(cur.Item2).Where(i => !i.Angle))
                        {
                            string file = ProvidedCache.Resolve(inc, cur.Item1, root);
                            if (file == null || !seen.Add(file)) continue;
                            string t;
                            try { t = File.ReadAllText(file); } catch (Exception) { continue; }
                            found.AddRange(SwitchGen.ParseEnums(t));
                            queue.Add(Tuple.Create(file, t, cur.Item3 + 1));
                        }
                    }
                    return found;
                });
                await JoinableTaskFactory.SwitchToMainThreadAsync();
                enums.AddRange(extra);
                var plan = SwitchGen.Make(text, caret, enums, eol, out why);
                if (plan == null) { await ReportAsync(why, true); return; }
                pos = plan.Position;
                ins = plan.Text;
                done = plan.EnumName + " の case を " + plan.Added.Count + " 件足しました (" + string.Join(", ", plan.Added) + ")";
            }
            else
            {
                var plan = CtorGen.Make(text, caret, eol, out why);
                if (plan == null) { await ReportAsync(why, true); return; }
                pos = plan.Position;
                ins = plan.Text;
                done = plan.ClassName + " のコンストラクターを作りました (メンバー " + plan.Count + " 個)";
            }

            SyncService.ApplyEdits(view.TextBuffer, new List<Tuple<int, int, string>> { Tuple.Create(pos, 0, ins) }, undo,
                isSwitch ? "K-CppAssist: switch の case を足す" : "K-CppAssist: コンストラクターを作る");
            await ReportAsync(done, false);
        }
    }
}

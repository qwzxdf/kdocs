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
        internal const int CmdOverride = 0x0112;

        private void RegisterGenCommands(OleMenuCommandService commands)
        {
            commands.AddCommand(new MenuCommand((s, e) => RunGen(0), new CommandID(CmdSet, CmdSwitch)));
            commands.AddCommand(new MenuCommand((s, e) => RunGen(1), new CommandID(CmdSet, CmdCtor)));
            commands.AddCommand(new MenuCommand((s, e) => RunGen(2), new CommandID(CmdSet, CmdOverride)));
        }

        internal void RunSwitch() { RunGen(0); }
        internal void RunCtor() { RunGen(1); }
        internal void RunOverride() { RunGen(2); }

        private void RunGen(int kind)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunGenAsync(kind); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        private async Task RunGenAsync(int kind)
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

            if (kind == 0)
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
            else if (kind == 2)
            {
                // 基底クラスの定義は、このファイルと、#include をたどった先(2 段まで)、型の索引から探す
                var names = OverrideGen.BaseNamesAt(text, caret);
                if (names == null) { await ReportAsync("カーソルが、class / struct の中にありません", true); return; }
                string root = IncludeService.RootFor(path);
                var texts = await Task.Run(() =>
                {
                    var result = new List<string>();
                    var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { path };
                    var queue = new List<Tuple<string, string, int>> { Tuple.Create(path, text, 0) };
                    foreach (string b in names)
                        foreach (string f in IncludeService.Index.Lookup(b))
                        {
                            if (!seen.Add(f)) continue;
                            string t;
                            try { t = File.ReadAllText(f); } catch (Exception) { continue; }
                            result.Add(t);
                            queue.Add(Tuple.Create(f, t, 1));
                        }
                    for (int qi = 0; qi < queue.Count && qi < 80; qi++)
                    {
                        var cur = queue[qi];
                        if (cur.Item3 >= 3) continue;
                        foreach (var inc in IncludeTidy.Parse(cur.Item2).Where(i => !i.Angle))
                        {
                            string file = ProvidedCache.Resolve(inc, cur.Item1, root);
                            if (file == null || !seen.Add(file)) continue;
                            string t;
                            try { t = File.ReadAllText(file); } catch (Exception) { continue; }
                            result.Add(t);
                            queue.Add(Tuple.Create(file, t, cur.Item3 + 1));
                        }
                    }
                    return result;
                });
                await JoinableTaskFactory.SwitchToMainThreadAsync();
                var plan = OverrideGen.Make(text, caret, texts, eol, out why);
                if (plan == null) { await ReportAsync(why, true); return; }
                pos = plan.Position;
                ins = plan.Text;
                done = plan.ClassName + " に override を " + plan.Added.Count + " 件足しました (" + string.Join(", ", plan.Added) + ")"
                    + (plan.PureOnly ? "。純粋仮想関数だけです。残りの仮想関数は、もう一度押すと足します" : "");
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
                kind == 0 ? "K-CppAssist: switch の case を足す" : kind == 2 ? "K-CppAssist: override を足す" : "K-CppAssist: コンストラクターを作る");
            await ReportAsync(done, false);
        }
    }
}

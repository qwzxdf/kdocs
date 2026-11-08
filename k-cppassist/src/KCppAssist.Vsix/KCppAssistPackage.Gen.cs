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
            commands.AddCommand(new MenuCommand((s, e) => RunUsage(), new CommandID(CmdSet, CmdUsage)));
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

        // ---- 使用箇所から関数を作る ----

        internal const int CmdUsage = 0x0113;

        /// <summary>クラスの本体に、メンバーの宣言 1 つを足す編集(位置と文字)。自分のクラスなら末尾、ほかのクラスなら public。</summary>
        private static Tuple<int, string> PlanMember(string text, int open, bool isStruct, bool own, string declaration, string eol)
        {
            if (own)
            {
                var e = HeaderEditor.PlanAt(text, open, declaration, eol);
                return e == null ? null : Tuple.Create(e.Position, e.Text);
            }
            var d = DefinitionGen.PlanPublicMember(text, open, isStruct, declaration, eol);
            return d == null ? null : Tuple.Create(d.Position, d.Text);
        }

        internal void RunUsage()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunUsageAsync(); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        /// <summary>
        /// 呼び出し(Foo(a, 1) / obj.Foo(x))の行で押すと、その関数を作る。メンバーなら、クラスの宣言と cpp の定義の雛形。
        /// クラスの外なら、いまの関数の前に自由関数の定義(中身は TODO)。
        /// </summary>
        private async Task RunUsageAsync()
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
            var u = UsageGen.Find(text, caret, out why);
            if (u == null) { await ReportAsync(why, true); return; }

            string note = (u.Unknown.Count > 0 ? "。型を決められなかった引数は int にしました (" + string.Join(", ", u.Unknown) + ")" : "")
                + (u.ReturnGuessed ? "。戻り値の型は int にしました" : "");

            // 足し先のクラス: obj.Foo は obj の型、Foo / this->Foo は、いまのメンバー関数のクラス
            ClassRef cref;
            bool own;
            if (u.Receiver != null && u.Receiver != "this")
            {
                if (u.ReceiverType == null) { await ReportAsync(u.Receiver.TrimEnd('.', '-', '>') + " の型を決められません。宣言が見える場所で試してください", true); return; }
                cref = new ClassRef { Name = u.ReceiverType };
                own = false;
            }
            else
            {
                cref = CppScan.EnclosingClassRef(text, caret);
                own = true;
            }

            if (cref == null)
            {
                // クラスの外: いまの関数の前に自由関数を作る
                if (IncludeService.IsHeader(path)) { await ReportAsync("ヘッダーの自由関数は作りません。メンバー関数の中か、cpp で押してください", true); return; }
                var encl = FunctionScan.Scan(text).Where(s => s.HasBody && s.BodyOpen >= 0 && s.BodyOpen < caret && caret < s.End).OrderByDescending(s => s.BodyOpen).FirstOrDefault();
                if (encl == null) { await ReportAsync("関数の中で押してください", true); return; }
                int pos0; string def0;
                UsageGen.PlanFreeDefinition(text, encl.PrefixStart, u, eol, out pos0, out def0);
                SyncService.ApplyEdits(view.TextBuffer, new List<Tuple<int, int, string>> { Tuple.Create(pos0, 0, def0) }, undo, "K-CppAssist: 関数を作る");
                await ReportAsync(u.Signature() + " を作りました (いまの関数の前)" + note, false);
                return;
            }

            var loc = await LocateClassAsync(dte, path, view, cref);
            if (loc == null) return;

            // すでに同じ名前の関数があれば、作らない
            var existing = FunctionScan.Scan(loc.Text).FirstOrDefault(s => s.Name == u.Name && s.Open > loc.Scope.Open && s.Close < loc.Scope.Close);
            if (existing != null) { await ReportAsync(cref.Name + "::" + u.Name + " は " + Path.GetFileName(loc.File) + " にすでにあります", true); return; }

            string hEol = loc.Text.Contains("\r\n") ? "\r\n" : "\n";
            string root = IncludeService.RootFor(loc.File);
            var opt = SyncService.Options;
            var cpps = await Task.Run(() => SyncService.Candidates(loc.File, cref.Name, root, true, opt).Where(f => !IncludeService.IsHeader(f)).ToList());
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            string cppFile = !IncludeService.IsHeader(path) && own ? path : (cpps.Count > 0 ? cpps[0] : null);

            if (cppFile == null)
            {
                // cpp がない(ヘッダーだけのクラス): 宣言と一緒に、中身が空の本体を書く
                string inline = u.Signature() + (u.ReturnType == "void" ? " {}" : " { return {}; }");
                var ed0 = PlanMember(loc.Text, loc.Scope.Open, loc.Scope.IsStruct, own, inline, hEol);
                if (ed0 == null) { await ReportAsync(Path.GetFileName(loc.File) + " の中でクラス " + cref.Name + " の本体を読めませんでした", true); return; }
                SyncService.Insert(loc.View.TextBuffer, ed0.Item1, ed0.Item2, undo, "K-CppAssist: 関数を作る");
                ReturnTo(path, loc.File);
                await ReportAsync(cref.Name + "::" + u.Name + " を " + Path.GetFileName(loc.File) + " に作りました (cpp がないので、本体つき)" + note, false);
                return;
            }

            // 宣言をクラスに足す(自分のクラスなら末尾、ほかのクラスなら public)
            var ed = PlanMember(loc.Text, loc.Scope.Open, loc.Scope.IsStruct, own, u.Declaration(), hEol);
            if (ed == null) { await ReportAsync(Path.GetFileName(loc.File) + " の中でクラス " + cref.Name + " の本体を読めませんでした", true); return; }
            SyncService.Insert(loc.View.TextBuffer, ed.Item1, ed.Item2, undo, "K-CppAssist: 宣言を作る");

            // cpp に定義の雛形(足した宣言を、足したあとのヘッダーから読み直す)
            string newHeader = loc.View.TextSnapshot.GetText();
            var scope2 = Scopes.Parse(newHeader).Where(s => s.IsClass && s.Name == cref.Name).OrderBy(s => Math.Abs(s.Open - loc.Scope.Open)).FirstOrDefault();
            var sig = scope2 == null ? null : FunctionScan.Scan(newHeader).FirstOrDefault(s => !s.HasBody && s.Name == u.Name && s.Open > scope2.Open && s.Close < scope2.Close);
            string defMsg;
            if (sig == null) defMsg = "。定義の雛形は作れませんでした (足した宣言を読めません)";
            else
            {
                ITextBuffer buf = string.Equals(cppFile, path, StringComparison.OrdinalIgnoreCase) ? view.TextBuffer : SyncService.OpenForEdit(cppFile, adapters);
                if (buf == null) defMsg = "。" + Path.GetFileName(cppFile) + " を開けませんでした";
                else
                {
                    string cppText = buf.CurrentSnapshot.GetText();
                    string cEol = cppText.Contains("\r\n") ? "\r\n" : cppText.Contains("\n") ? "\n" : hEol;
                    string why2;
                    var def = DefinitionGen.PlanDefinition(newHeader, sig, cppText, cEol, out why2);
                    if (def == null) defMsg = "。定義の雛形は作れませんでした (" + why2 + ")";
                    else
                    {
                        SyncService.Insert(buf, def.Position, def.Text, undo, "K-CppAssist: 定義を作る");
                        defMsg = "。定義を " + Path.GetFileName(cppFile) + " に足しました";
                    }
                }
            }
            ReturnTo(path, loc.File);
            await ReportAsync(cref.Name + "::" + u.Name + " の宣言を " + Path.GetFileName(loc.File) + " に作りました" + defMsg + note, false);
        }
    }
}

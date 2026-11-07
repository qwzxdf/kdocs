using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.IO;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Windows;
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
    /// #include の整理(プロジェクト全体・いまのファイル)、使っていない #include の削除、#include を前方宣言にする。
    /// 計算は IncludeTidy と ForwardDecl。ここは、ファイルの集め方と読み書き(VS とのつなぎ)。
    /// </summary>
    public sealed partial class KCppAssistPackage
    {
        internal const int CmdTidyProject = 0x010A;
        internal const int CmdUnusedProject = 0x010B;
        internal const int CmdForward = 0x010C;
        internal const int CmdTidyFile = 0x010D;

        private static readonly string[] CodeExt = { ".h", ".hpp", ".hh", ".hxx", ".cpp", ".cc", ".cxx", ".c++" };

        private void RegisterTidyCommands(OleMenuCommandService commands)
        {
            commands.AddCommand(new MenuCommand((s, e) => RunTidy(false, false), new CommandID(CmdSet, CmdTidyProject)));
            commands.AddCommand(new MenuCommand((s, e) => RunTidy(true, false), new CommandID(CmdSet, CmdUnusedProject)));
            commands.AddCommand(new MenuCommand((s, e) => RunForward(), new CommandID(CmdSet, CmdForward)));
            commands.AddCommand(new MenuCommand((s, e) => RunTidy(false, true), new CommandID(CmdSet, CmdTidyFile)));
        }

        // ---- ファイルの読み書き(エンコードと BOM を保つ) ----

        private sealed class SourceFile
        {
            public string Path;
            public string Text;
            public Encoding Encoding;
            public bool Bom;
            public ITextBuffer Buffer;      // エディターで開いているときは、こちらを書き換える
        }

        private static SourceFile ReadSource(string path, Microsoft.VisualStudio.Editor.IVsEditorAdaptersFactoryService adapters)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var buf = SyncService.OpenBuffer(path, adapters);
            if (buf != null) return new SourceFile { Path = path, Text = buf.CurrentSnapshot.GetText(), Buffer = buf };
            byte[] bytes;
            try { bytes = File.ReadAllBytes(path); } catch (Exception) { return null; }
            var f = new SourceFile { Path = path };
            int skip = 0;
            if (bytes.Length >= 3 && bytes[0] == 0xEF && bytes[1] == 0xBB && bytes[2] == 0xBF) { f.Encoding = new UTF8Encoding(true); f.Bom = true; skip = 3; }
            else if (bytes.Length >= 2 && bytes[0] == 0xFF && bytes[1] == 0xFE) { f.Encoding = new UnicodeEncoding(false, true); f.Bom = true; skip = 2; }
            else if (bytes.Length >= 2 && bytes[0] == 0xFE && bytes[1] == 0xFF) { f.Encoding = new UnicodeEncoding(true, true); f.Bom = true; skip = 2; }
            else
            {
                try { new UTF8Encoding(false, true).GetString(bytes); f.Encoding = new UTF8Encoding(false); }
                catch (Exception)
                {
                    try { f.Encoding = Encoding.GetEncoding(932); } catch (Exception) { return null; }
                }
            }
            try { f.Text = f.Encoding.GetString(bytes, skip, bytes.Length - skip); } catch (Exception) { return null; }
            return f;
        }

        private static bool WriteSource(SourceFile f, string newText, ITextUndoHistoryRegistry undo, string description)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (f.Buffer != null)
            {
                SyncService.ApplyEdits(f.Buffer, SyncService.Diff(f.Buffer.CurrentSnapshot.GetText(), newText), undo, description);
                return true;
            }
            try
            {
                byte[] body = f.Encoding.GetBytes(newText);
                byte[] pre = f.Bom ? f.Encoding.GetPreamble() : new byte[0];
                File.WriteAllBytes(f.Path, pre.Concat(body).ToArray());
                return true;
            }
            catch (Exception ex) { Log("write failed: " + f.Path + " " + ex.Message); return false; }
        }

        // ---- 対象のファイルを集める ----

        private static IEnumerable<string> ProjectFiles(DTE dte, bool wholeSolution)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var projects = new List<Project>();
            if (!wholeSolution)
            {
                try
                {
                    foreach (SelectedItem si in dte.SelectedItems)
                    {
                        if (si.Project != null) projects.Add(si.Project);
                        else if (si.ProjectItem != null && si.ProjectItem.ContainingProject != null) projects.Add(si.ProjectItem.ContainingProject);
                    }
                }
                catch (Exception) { }
            }
            if (projects.Count == 0 && dte.Solution != null) foreach (Project p in dte.Solution.Projects) projects.Add(p);

            var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
            foreach (var p in projects) foreach (string f in Walk(p, seen)) yield return f;
        }

        private static IEnumerable<string> Walk(Project p, HashSet<string> seen)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            ProjectItems items = null;
            try { items = p.ProjectItems; } catch (Exception) { }
            if (items == null) yield break;
            // ソリューション フォルダーの中のプロジェクトも辿る
            foreach (string f in Walk(items, seen)) yield return f;
        }

        private static IEnumerable<string> Walk(ProjectItems items, HashSet<string> seen)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (items == null) yield break;
            foreach (ProjectItem it in items)
            {
                string file = null;
                try { if (it.FileCount > 0) file = it.FileNames[1]; } catch (Exception) { }
                if (!string.IsNullOrEmpty(file) && File.Exists(file) && CodeExt.Contains(Path.GetExtension(file).ToLowerInvariant()) && seen.Add(file)) yield return file;
                ProjectItems sub = null;
                try { sub = it.ProjectItems; } catch (Exception) { }
                if (sub != null) foreach (string f in Walk(sub, seen)) yield return f;
                Project subProject = null;
                try { subProject = it.SubProject; } catch (Exception) { }
                if (subProject != null) foreach (string f in Walk(subProject, seen)) yield return f;
            }
        }

        // ---- include の整理・使っていない include ----

        internal void RunTidy(bool unused, bool currentFileOnly)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunTidyAsync(unused, currentFileOnly); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        private async Task RunTidyAsync(bool unused, bool currentFileOnly)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<ITextUndoHistoryRegistry>();
            var dte = (DTE)await GetServiceAsync(typeof(DTE));
            var opt = SyncService.Options;

            List<string> files;
            if (currentFileOnly)
            {
                string cur = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
                if (cur == null || !CodeExt.Contains(Path.GetExtension(cur).ToLowerInvariant())) { await ReportAsync("C++ のファイルを開いてから実行してください", true); return; }
                files = new List<string> { cur };
            }
            else files = ProjectFiles(dte, false).ToList();
            if (files.Count == 0) { await ReportAsync("対象のファイルが見つかりません (プロジェクトを右クリックして実行してください)", true); return; }

            bool headersToo = opt != null && opt.RemoveUnusedInHeaders;
            var provider = new ProvidedCache(opt);
            var changes = new List<Tuple<SourceFile, string, string>>();   // (ファイル, 新しい文字, 説明)
            int skipped = 0;
            var details = new List<string>();
            foreach (string path in files)
            {
                var src = ReadSource(path, adapters);
                if (src == null) { skipped++; Log("tidy: skipped (read/encoding) " + path); continue; }
                string eol = src.Text.Contains("\r\n") ? "\r\n" : "\n";
                bool header = IncludeService.IsHeader(path);
                string stem = header ? null : Path.GetFileNameWithoutExtension(path);
                string text = src.Text;
                string root = IncludeService.RootFor(path);

                if (unused)
                {
                    if (header && !headersToo) continue;
                    var list = IncludeTidy.Unused(text, stem, it => provider.For(it, path, root));
                    if (list.Count == 0) continue;
                    text = IncludeTidy.Remove(text, list);
                    foreach (var it in list) details.Add(Path.GetFileName(path) + ": " + it.Token);
                }
                else
                {
                    string organized = IncludeTidy.Organize(text, stem, eol);
                    if (organized == null) continue;
                    text = organized;
                }
                if (text != src.Text) changes.Add(Tuple.Create(src, text, Path.GetFileName(path)));
            }

            if (changes.Count == 0)
            {
                await ReportAsync((unused ? "使っていない #include は、見つかりませんでした" : "#include は、すでに整っています") + " (" + files.Count + " ファイル" + (skipped > 0 ? "、読めなかったもの " + skipped : "") + ")", false);
                return;
            }

            if (unused)
            {
                string preview = string.Join("\n", details.Take(25)) + (details.Count > 25 ? "\n… ほか " + (details.Count - 25) + " 件" : "");
                var answer = System.Windows.MessageBox.Show("次の " + details.Count + " 件の #include を消します。\n名前の使われ方から調べているので、マクロや、他のヘッダー経由の使い方は見ていません。消したあと、ビルドして確かめてください。\n\n" + preview + "\n\n消しますか?",
                    "K-CppAssist: 使っていない #include", MessageBoxButton.YesNo, MessageBoxImage.Question);
                if (answer != MessageBoxResult.Yes) { await ReportAsync("やめました", false); return; }
            }

            int written = 0;
            foreach (var c in changes)
                if (WriteSource(c.Item1, c.Item2, undo, unused ? "K-CppAssist: 使っていない #include を消す" : "K-CppAssist: #include を整理")) written++;
            Log("tidy: " + (unused ? "unused" : "organize") + " files=" + files.Count + " changed=" + written + " skipped=" + skipped);
            await ReportAsync((unused ? "使っていない #include を " + details.Count + " 件消しました" : "#include を整理しました") + " (" + written + " / " + files.Count + " ファイル" + (skipped > 0 ? "、読めなかったもの " + skipped : "") + ")。エディターで開いていないファイルは、保存済みです", false);
        }

        /// <summary>#include 先のヘッダーが(間接に include するものも含めて)定義している名前。結果は、1 回の実行の間だけ覚える。</summary>
        private sealed class ProvidedCache
        {
            private readonly OptionsPage opt;
            private readonly Dictionary<string, HashSet<string>> direct = new Dictionary<string, HashSet<string>>(StringComparer.OrdinalIgnoreCase);

            public ProvidedCache(OptionsPage opt) { this.opt = opt; }

            public static string Resolve(IncludeTidy.Item it, string curPath, string root)
            {
                string rel = it.Path.Replace('/', Path.DirectorySeparatorChar);
                var dirs = new List<string>();
                if (!it.Angle) dirs.Add(Path.GetDirectoryName(curPath));
                if (!string.IsNullOrEmpty(root)) dirs.Add(root);
                dirs.AddRange(IncludeService.Index.IncludeRoots());
                foreach (string d in dirs)
                {
                    try { string full = Path.GetFullPath(Path.Combine(d, rel)); if (File.Exists(full)) return full; } catch (Exception) { }
                }
                return null;
            }

            public ISet<string> For(IncludeTidy.Item it, string curPath, string root)
            {
                string file = Resolve(it, curPath, root);
                if (file == null)
                {
                    return it.Angle ? StdHeaders.NamesFor(it.Token.ToLowerInvariant()) : null;     // 読めない相手は、残す
                }
                var set = new HashSet<string>(StringComparer.Ordinal);
                Collect(file, root, set, new HashSet<string>(StringComparer.OrdinalIgnoreCase), 0);
                return set;
            }

            private void Collect(string file, string root, HashSet<string> into, HashSet<string> visited, int depth)
            {
                if (depth > 6 || !visited.Add(file)) return;
                HashSet<string> own;
                if (!direct.TryGetValue(file, out own))
                {
                    string text = null;
                    try { text = File.ReadAllText(file); } catch (Exception) { }
                    own = text == null ? new HashSet<string>() : IncludeTidy.Provided(text);
                    direct[file] = own;
                }
                into.UnionWith(own);
                string content = null;
                try { content = File.ReadAllText(file); } catch (Exception) { }
                if (content == null) return;
                foreach (var inc in IncludeTidy.Parse(content))
                {
                    string next = Resolve(inc, file, root);
                    if (next != null) { Collect(next, root, into, visited, depth + 1); continue; }
                    var std = inc.Angle ? StdHeaders.NamesFor(inc.Token.ToLowerInvariant()) : null;
                    if (std != null) into.UnionWith(std);
                }
            }
        }

        // ---- #include を前方宣言にする ----

        internal void RunForward()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunForwardAsync(); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        private async Task RunForwardAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<ITextUndoHistoryRegistry>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));
            var opt = SyncService.Options;

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync("アクティブなエディターがありません", true); return; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null || !IncludeService.IsHeader(path)) { await ReportAsync("前方宣言にするのは、ヘッダーで押してください", true); return; }

            string text = view.TextSnapshot.GetText();
            string eol = text.Contains("\r\n") ? "\r\n" : "\n";
            int caret = view.Caret.Position.BufferPosition.Position;
            var includes = IncludeTidy.Parse(text).Where(i => i.Depth == 0 && !i.Angle).ToList();
            if (includes.Count == 0) { await ReportAsync("このヘッダーに、\"...\" の #include がありません", true); return; }
            var onLine = includes.FirstOrDefault(i => caret >= i.Start && caret < i.End);
            var targets = onLine != null ? new List<IncludeTidy.Item> { onLine } : includes;

            string root = IncludeService.RootFor(path);
            var cache = new ProvidedCache(opt);
            var cppTokens = new List<string>();
            var done = new List<string>();
            var why = new List<string>();
            string current = text;
            foreach (var inc0 in targets)
            {
                // 前の置き換えで位置が動くので、毎回、文字から探し直す
                var inc = IncludeTidy.Parse(current).FirstOrDefault(i => i.Depth == 0 && !i.Angle && i.Path == inc0.Path);
                if (inc == null) continue;
                string file = ProvidedCache.Resolve(inc, path, root);
                if (file == null) { why.Add(inc.Path + ": ファイルを探せません"); continue; }
                string incText;
                try { incText = File.ReadAllText(file); } catch (Exception) { why.Add(inc.Path + ": 読めません"); continue; }
                var types = ForwardDecl.Types(incText);
                if (types.Count == 0) { why.Add(inc.Path + ": 前方宣言できる class / struct がありません"); continue; }
                var transitive = new HashSet<string>(StringComparer.Ordinal);
                var provided = cache.For(inc, path, root);
                if (provided != null) transitive.UnionWith(provided);
                string reason;
                var r = ForwardDecl.Make(current, inc, types, transitive, eol, out reason);
                if (r == null) { why.Add(inc.Path + ": " + reason); continue; }
                current = r.NewText;
                cppTokens.Add(r.CppToken);
                done.Add(inc.Path + " → " + string.Join(", ", r.Names));
            }

            if (done.Count == 0)
            {
                await ReportAsync("前方宣言にできる #include がありません。" + (why.Count > 0 ? why[0] : ""), true);
                Log("forward: " + string.Join(" / ", why));
                return;
            }

            // cpp 側に #include を足す(すでにあれば足さない)
            string stem = Path.GetFileNameWithoutExtension(path);
            var cpps = await Task.Run(() => SyncService.Candidates(path, null, root, true, opt).Where(f => !IncludeService.IsHeader(f)).ToList());
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var addedTo = new List<string>();
            foreach (string cpp in cpps)
            {
                ITextBuffer buf = SyncService.OpenForEdit(cpp, adapters);
                if (buf == null) continue;
                string cppText = buf.CurrentSnapshot.GetText();
                string cppEol = cppText.Contains("\r\n") ? "\r\n" : cppText.Contains("\n") ? "\n" : eol;
                var edits = new List<Tuple<int, int, string>>();
                string work = cppText;
                foreach (string token in cppTokens)
                {
                    var e = IncludeEditor.Plan(work, token, Path.GetFileNameWithoutExtension(cpp), cppEol);
                    if (e == null) continue;
                    edits.Add(Tuple.Create(e.Position, 0, e.Text));
                    work = work.Substring(0, e.Position) + e.Text + work.Substring(e.Position);
                }
                if (edits.Count == 0) continue;
                // Plan は、足すたびの文字列に対する位置なので、まとめて 1 回で置き換える
                SyncService.ApplyEdits(buf, SyncService.Diff(cppText, work), undo, "K-CppAssist: #include を cpp に移す");
                addedTo.Add(Path.GetFileName(cpp));
            }
            SyncService.ApplyEdits(view.TextBuffer, SyncService.Diff(text, current), undo, "K-CppAssist: #include を前方宣言にする");
            Log("forward: " + string.Join(" / ", done));
            await ReportAsync(string.Join("、", done) + " を前方宣言にしました" + (addedTo.Count > 0 ? "。#include は " + string.Join("・", addedTo) + " に足しました" : "。cpp が見つからないので、#include は移していません"), false);
        }
    }
}

using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using EnvDTE;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist
{
    /// <summary>
    /// 拡張機能 メニューの「ファイルの文字コードをそろえる...」。プロジェクト(かソリューション)のファイルを、1 つの文字コードと改行にそろえる。
    /// 判定と変換は EncodingTool。ここは、画面と、ファイルの集め方・書き方。
    /// </summary>
    public sealed partial class KCppAssistPackage
    {
        internal const int CmdEncoding = 0x0114;

        private const string DefaultEncodingExts = ".h;.hpp;.hh;.hxx;.inl;.ipp;.c;.cpp;.cc;.cxx;.ixx;.hlsl;.hlsli;.fx";

        private void RegisterEncodingCommand(OleMenuCommandService commands)
        {
            commands.AddCommand(new MenuCommand((s, e) => ShowEncodingWindow(), new CommandID(CmdSet, CmdEncoding)));
        }

        private sealed class EncRow
        {
            public string File { get; set; }
            public string Shown { get; set; }
            public string Current { get; set; }
            public string Eol { get; set; }
            public string Action { get; set; }
            public EncodingTool.Plan Plan;
            public bool Dirty;
        }

        private void ShowEncodingWindow()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try { new EncodingWindow(this).ShowDialog(); }
            catch (Exception ex) { Log("encoding window failed: " + ex); }
        }

        /// <summary>画面。中身はコードで組み立てる(XAML は使わない)。</summary>
        private sealed class EncodingWindow : System.Windows.Window
        {
            private readonly KCppAssistPackage pkg;
            private readonly DTE dte;
            private readonly RadioButton scopeProject = new RadioButton { Content = "選択中のプロジェクト", IsChecked = true, Margin = new Thickness(0, 0, 12, 0) };
            private readonly RadioButton scopeSolution = new RadioButton { Content = "ソリューションのすべてのプロジェクト", Margin = new Thickness(0, 0, 12, 0) };
            private readonly RadioButton scopeFolder = new RadioButton { Content = "ソリューションのフォルダー全体 (プロジェクトに入っていないファイルも)" };
            private readonly ComboBox target = new ComboBox { Width = 330 };
            private readonly ComboBox eol = new ComboBox { Width = 330 };
            private readonly TextBox exts = new TextBox { Text = DefaultEncodingExts, Width = 420 };
            private readonly CheckBox editorConfig = new CheckBox { Content = ".editorconfig に書く (これから新しく保存するファイルも、この文字コードと改行になります)", IsChecked = true };
            private readonly CheckBox saveFirst = new CheckBox { Content = "開いている未保存のファイルを、先に全部保存する", IsChecked = true };
            private readonly CheckBox sourceCharset = new CheckBox { Content = "BOM なし UTF-8 のとき、プロジェクトに /source-charset:utf-8 を付ける (MSVC が Shift-JIS として読まないように)", IsChecked = true };
            private readonly CheckBox onlyChanges = new CheckBox { Content = "変換が要るファイルだけ一覧に出す", IsChecked = true };
            private readonly ListView list = new ListView { Height = 300 };
            private readonly TextBlock summary = new TextBlock { TextWrapping = TextWrapping.Wrap, Margin = new Thickness(0, 6, 0, 6) };
            private readonly Button scanButton = new Button { Content = "調べる", Padding = new Thickness(14, 3, 14, 3), Margin = new Thickness(0, 0, 8, 0) };
            private readonly Button convertButton = new Button { Content = "変換する", Padding = new Thickness(14, 3, 14, 3), Margin = new Thickness(0, 0, 8, 0), IsEnabled = false };
            private readonly Button copyButton = new Button { Content = "一覧をコピー", Padding = new Thickness(10, 3, 10, 3), Margin = new Thickness(0, 0, 8, 0), IsEnabled = false };
            private readonly Button closeButton = new Button { Content = "閉じる", Padding = new Thickness(14, 3, 14, 3), IsCancel = true };
            private List<EncRow> rows = new List<EncRow>();
            private List<Project> scannedProjects = new List<Project>();
            private string root;

            public EncodingWindow(KCppAssistPackage pkg)
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                this.pkg = pkg;
                dte = (DTE)Package.GetGlobalService(typeof(DTE));
                Title = "K-CppAssist: ファイルの文字コードをそろえる";
                Width = 900;
                SizeToContent = SizeToContent.Height;
                WindowStartupLocation = WindowStartupLocation.CenterScreen;
                ResizeMode = ResizeMode.CanResizeWithGrip;

                target.Items.Add("UTF-8 (BOM 付き) … Visual Studio と MSVC がそのまま読めます (おすすめ)");
                target.Items.Add("UTF-8 (BOM なし) … Git や他のエディターと相性がよい。MSVC には /source-charset:utf-8 が要ります");
                target.Items.Add("Shift-JIS (CP932) … 古いプロジェクトに合わせるとき");
                target.SelectedIndex = 0;
                eol.Items.Add("改行はそのまま");
                eol.Items.Add("CRLF にそろえる (Windows の標準)");
                eol.Items.Add("LF にそろえる");
                eol.SelectedIndex = 0;

                var view = new GridView();
                view.Columns.Add(new GridViewColumn { Header = "ファイル", Width = 330, DisplayMemberBinding = new System.Windows.Data.Binding("Shown") });
                view.Columns.Add(new GridViewColumn { Header = "いまの文字コード", Width = 130, DisplayMemberBinding = new System.Windows.Data.Binding("Current") });
                view.Columns.Add(new GridViewColumn { Header = "改行", Width = 50, DisplayMemberBinding = new System.Windows.Data.Binding("Eol") });
                view.Columns.Add(new GridViewColumn { Header = "すること", Width = 340, DisplayMemberBinding = new System.Windows.Data.Binding("Action") });
                list.View = view;
                list.MouseDoubleClick += (s, e) =>
                {
                    var r = list.SelectedItem as EncRow;
                    if (r == null) return;
                    try { dte.ItemOperations.OpenFile(r.File); } catch (Exception) { }
                };

                var panel = new StackPanel { Margin = new Thickness(12) };
                panel.Children.Add(Label("対象"));
                var scope = new WrapPanel { Margin = new Thickness(0, 0, 0, 8) };
                scope.Children.Add(scopeProject);
                scope.Children.Add(scopeSolution);
                scope.Children.Add(scopeFolder);
                panel.Children.Add(scope);
                panel.Children.Add(Row("拡張子", exts));
                panel.Children.Add(Row("文字コード", target));
                panel.Children.Add(Row("改行", eol));
                foreach (var c in new[] { editorConfig, saveFirst, sourceCharset, onlyChanges }) { c.Margin = new Thickness(0, 2, 0, 2); panel.Children.Add(c); }
                var buttons = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 8, 0, 6) };
                buttons.Children.Add(scanButton);
                buttons.Children.Add(convertButton);
                buttons.Children.Add(copyButton);
                buttons.Children.Add(closeButton);
                panel.Children.Add(buttons);
                panel.Children.Add(summary);
                panel.Children.Add(list);
                panel.Children.Add(new TextBlock
                {
                    Text = "開いているファイルは、変換したあと Visual Studio が読み直します (「再読み込みしますか」と聞かれたら、はいを押します)。行をダブルクリックすると、そのファイルを開きます。",
                    TextWrapping = TextWrapping.Wrap,
                    Margin = new Thickness(0, 6, 0, 0),
                    Opacity = 0.75,
                });
                Content = new ScrollViewer { Content = panel, VerticalScrollBarVisibility = ScrollBarVisibility.Auto };

                // async void のラムダは、例外が VS ごと落とすので、JoinableTaskFactory で走らせて、例外は記録に残す
                scanButton.Click += (s, e) => RunGuarded(ScanAsync);
                convertButton.Click += (s, e) => RunGuarded(ConvertAsync);
                copyButton.Click += (s, e) => CopyList();
                closeButton.Click += (s, e) => Close();
                onlyChanges.Click += (s, e) => ShowRows();
                target.SelectionChanged += (s, e) => { convertButton.IsEnabled = false; summary.Text = "設定を変えたので、もう一度「調べる」を押してください。"; };
                eol.SelectionChanged += (s, e) => { convertButton.IsEnabled = false; summary.Text = "設定を変えたので、もう一度「調べる」を押してください。"; };
                summary.Text = "対象と文字コードを選んで「調べる」を押すと、いまの文字コードと、変換するファイルの一覧が出ます。まだ何も書き換えません。";
            }

            private static TextBlock Label(string s) { return new TextBlock { Text = s, FontWeight = FontWeights.SemiBold, Margin = new Thickness(0, 0, 0, 2) }; }

            private static UIElement Row(string label, UIElement control)
            {
                var p = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 2, 0, 2) };
                p.Children.Add(new TextBlock { Text = label, Width = 80, VerticalAlignment = VerticalAlignment.Center, FontWeight = FontWeights.SemiBold });
                p.Children.Add(control);
                return p;
            }

            private EncodingTool.Target Target() { return target.SelectedIndex == 1 ? EncodingTool.Target.Utf8 : target.SelectedIndex == 2 ? EncodingTool.Target.ShiftJis : EncodingTool.Target.Utf8Bom; }

            private EncodingTool.Eol Eol() { return eol.SelectedIndex == 1 ? EncodingTool.Eol.Crlf : eol.SelectedIndex == 2 ? EncodingTool.Eol.Lf : EncodingTool.Eol.Keep; }

            private HashSet<string> Exts()
            {
                return new HashSet<string>(exts.Text.Split(new[] { ';', ',', ' ' }, StringSplitOptions.RemoveEmptyEntries)
                    .Select(x => (x.StartsWith(".") ? x : "." + x.TrimStart('*')).ToLowerInvariant()), StringComparer.OrdinalIgnoreCase);
            }

            // ---- 調べる ----

            private static void RunGuarded(Func<Task> work)
            {
                _ = ThreadHelper.JoinableTaskFactory.RunAsync(async () =>
                {
                    try { await work(); }
                    catch (Exception ex) { Log("encoding window failed: " + ex); }
                });
            }

            private async Task ScanAsync()
            {
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                try
                {
                    scanButton.IsEnabled = convertButton.IsEnabled = copyButton.IsEnabled = false;
                    summary.Text = "調べています…";
                    if (saveFirst.IsChecked == true) { try { dte.ExecuteCommand("File.SaveAll"); } catch (Exception) { } }

                    var extSet = Exts();
                    string sln = dte.Solution != null ? dte.Solution.FullName : null;
                    root = string.IsNullOrEmpty(sln) ? null : Path.GetDirectoryName(sln);
                    var projects = new List<Project>();
                    var files = new List<string>();
                    if (scopeFolder.IsChecked == true)
                    {
                        if (root == null) { summary.Text = "ソリューションを開いてから使ってください。"; return; }
                        if (dte.Solution != null) foreach (Project p in dte.Solution.Projects) projects.Add(p);
                        var skip = IncludeService.SkipDirs(SyncService.Options);
                        files = await Task.Run(() => DiskFiles(root, extSet, skip));
                        await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                    }
                    else
                    {
                        projects = scopeSolution.IsChecked == true ? AllProjects() : SelectedProjects();
                        if (projects.Count == 0) projects = AllProjects();
                        var seen = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                        foreach (var p in projects) files.AddRange(ProjectFilesOf(p, extSet, seen));
                    }
                    scannedProjects = projects;
                    if (root == null && files.Count > 0) root = Path.GetDirectoryName(files[0]);

                    // 未保存の文書(書き換えると、保存したときに上書きされる)
                    var dirty = new HashSet<string>(StringComparer.OrdinalIgnoreCase);
                    try { foreach (Document d in dte.Documents) { try { if (!d.Saved) dirty.Add(d.FullName); } catch (Exception) { } } } catch (Exception) { }

                    var t = Target();
                    var e = Eol();
                    string baseDir = root;
                    rows = await Task.Run(() => files.Select(f =>
                    {
                        var r = new EncRow { File = f, Shown = Rel(baseDir, f), Dirty = dirty.Contains(f) };
                        try
                        {
                            if (new FileInfo(f).Length > 8 * 1024 * 1024) { r.Current = "-"; r.Eol = "-"; r.Action = "大きすぎるので飛ばす (8 MB 超)"; return r; }
                            r.Plan = EncodingTool.PlanFile(File.ReadAllBytes(f), t, e);
                            r.Current = EncodingTool.KindName(r.Plan.Before.Kind);
                            r.Eol = r.Plan.Before.EolName;
                            r.Action = r.Dirty && r.Plan.NewBytes != null ? "未保存なので飛ばす" : r.Plan.Action;
                        }
                        catch (Exception ex) { r.Current = "-"; r.Eol = "-"; r.Action = "読めない: " + ex.Message; }
                        return r;
                    }).ToList());
                    await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                    ShowRows();
                    convertButton.IsEnabled = rows.Any(Convertible);
                    copyButton.IsEnabled = rows.Count > 0;
                }
                catch (Exception ex) { summary.Text = "調べられませんでした: " + ex.Message; KCppAssistPackage.Log("encoding scan failed: " + ex); }
                finally { scanButton.IsEnabled = true; }
            }

            private static bool Convertible(EncRow r) { return r.Plan != null && r.Plan.NewBytes != null && !r.Dirty; }

            private void ShowRows()
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                list.ItemsSource = onlyChanges.IsChecked == true ? rows.Where(r => r.Action != "そのまま").ToList() : rows;
                if (rows.Count == 0) { summary.Text = "対象のファイルが見つかりませんでした。対象と拡張子を確かめてください。"; return; }
                var byKind = rows.Where(r => r.Plan != null).GroupBy(r => r.Current).Select(g => g.Key + " " + g.Count());
                int conv = rows.Count(Convertible), same = rows.Count(r => r.Action == "そのまま");
                int blocked = rows.Count(r => r.Plan != null && r.Plan.Blocked), dirtyN = rows.Count(r => r.Dirty && r.Plan != null && r.Plan.NewBytes != null);
                var sb = new StringBuilder();
                sb.Append(rows.Count).Append(" ファイル。いまの内訳: ").Append(string.Join(" / ", byKind)).Append("\n");
                sb.Append("変換する ").Append(conv).Append("、そのまま ").Append(same);
                if (blocked > 0) sb.Append("、変換できない ").Append(blocked);
                if (dirtyN > 0) sb.Append("、未保存で飛ばす ").Append(dirtyN);
                if (Target() == EncodingTool.Target.ShiftJis && editorConfig.IsChecked == true) sb.Append("\n.editorconfig は Shift-JIS を書けない (規格にない) ので、文字コードは書きません。改行だけ書きます。");
                summary.Text = sb.ToString();
            }

            private void CopyList()
            {
                var sb = new StringBuilder();
                foreach (var r in rows) sb.Append(r.Shown).Append('\t').Append(r.Current).Append('\t').Append(r.Eol).Append('\t').Append(r.Action).Append("\r\n");
                try { Clipboard.SetText(sb.ToString()); } catch (Exception) { }
            }

            // ---- 変換する ----

            private async Task ConvertAsync()
            {
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();
                var todo = rows.Where(Convertible).ToList();
                if (todo.Count == 0) return;
                var t = Target();
                var e = Eol();
                string msg = todo.Count + " 個のファイルを " + EncodingTool.TargetName(t) + (e == EncodingTool.Eol.Keep ? "" : "・" + (e == EncodingTool.Eol.Lf ? "LF" : "CRLF")) + " にそろえます。"
                    + "\n開いていないファイルは、そのまま保存します (Ctrl+Z では戻せません。戻すときは Git などを使います)。";
                if (!KDialog.Confirm("文字コードをそろえる", msg, null, "そろえる")) return;

                scanButton.IsEnabled = convertButton.IsEnabled = false;
                summary.Text = "変換しています…";
                var result = await Task.Run(() =>
                {
                    int ok = 0;
                    var failed = new List<string>();
                    foreach (var r in todo)
                    {
                        try
                        {
                            byte[] now = File.ReadAllBytes(r.File);
                            // 調べたあとで書き換わっていたら、計画を作り直す
                            var plan = EncodingTool.PlanFile(now, t, e);
                            if (plan.NewBytes == null) continue;
                            File.WriteAllBytes(r.File, plan.NewBytes);
                            r.Action = "変換しました";
                            r.Plan = null;
                            ok++;
                        }
                        catch (Exception ex) { failed.Add(r.Shown + ": " + ex.Message); r.Action = "失敗: " + ex.Message; }
                    }
                    return Tuple.Create(ok, failed);
                });
                await ThreadHelper.JoinableTaskFactory.SwitchToMainThreadAsync();

                var notes = new List<string>();
                if (editorConfig.IsChecked == true && root != null) notes.Add(WriteEditorConfig(t, e));
                if (t == EncodingTool.Target.Utf8 && sourceCharset.IsChecked == true) notes.Add(AddSourceCharset(scannedProjects));
                ShowRows();
                summary.Text = result.Item1 + " 個のファイルを変換しました" + (result.Item2.Count > 0 ? " (失敗 " + result.Item2.Count + ")" : "") + "。"
                    + string.Concat(notes.Where(n => !string.IsNullOrEmpty(n)).Select(n => "\n" + n));
                KCppAssistPackage.Log("encoding: converted " + result.Item1 + " failed " + result.Item2.Count);
                list.Items.Refresh();
                scanButton.IsEnabled = true;
            }

            /// <summary>ソリューションのフォルダーの .editorconfig に、文字コードと改行を書く(同じ見出しの節があれば、書き換える)。</summary>
            private string WriteEditorConfig(EncodingTool.Target t, EncodingTool.Eol e)
            {
                try
                {
                    string header = EncodingTool.SectionHeader(Exts());
                    if (header == null) return null;
                    string charset = EncodingTool.CharsetValue(t);
                    string endOfLine = e == EncodingTool.Eol.Keep ? null : e == EncodingTool.Eol.Lf ? "lf" : "crlf";
                    if (charset == null && endOfLine == null) return ".editorconfig には書きませんでした (Shift-JIS は .editorconfig の規格にありません)。";
                    string path = Path.Combine(root, ".editorconfig");
                    Encoding enc = new UTF8Encoding(false);
                    string old = File.Exists(path) ? RenameSync.ReadKeepingEncoding(path, out enc) : "";
                    string eolText = old.Contains("\r\n") || old.Length == 0 ? "\r\n" : "\n";
                    string updated = EncodingTool.UpdateEditorConfig(old, header, charset, endOfLine, eolText);
                    if (updated == old) return ".editorconfig は、すでにこの設定です。";
                    RenameSync.WriteKeepingEncoding(path, updated, enc);
                    try { if (dte.Solution != null) { var item = dte.Solution.FindProjectItem(path); } } catch (Exception) { }
                    return ".editorconfig に書きました: " + path;
                }
                catch (Exception ex) { return ".editorconfig に書けませんでした: " + ex.Message; }
            }

            /// <summary>
            /// C++ のプロジェクト(VCProject)のすべての構成に、/source-charset:utf-8 を付ける。BOM のない UTF-8 を、MSVC は Shift-JIS として読むため。
            /// /utf-8 は文字列リテラルの文字コードも変える(画面に出す日本語が化けることがある)ので、ソースの読み方だけを変えるこちらを使う。
            /// </summary>
            private string AddSourceCharset(List<Project> projects)
            {
                int done = 0, already = 0, notCpp = 0;
                foreach (var p in projects)
                {
                    try
                    {
                        object vcp = p.Object;
                        object configs = vcp == null ? null : Get(vcp, "Configurations");
                        if (configs == null) { notCpp++; continue; }
                        int count = Convert.ToInt32(Get(configs, "Count"));
                        bool changed = false;
                        for (int i = 1; i <= count; i++)
                        {
                            object cfg = Call(configs, "Item", i);
                            object tools = Get(cfg, "Tools");
                            object cl = tools == null ? null : Call(tools, "Item", "VCCLCompilerTool");
                            if (cl == null) continue;
                            string opts = (Get(cl, "AdditionalOptions") as string) ?? "";
                            if (opts.IndexOf("/utf-8", StringComparison.OrdinalIgnoreCase) >= 0 || opts.IndexOf("source-charset", StringComparison.OrdinalIgnoreCase) >= 0) { already++; continue; }
                            Set(cl, "AdditionalOptions", (opts.Trim() + " /source-charset:utf-8").Trim());
                            changed = true;
                        }
                        if (changed) { p.Save(); done++; }
                    }
                    catch (Exception ex) { notCpp++; KCppAssistPackage.Log("source-charset failed for " + SafeName(p) + ": " + ex.Message); }
                }
                if (done == 0 && already == 0) return "/source-charset:utf-8 は付けられませんでした (C++ のプロジェクト (.vcxproj) が見つかりません。CMake なら add_compile_options(/source-charset:utf-8) を書きます)。";
                return "/source-charset:utf-8 を " + done + " 個のプロジェクトに付けました" + (already > 0 ? " (すでに付いている構成 " + already + ")" : "") + "。";
            }

            private static string SafeName(Project p) { try { return p.Name; } catch (Exception) { return "?"; } }
            private static object Get(object o, string name) { return o.GetType().InvokeMember(name, BindingFlags.GetProperty, null, o, null); }
            private static void Set(object o, string name, object value) { o.GetType().InvokeMember(name, BindingFlags.SetProperty, null, o, new[] { value }); }
            private static object Call(object o, string name, object arg) { return o.GetType().InvokeMember(name, BindingFlags.InvokeMethod, null, o, new[] { arg }); }

            // ---- ファイルを集める ----

            private List<Project> AllProjects()
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                var list = new List<Project>();
                if (dte.Solution == null) return list;
                foreach (Project p in dte.Solution.Projects) Flatten(p, list);
                return list;
            }

            private List<Project> SelectedProjects()
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                var list = new List<Project>();
                try
                {
                    foreach (SelectedItem si in dte.SelectedItems)
                    {
                        if (si.Project != null) list.Add(si.Project);
                        else if (si.ProjectItem != null && si.ProjectItem.ContainingProject != null) list.Add(si.ProjectItem.ContainingProject);
                    }
                    if (list.Count == 0 && dte.ActiveDocument != null && dte.ActiveDocument.ProjectItem != null) list.Add(dte.ActiveDocument.ProjectItem.ContainingProject);
                }
                catch (Exception) { }
                return list.Where(p => p != null).Distinct().ToList();
            }

            /// <summary>ソリューション フォルダーの中のプロジェクトも、平らに並べる。</summary>
            private static void Flatten(Project p, List<Project> into)
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                if (p == null) return;
                into.Add(p);
                ProjectItems items = null;
                try { items = p.ProjectItems; } catch (Exception) { }
                if (items == null) return;
                foreach (ProjectItem it in items)
                {
                    Project sub = null;
                    try { sub = it.SubProject; } catch (Exception) { }
                    if (sub != null) Flatten(sub, into);
                }
            }

            private static IEnumerable<string> ProjectFilesOf(Project p, HashSet<string> exts, HashSet<string> seen)
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                ProjectItems items = null;
                try { items = p.ProjectItems; } catch (Exception) { }
                var result = new List<string>();
                Walk(items, exts, seen, result);
                return result;
            }

            private static void Walk(ProjectItems items, HashSet<string> exts, HashSet<string> seen, List<string> result)
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                if (items == null) return;
                foreach (ProjectItem it in items)
                {
                    string file = null;
                    try { if (it.FileCount > 0) file = it.FileNames[1]; } catch (Exception) { }
                    if (!string.IsNullOrEmpty(file) && File.Exists(file) && exts.Contains(Path.GetExtension(file)) && seen.Add(file)) result.Add(file);
                    ProjectItems sub = null;
                    try { sub = it.ProjectItems; } catch (Exception) { }
                    if (sub != null) Walk(sub, exts, seen, result);
                }
            }

            private static List<string> DiskFiles(string root, HashSet<string> exts, ISet<string> skip)
            {
                var list = new List<string>();
                var stack = new Stack<string>();
                stack.Push(root);
                while (stack.Count > 0 && list.Count < 50000)
                {
                    string dir = stack.Pop();
                    try
                    {
                        foreach (string f in Directory.GetFiles(dir)) if (exts.Contains(Path.GetExtension(f))) list.Add(f);
                        foreach (string d in Directory.GetDirectories(dir))
                        {
                            string leaf = Path.GetFileName(d);
                            if (skip.Contains(leaf) || leaf.StartsWith(".", StringComparison.Ordinal) || leaf.StartsWith("cmake-build", StringComparison.OrdinalIgnoreCase)) continue;
                            stack.Push(d);
                        }
                    }
                    catch (Exception) { }
                }
                return list;
            }

            private static string Rel(string baseDir, string file)
            {
                if (!string.IsNullOrEmpty(baseDir) && file.StartsWith(baseDir.TrimEnd('\\') + "\\", StringComparison.OrdinalIgnoreCase))
                    return file.Substring(baseDir.TrimEnd('\\').Length + 1);
                return file;
            }
        }
    }
}

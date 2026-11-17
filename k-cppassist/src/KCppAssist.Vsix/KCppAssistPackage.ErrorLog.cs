using System;
using System.IO;
using System.Linq;
using System.Threading;
using EnvDTE;
using EnvDTE80;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.TextManager.Interop;
using KCppAssist.ErrorLog;
using Task = System.Threading.Tasks.Task;
using ErrorLink = KCppAssist.ErrorLog.Run;

namespace KCppAssist
{
    /// <summary>
    /// K-ErrorLog の部分。ビルドが終わるたびに「出力」ウィンドウのビルド欄を読み、色つきのエラーログとして、専用の窓に出す。
    /// 未解決の外部シンボルは、原因ごとにまとめ、.lib とソースを探して、原因を言い当てる。
    /// </summary>
    public sealed partial class KCppAssistPackage
    {
        internal const int CmdErrorLog = 0x0107;
        // ビルドの出力欄(VSConstants.OutputWindowPaneGuid.BuildOutputPane_guid)
        private const string BuildPaneGuid = "{1BD8A850-02D1-11D1-BEE7-00A0C913D1F8}";

        private DTE2 _dte;
        private BuildEvents _buildEvents;
        private RenderInput _current;
        private CancellationTokenSource _enrichCts;
        private int _lastTextLength = -1;

        private OptionsPage ErrorLogOptions()
        {
            var o = (OptionsPage)GetDialogPage(typeof(OptionsPage));
            ErrorLogSettings.Load(o);
            return o;
        }

        private async Task InitializeErrorLogAsync()
        {
            _dte = await GetServiceAsync(typeof(DTE)) as DTE2;
            if (_dte != null)
            {
                _buildEvents = _dte.Events.BuildEvents;
                _buildEvents.OnBuildBegin += OnBuildBegin;
                _buildEvents.OnBuildDone += OnBuildDone;
            }
        }

        private void OnBuildBegin(vsBuildScope scope, vsBuildAction action)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                if (!ErrorLogOptions().ErrorLogEnabled) return;
                CancelEnrich();
                _current = null;
                var window = FindToolWindow(typeof(ErrorLogToolWindow), 0, false) as ErrorLogToolWindow;
                if (window != null) window.View.ShowMessage("ビルド中です…");
            }
            catch (Exception ex) { Log("build begin failed: " + ex.Message); }
        }

        private void OnBuildDone(vsBuildScope scope, vsBuildAction action)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var opt = ErrorLogOptions();
                if (!opt.ErrorLogEnabled) return;
                bool errors = Refresh(false);
                if (errors && opt.ErrorLogAutoShow) ShowWindow(false, false);
                // 出力欄への最後の書き込みが、遅れて届くことがある。少し待って、変わっていたら読み直す
                var ignored = JoinableTaskFactory.RunAsync(async delegate
                {
                    await Task.Delay(900);
                    await JoinableTaskFactory.SwitchToMainThreadAsync();
                    string text = ReadBuildPane();
                    if (text.Length != _lastTextLength)
                    {
                        bool more = Refresh(false);
                        if (more && opt.ErrorLogAutoShow) ShowWindow(false, false);
                    }
                    AppendNarrowHints();
                });
            }
            catch (Exception ex) { Log("build done failed: " + ex.Message); }
        }

        /// <summary>
        /// ビルドの出力欄(ログ)の末尾に、縮小変換の警告ごとに「直せます」の行を足す。
        /// 出力欄にボタンは置けないので、行のダブルクリックでその行へ飛び、Ctrl+. の電球で直す。
        /// 「warning」「error」の語は入れない(エラー一覧に二重に出ないように)。
        /// </summary>
        private void AppendNarrowHints()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var input = _current;
                if (input == null || input.Report == null || _dte == null) return;
                var lines = new System.Collections.Generic.List<string>();
                var seen = new System.Collections.Generic.HashSet<string>();
                foreach (var d in input.Report.Diags)
                {
                    if (lines.Count >= 30) break;
                    if (!d.HasLocation || !NarrowFix.IsCandidate(d.Code)) continue;
                    string type = NarrowFix.TargetType(d.Message);
                    if (type == null || !seen.Add(d.File + "|" + d.Line)) continue;
                    string src = null;
                    try
                    {
                        var all = System.IO.File.ReadAllLines(d.File);
                        if (d.Line >= 1 && d.Line <= all.Length) src = all[d.Line - 1];
                    }
                    catch (Exception) { }
                    if (src == null || NarrowFix.Make(src, type) == null) continue;
                    lines.Add(d.File + "(" + d.Line + "): K-CppAssist: static_cast<" + type + "> で直せます。ダブルクリックで飛んで Ctrl+. → 「右辺を static_cast にする」");
                }
                if (lines.Count == 0) return;
                foreach (OutputWindowPane pane in _dte.ToolWindows.OutputWindow.OutputWindowPanes)
                {
                    if (!string.Equals(pane.Guid, BuildPaneGuid, StringComparison.OrdinalIgnoreCase)) continue;
                    pane.OutputString("\r\n" + string.Join("\r\n", lines) + "\r\n");
                    break;
                }
            }
            catch (Exception ex) { Log("narrow hints failed: " + ex.Message); }
        }

        /// <summary>ビルド欄を読んで解析し、窓に出す。エラーがあれば true。</summary>
        internal bool Refresh(bool activate)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            ErrorLogOptions();
            string text = ReadBuildPane();
            _lastTextLength = text.Length;
            BuildReport report = BuildLogParser.Parse(text);

            var input = new RenderInput
            {
                Report = report,
                Syms = Diagnoser.Collect(report),
                Ctx = new AnalysisContext { SolutionDir = SolutionDir(), Platform = ActivePlatform() }
            };
            input.Pending = ErrorLogSettings.FindLibs && (input.Syms.Count > 0 || Diagnoser.NeedsFileSearch(report));

            CancelEnrich();
            _current = input;
            var window = FindToolWindow(typeof(ErrorLogToolWindow), 0, false) as ErrorLogToolWindow;
            if (window != null) window.View.SetInput(input);

            if (input.Pending) StartEnrich(input);
            return report.ErrorCount > 0;
        }

        // ウィンドウをまだ作っていない間に出た結果は、作ったときに渡す
        internal void PushPending(ErrorLogToolWindow window)
        {
            if (_current != null) window.View.SetInput(_current);
        }

        private void CancelEnrich()
        {
            var cts = _enrichCts;
            _enrichCts = null;
            if (cts != null) { try { cts.Cancel(); } catch (Exception) { } }
        }

        /// <summary>.lib とソースの検索を、別のスレッドで行う。終わったら、窓を描き直す。</summary>
        private void StartEnrich(RenderInput input)
        {
            var cts = new CancellationTokenSource();
            _enrichCts = cts;
            var token = cts.Token;
            var ignored = JoinableTaskFactory.RunAsync(async delegate
            {
                Diagnoser.EnrichResult result = null;
                try { result = await Task.Run(() => Diagnoser.Compute(input, token)); }
                catch (Exception ex) { Log("enrich failed: " + ex.Message); }

                await JoinableTaskFactory.SwitchToMainThreadAsync();
                if (token.IsCancellationRequested || !ReferenceEquals(_current, input)) return;
                if (result != null) Diagnoser.Apply(result);   // 画面が読むオブジェクトは、UI スレッドでだけ書き換える
                input.Pending = false;
                var window = FindToolWindow(typeof(ErrorLogToolWindow), 0, false) as ErrorLogToolWindow;
                if (window != null) window.View.Redraw();
            });
        }

        internal string SolutionDir()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                string path = _dte != null ? _dte.Solution.FullName : "";
                return string.IsNullOrEmpty(path) ? "" : Path.GetDirectoryName(path);
            }
            catch (Exception) { return ""; }
        }

        private string ActivePlatform()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var cfg = _dte.Solution.SolutionBuild.ActiveConfiguration as SolutionConfiguration2;
                return cfg != null ? cfg.PlatformName ?? "" : "";
            }
            catch (Exception) { return ""; }
        }

        private string ReadBuildPane()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                if (_dte == null) return "";
                foreach (OutputWindowPane pane in _dte.ToolWindows.OutputWindow.OutputWindowPanes)
                {
                    if (!string.Equals(pane.Guid, BuildPaneGuid, StringComparison.OrdinalIgnoreCase)) continue;
                    TextDocument doc = pane.TextDocument;
                    return doc.StartPoint.CreateEditPoint().GetText(doc.EndPoint);
                }
            }
            catch (Exception ex) { Log("read build pane failed: " + ex.Message); }
            return "";
        }

        private void ShowWindow(bool refresh, bool activate)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var window = FindToolWindow(typeof(ErrorLogToolWindow), 0, true) as ErrorLogToolWindow;
            if (window == null || window.Frame == null) return;
            window.Attach(this);
            if (refresh) Refresh(activate);
            var frame = (IVsWindowFrame)window.Frame;
            if (activate) frame.Show();
            else frame.ShowNoActivate();
            GrowWindow(frame);
        }

        /// <summary>下のパネルが低すぎると 1〜2 件しか見えないので、低いときだけ高くする(高くしてあるものは触らない)。</summary>
        private void GrowWindow(IVsWindowFrame frame)
        {
            try
            {
                object o;
                if (frame.GetProperty((int)__VSFPROPID.VSFPROPID_ExtWindowObject, out o) != 0) return;
                var w = o as EnvDTE.Window;
                if (w == null || w.Height >= 300) return;
                w.Height = 380;
            }
            catch (Exception ex) { Log("grow window failed: " + ex.Message); }
        }

        /// <summary>エラーログの「static_cast にする」を押したとき。その行の右辺を包む(1 回の Undo)。</summary>
        /// <summary>
        /// 直前のビルドの警告(C4267 など)のうち、path の lineNo 行目(1 から)にある縮小変換の、変換先の型。なければ null。
        /// 電球(Quick Fix)に「static_cast を付ける」を出すために、エディターから引く。
        /// </summary>
        internal string NarrowTypeAt(string path, int lineNo)
        {
            var input = _current;
            if (input == null || input.Report == null || path == null) return null;
            foreach (var d in input.Report.Diags)
            {
                if (d.Line != lineNo || !d.HasLocation || !NarrowFix.IsCandidate(d.Code)) continue;
                if (!string.Equals(d.File, path, StringComparison.OrdinalIgnoreCase)) continue;
                string type = NarrowFix.TargetType(d.Message);
                if (type != null) return type;
            }
            return null;
        }

        /// <summary>電球から: path の lineNo 行目の右辺を static_cast&lt;type&gt;(…) で包む(エラーログの「クリックで修正」と同じ処理)。</summary>
        internal void ApplyNarrowFixAt(string path, int lineNo, string type, string lineText)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            ApplyNarrowFix(new ErrorLink { File = path, Line = lineNo, Fix = type, FixLine = lineText.Trim() });
        }

        private void ApplyNarrowFix(ErrorLink run)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var model = (Microsoft.VisualStudio.ComponentModelHost.IComponentModel)GetService(typeof(Microsoft.VisualStudio.ComponentModelHost.SComponentModel));
            var adapters = model.GetService<Microsoft.VisualStudio.Editor.IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry>();
            var buf = SyncService.OpenForEdit(run.File, adapters);
            if (buf == null) { _ = ReportAsync("ファイルを開けませんでした: " + run.File, true); return; }
            var snap = buf.CurrentSnapshot;
            if (run.Line < 1 || run.Line > snap.LineCount) { _ = ReportAsync("行が見つかりません。ビルドし直してください。", true); return; }
            var line = snap.GetLineFromLineNumber(run.Line - 1);
            string text = line.GetText();
            if (text.Trim() != run.FixLine) { _ = ReportAsync("ファイルがビルドのあとで変わっています。ビルドし直してください。", true); return; }
            var plan = NarrowFix.Make(text, run.Fix);
            if (plan == null) { _ = ReportAsync("この行は、自動では直せません。", true); return; }
            SyncService.ApplyEdits(buf, new System.Collections.Generic.List<Tuple<int, int, string>> { Tuple.Create(line.Start.Position + plan.Start, plan.Length, plan.Text) }, undo, "K-CppAssist: static_cast を付ける");
            _ = ReportAsync("static_cast<" + run.Fix + ">(…) を付けました(" + run.Line + " 行目)。ビルドし直すと、ログが更新されます。", false);
        }

        /// <summary>
        /// エラーログの「全部を修正」を押したとき。表示している縮小変換の行を、ファイルごとに 1 回の Undo で static_cast で包む。
        /// ビルドのあとで行が変わっているもの・自動で直せないものは飛ばして、その数を知らせる。
        /// </summary>
        internal void ApplyAllNarrowFixes(System.Collections.Generic.List<ErrorLink> fixes)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                if (fixes == null || fixes.Count == 0) return;
                var byFile = fixes.GroupBy(f => f.File, StringComparer.OrdinalIgnoreCase).ToList();
                string list = string.Join("\n", byFile.Take(15).Select(g => Path.GetFileName(g.Key) + ": " + g.Count() + " か所"))
                    + (byFile.Count > 15 ? "\n… ほか " + (byFile.Count - 15) + " ファイル" : "");
                var ok = System.Windows.MessageBox.Show(fixes.Count + " か所の縮小変換を、static_cast<型>(…) で包みます。\n値が切り捨てられてよいか、確かめてから実行してください。\n\n" + list
                    + "\n\nファイルを開いて書き換えます (保存はしません。ファイルごとに Ctrl+Z で戻せます)。続けますか?",
                    "K-CppAssist: 全部を修正", System.Windows.MessageBoxButton.YesNo, System.Windows.MessageBoxImage.Question);
                if (ok != System.Windows.MessageBoxResult.Yes) return;

                var model = (Microsoft.VisualStudio.ComponentModelHost.IComponentModel)GetService(typeof(Microsoft.VisualStudio.ComponentModelHost.SComponentModel));
                var adapters = model.GetService<Microsoft.VisualStudio.Editor.IVsEditorAdaptersFactoryService>();
                var undo = model.GetService<Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry>();
                int done = 0, skipped = 0;
                foreach (var g in byFile)
                {
                    var buf = SyncService.OpenForEdit(g.Key, adapters);
                    if (buf == null) { skipped += g.Count(); continue; }
                    var snap = buf.CurrentSnapshot;
                    var edits = new System.Collections.Generic.List<Tuple<int, int, string>>();
                    foreach (var run in g)
                    {
                        if (run.Line < 1 || run.Line > snap.LineCount) { skipped++; continue; }
                        var line = snap.GetLineFromLineNumber(run.Line - 1);
                        string text = line.GetText();
                        var plan = text.Trim() == run.FixLine ? NarrowFix.Make(text, run.Fix) : null;
                        if (plan == null) { skipped++; continue; }
                        edits.Add(Tuple.Create(line.Start.Position + plan.Start, plan.Length, plan.Text));
                    }
                    if (edits.Count == 0) continue;
                    SyncService.ApplyEdits(buf, edits, undo, "K-CppAssist: static_cast をまとめて付ける");
                    done += edits.Count;
                }
                _ = ReportAsync("static_cast を " + done + " か所に付けました"
                    + (skipped > 0 ? "(" + skipped + " か所は、ビルドのあとで行が変わっているか、自動で直せないので飛ばしました)" : "")
                    + "。ビルドし直すと、ログが更新されます。", done == 0);
            }
            catch (Exception ex) { Log("fix all failed: " + ex); }
        }

        // ---- リンクを押したとき ----

        internal void OnLink(ErrorLink run)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                if (!string.IsNullOrEmpty(run.Fix)) ApplyNarrowFix(run);
                else if (!string.IsNullOrEmpty(run.File)) OpenFile(run.File, run.Line, run.Col);
                else if (!string.IsNullOrEmpty(run.Search)) FindInSolution(run.Search);
                else if (!string.IsNullOrEmpty(run.Url) && run.Url.StartsWith("https://learn.microsoft.com/", StringComparison.Ordinal))
                    System.Diagnostics.Process.Start(run.Url);
            }
            catch (Exception ex) { Log("link failed: " + ex.Message); }
        }

        private void OpenFile(string path, int line, int col)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (!File.Exists(path))
            {
                string dir = SolutionDir();
                string alt = dir.Length > 0 ? Path.Combine(dir, path) : path;
                if (!File.Exists(alt)) return;
                path = alt;
            }
            IVsUIHierarchy hier;
            uint itemId;
            IVsWindowFrame frame;
            VsShellUtilities.OpenDocument(this, path, Guid.Empty, out hier, out itemId, out frame);
            if (frame == null) return;
            frame.Show();
            IVsTextView view = VsShellUtilities.GetTextView(frame);
            if (view == null || line <= 0) return;
            int l = Math.Max(line - 1, 0);
            int c = Math.Max(col - 1, 0);
            view.SetCaretPos(l, c);
            view.CenterLines(l, 1);
        }

        /// <summary>ソリューション全体から語を探して、「検索結果 1」に出す(宣言と定義の場所を探すため)。</summary>
        private void FindInSolution(string term)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (_dte == null) return;
            Find find = _dte.Find;
            find.FindWhat = term;
            find.Target = vsFindTarget.vsFindTargetSolution;
            find.MatchCase = true;
            find.MatchWholeWord = true;
            find.SearchSubfolders = true;
            find.FilesOfType = "*.h;*.hpp;*.hh;*.hxx;*.inl;*.cpp;*.cc;*.cxx;*.c;*.ixx";
            find.Action = vsFindAction.vsFindActionFindAll;
            find.ResultsLocation = vsFindResultsLocation.vsFindResults1;
            find.Execute();
        }
    }
}

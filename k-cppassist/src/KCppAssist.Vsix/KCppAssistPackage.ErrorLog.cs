using System;
using System.IO;
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
                });
            }
            catch (Exception ex) { Log("build done failed: " + ex.Message); }
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
        }

        // ---- リンクを押したとき ----

        internal void OnLink(ErrorLink run)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                if (!string.IsNullOrEmpty(run.File)) OpenFile(run.File, run.Line, run.Col);
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

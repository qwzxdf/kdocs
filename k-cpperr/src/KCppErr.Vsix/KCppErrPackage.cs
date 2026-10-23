using System;
using System.ComponentModel.Design;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using EnvDTE;
using EnvDTE80;
using Microsoft.VisualStudio;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Task = System.Threading.Tasks.Task;

namespace KCppErr
{
    /// <summary>
    /// ビルドが終わるたびに「出力」ウィンドウのビルド欄を読み、エラーを自分のコードの場所つきで一覧にする。
    /// 一覧はエラー一覧のとなりに出る。
    /// </summary>
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [InstalledProductRegistration("K-CppErr", "C++ エラーを、自分のコードの場所つきで表示する", "1.0.0")]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [ProvideToolWindow(typeof(ErrorToolWindow), Style = VsDockStyle.Tabbed, Window = "D78612C7-9962-4B83-95D9-268046DAD23A")]
    [ProvideAutoLoad(VSConstants.UICONTEXT.SolutionExists_string, PackageAutoLoadFlags.BackgroundLoad)]
    [Guid(PackageGuid)]
    public sealed class KCppErrPackage : AsyncPackage
    {
        public const string PackageGuid = "3e8c4a72-91d5-4b06-a7c2-5f1d8e6b0a34";
        private static readonly Guid CmdSet = new Guid("a4d2b7c9-6e13-4f85-92a0-7c3b1e5d8f46");
        private const int CmdShow = 0x0100;
        // ビルドの出力欄(VSConstants.OutputWindowPaneGuid.BuildOutputPane_guid)
        private const string BuildPaneGuid = "{1BD8A850-02D1-11D1-BEE7-00A0C913D1F8}";

        private DTE2 _dte;
        private BuildEvents _buildEvents;

        internal static void Log(string text)
        {
            try
            {
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-CppErr");
                Directory.CreateDirectory(dir);
                File.AppendAllText(Path.Combine(dir, "vsix.log"), DateTime.Now.ToString("HH:mm:ss.fff") + " " + text + Environment.NewLine);
            }
            catch (Exception) { }
        }

        protected override async Task InitializeAsync(CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
            _dte = await GetServiceAsync(typeof(DTE)) as DTE2;
            if (_dte != null)
            {
                _buildEvents = _dte.Events.BuildEvents;
                _buildEvents.OnBuildDone += OnBuildDone;
            }
            var commands = await GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            if (commands != null)
                commands.AddCommand(new MenuCommand((s, e) => ShowWindow(true), new CommandID(CmdSet, CmdShow)));
            Log("package initialized");
        }

        private void OnBuildDone(vsBuildScope scope, vsBuildAction action)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                // 出力欄への書き込みが落ち着くのを待たず、同じターンで読む。足りなければ「読み直す」で再取得できる
                bool any = Refresh();
                if (any) ShowWindow(false);
            }
            catch (Exception ex) { Log("build done failed: " + ex.Message); }
        }

        /// <summary>ビルド欄を読んで、一覧を更新する。エラーがあれば true。</summary>
        internal bool Refresh()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            string text = ReadBuildPane();
            var groups = BuildOutputParser.Parse(text);
            var window = FindToolWindow(typeof(ErrorToolWindow), 0, false) as ErrorToolWindow;
            if (window != null) window.View.SetResult(groups, SolutionDir());
            else lastGroups = groups;
            return groups.Exists(g => g.IsError);
        }

        // ウィンドウをまだ作っていない間の結果(ウィンドウを作ったときに渡す)
        private System.Collections.Generic.List<ErrorGroup> lastGroups;

        internal System.Collections.Generic.List<ErrorGroup> TakePending()
        {
            var g = lastGroups;
            lastGroups = null;
            return g;
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

        private void ShowWindow(bool refresh)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var window = FindToolWindow(typeof(ErrorToolWindow), 0, true) as ErrorToolWindow;
            if (window == null || window.Frame == null) return;
            window.Attach(this);
            var pending = TakePending();
            if (pending != null) window.View.SetResult(pending, SolutionDir());
            else if (refresh) Refresh();
            ((IVsWindowFrame)window.Frame).Show();
        }
    }
}

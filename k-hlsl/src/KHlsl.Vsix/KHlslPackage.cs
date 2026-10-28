using System;
using System.ComponentModel.Design;
using System.Diagnostics;
using System.IO;
using System.Runtime.InteropServices;
using System.Threading;
using Microsoft.VisualStudio;
using Microsoft.VisualStudio.ComponentModelHost;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Utilities;
using Task = System.Threading.Tasks.Task;

namespace KHlsl.Vsix
{
    /// <summary>
    /// VS の起動時に読み込まれ、HLSL のドキュメントが作られた瞬間(ビューやタガーが作られるより前)に、
    /// バッファのコンテンツ タイプを "khlsl" へ切り替える。VS 標準の言語サービスが後から元の
    /// コンテンツ タイプに戻すので、戻されたら、その場でもう一度切り替える。
    /// 古い HLSL 拡張は "hlsl" コンテンツ タイプに従来型の補完などを登録していて、同じバッファでは
    /// LSP の補完が使われない。"khlsl" へ切り離すと、K-HLSL の機能だけが働く。
    /// </summary>
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [InstalledProductRegistration("K-HLSL", "HLSL language support (SM 6.9)", "1.3.6")]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [ProvideOptionPage(typeof(KHlslColorOptions), "K-HLSL", "色", 0, 0, true)]
    [ProvideToolWindow(typeof(CBufferToolWindow), Style = VsDockStyle.Tabbed, Window = "34E76E81-EE4A-11D0-AE2E-00A0C90FFFC3")]
    [ProvideAutoLoad(VSConstants.UICONTEXT.NoSolution_string, PackageAutoLoadFlags.BackgroundLoad)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.SolutionExists_string, PackageAutoLoadFlags.BackgroundLoad)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.EmptySolution_string, PackageAutoLoadFlags.BackgroundLoad)]
    [Guid(PackageGuid)]
    public sealed class KHlslPackage : AsyncPackage
    {
        public const string PackageGuid = "5b0c2f4e-6a1d-4c7b-9f33-8d1e7a2b4c90";

        // 拡張機能 メニューの「K-HLSL」(KHlsl.vsct と同じ値)
        private static readonly Guid CmdSet = new Guid("c7a9d3e1-4b52-4f08-8a6e-3d2f19b0e7c4");
        private const int CmdOpenDocs = 0x0102;
        private const int CmdOpenLogs = 0x0103;
        private const int CmdCBuffer = 0x0104;
        private const int CmdColorSettings = 0x0105;
        private const string DocsUrl = "https://qwzxdf.github.io/kdocs/khlsl/";

        internal static void Log(string text)
        {
            try
            {
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-HLSL");
                Directory.CreateDirectory(dir);
                File.AppendAllText(Path.Combine(dir, "vsix.log"), DateTime.Now.ToString("HH:mm:ss.fff") + " " + text + Environment.NewLine);
            }
            catch (Exception) { }
        }

        private ITextDocumentFactoryService _documents;
        private IContentTypeRegistryService _contentTypes;

        internal static KHlslPackage Current;

        protected override async Task InitializeAsync(CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            Current = this;
            await JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
            var model = await GetServiceAsync(typeof(SComponentModel)) as IComponentModel;
            if (model == null) return;
            _documents = model.GetService<ITextDocumentFactoryService>();
            _contentTypes = model.GetService<IContentTypeRegistryService>();
            _documents.TextDocumentCreated += OnDocumentCreated;
            var commands = await GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            if (commands != null)
            {
                AddCommand(commands, CmdColorSettings, (s, e) => ShowOptionPage(typeof(KHlslColorOptions)));
                AddCommand(commands, CmdOpenDocs, (s, e) => OpenShell(DocsUrl));
                AddCommand(commands, CmdCBuffer, (s, e) => ShowCBufferWindow());
                AddCommand(commands, CmdOpenLogs, (s, e) => OpenShell(Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-HLSL")));
            }
            var dte = await GetServiceAsync(typeof(EnvDTE.DTE)) as EnvDTE80.DTE2;
            if (dte != null)
            {
                // 保存したときと、別のファイルへ移ったときに、開いていれば定数バッファの表示を読み直す
                _documentEvents = dte.Events.DocumentEvents;
                _documentEvents.DocumentSaved += d => RefreshCBufferWindow();
                _windowEvents = dte.Events.WindowEvents;
                _windowEvents.WindowActivated += (got, lost) => RefreshCBufferWindow();
            }
            Log("package initialized");
        }

        private EnvDTE.DocumentEvents _documentEvents;
        private EnvDTE.WindowEvents _windowEvents;

        private void ShowCBufferWindow()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var window = FindToolWindow(typeof(CBufferToolWindow), 0, true) as CBufferToolWindow;
            if (window == null || window.Frame == null) return;
            ((Microsoft.VisualStudio.Shell.Interop.IVsWindowFrame)window.Frame).Show();
            window.View.Reload(true);
        }

        /// <summary>C++ の構造体を、HLSL の cbuffer と比べる(C++ のホバーのリンクから呼ばれる)。</summary>
        internal void ShowCompare(string cppPath, string cppText, string cppStruct)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var window = FindToolWindow(typeof(CBufferToolWindow), 0, true) as CBufferToolWindow;
            if (window == null || window.Frame == null) return;
            ((Microsoft.VisualStudio.Shell.Interop.IVsWindowFrame)window.Frame).Show();
            window.View.ShowCompare(cppPath, cppText, cppStruct);
        }

        private void RefreshCBufferWindow()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var window = FindToolWindow(typeof(CBufferToolWindow), 0, false) as CBufferToolWindow;
                if (window != null && window.View.IsVisible) window.View.Reload(false);
            }
            catch (Exception ex) { Log("refresh failed: " + ex.Message); }
        }

        private static void AddCommand(OleMenuCommandService service, int id, EventHandler handler)
        {
            service.AddCommand(new MenuCommand(handler, new CommandID(CmdSet, id)));
        }

        private static void OpenShell(string target)
        {
            try { Process.Start(new ProcessStartInfo(target) { UseShellExecute = true }); }
            catch (Exception ex) { Log("open failed: " + ex.Message); }
        }

        private void OnDocumentCreated(object sender, TextDocumentEventArgs e)
        {
            try
            {
                var doc = e.TextDocument;
                string path = doc.FilePath;
                if (string.IsNullOrEmpty(path) || !KHlslContentType.Extensions.Contains(Path.GetExtension(path))) return;
                var buffer = doc.TextBuffer;
                Log("document created: " + path + " type=" + buffer.ContentType.TypeName);
                Switch(buffer);
                buffer.ContentTypeChanged += (s, args) => Switch(buffer);
            }
            catch (Exception) { }
        }

        private bool _switching;

        private void Switch(ITextBuffer buffer)
        {
            if (_switching || buffer.ContentType.IsOfType(KHlslContentType.Name)) return;
            try
            {
                _switching = true;
                var ct = _contentTypes.GetContentType(KHlslContentType.Name);
                if (ct != null)
                {
                    buffer.ChangeContentType(ct, null);
                    Log("switched to khlsl");
                }
            }
            catch (Exception) { }
            finally { _switching = false; }
        }

        protected override void Dispose(bool disposing)
        {
            if (disposing && _documents != null) _documents.TextDocumentCreated -= OnDocumentCreated;
            base.Dispose(disposing);
        }
    }
}

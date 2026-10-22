using System;
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
    [InstalledProductRegistration("K-HLSL", "HLSL language support (SM 6.9)", "1.0.5")]
    [ProvideAutoLoad(VSConstants.UICONTEXT.NoSolution_string, PackageAutoLoadFlags.BackgroundLoad)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.SolutionExists_string, PackageAutoLoadFlags.BackgroundLoad)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.EmptySolution_string, PackageAutoLoadFlags.BackgroundLoad)]
    [Guid(PackageGuid)]
    public sealed class KHlslPackage : AsyncPackage
    {
        public const string PackageGuid = "5b0c2f4e-6a1d-4c7b-9f33-8d1e7a2b4c90";

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

        protected override async Task InitializeAsync(CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
            var model = await GetServiceAsync(typeof(SComponentModel)) as IComponentModel;
            if (model == null) return;
            _documents = model.GetService<ITextDocumentFactoryService>();
            _contentTypes = model.GetService<IContentTypeRegistryService>();
            _documents.TextDocumentCreated += OnDocumentCreated;
            Log("package initialized");
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

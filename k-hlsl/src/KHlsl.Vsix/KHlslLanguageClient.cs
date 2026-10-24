using System;
using System.Collections.Generic;
using System.ComponentModel.Composition;
using System.Diagnostics;
using System.IO;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;
using Microsoft.VisualStudio.LanguageServer.Client;
using Microsoft.VisualStudio.Threading;
using Microsoft.VisualStudio.Utilities;
using Newtonsoft.Json.Linq;
using StreamJsonRpc;

namespace KHlsl.Vsix
{
    /// <summary>K-HLSL の言語サーバー(KHlslServer.exe)を起動して、VS とつなぐ。</summary>
    [ContentType(KHlslContentType.Name)]
    [Export(typeof(ILanguageClient))]
    public sealed class KHlslLanguageClient : ILanguageClient, ILanguageClientCustomMessage2
    {
        public string Name => "K-HLSL";
        public IEnumerable<string> ConfigurationSections => null;
        public object InitializationOptions => null;
        public IEnumerable<string> FilesToWatch => new[] { "**/.khlsl.json" };
        public bool ShowNotificationOnInitializeFailed => true;

        public event AsyncEventHandler<EventArgs> StartAsync;
        public event AsyncEventHandler<EventArgs> StopAsync { add { } remove { } }

        // 独自のリクエスト(khlsl/cbuffers)を送るための接続
        private static volatile JsonRpc _rpc;

        public object MiddleLayer => null;
        public object CustomMessageTarget => null;

        public Task AttachForCustomMessageAsync(JsonRpc rpc)
        {
            _rpc = rpc;
            return Task.CompletedTask;
        }

        /// <summary>言語サーバーに、定数バッファのレイアウトを問い合わせる。サーバーがまだ動いていなければ null。</summary>
        internal static async Task<JToken> RequestCBuffersAsync(string path, bool includeStructs)
        {
            var rpc = _rpc;
            if (rpc == null) return null;
            string uri = new Uri(path).AbsoluteUri;
            return await rpc.InvokeWithParameterObjectAsync<JToken>("khlsl/cbuffers", new { uri, includeStructs }).ConfigureAwait(false);
        }

        /// <summary>言語サーバーが動いていて、独自のリクエストを送れるか。</summary>
        internal static bool IsConnected { get { return _rpc != null; } }

        /// <summary>言語サーバーへ、独自のリクエストを送る。接続がなければ null。</summary>
        internal static async Task<JToken> RequestAsync(string method, object args)
        {
            var rpc = _rpc;
            if (rpc == null) return null;
            return await rpc.InvokeWithParameterObjectAsync<JToken>(method, args).ConfigureAwait(false);
        }

        public async Task<Connection> ActivateAsync(CancellationToken token)
        {
            await Task.Yield();
            string dir = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
            string exe = Path.Combine(dir, "Server", "KHlslServer.exe");
            var psi = new ProcessStartInfo
            {
                FileName = exe,
                WorkingDirectory = Path.GetDirectoryName(exe),
                RedirectStandardInput = true,
                RedirectStandardOutput = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };
            var process = new Process { StartInfo = psi };
            if (!process.Start()) return null;
            return new Connection(process.StandardOutput.BaseStream, process.StandardInput.BaseStream);
        }

        public async Task OnLoadedAsync()
        {
            if (StartAsync != null) await StartAsync.InvokeAsync(this, EventArgs.Empty);
        }

        public Task OnServerInitializedAsync() => Task.CompletedTask;

        public Task<InitializationFailureContext> OnServerInitializeFailedAsync(ILanguageClientInitializationInfo initializationState)
        {
            return Task.FromResult(new InitializationFailureContext
            {
                FailureMessage = "K-HLSL の言語サーバーを起動できませんでした: " + initializationState?.InitializationException?.Message
            });
        }
    }
}

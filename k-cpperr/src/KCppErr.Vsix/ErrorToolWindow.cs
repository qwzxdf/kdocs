using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;

namespace KCppErr
{
    [Guid("6b1f9d03-2c74-4e8a-b5d9-0a7e3c418f92")]
    public sealed class ErrorToolWindow : ToolWindowPane
    {
        public ErrorView View { get; private set; }

        public ErrorToolWindow() : base(null)
        {
            Caption = "C++ エラー(かんたん表示)";
            View = new ErrorView();
            Content = View;
        }

        public override void OnToolWindowCreated()
        {
            base.OnToolWindowCreated();
            var package = Package as KCppErrPackage;
            if (package != null) Attach(package);
        }

        /// <summary>パッケージを結びつける。ファイルを開く処理と、「読み直す」ボタンが使う。</summary>
        public void Attach(KCppErrPackage package)
        {
            View.Initialize(package);
            View.RefreshRequested = () => package.Refresh();
        }
    }
}

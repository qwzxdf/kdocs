using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;

namespace KErrorLog
{
    [Guid("0d5d510a-337f-42df-856a-402ea91535ef")]
    public sealed class ErrorLogToolWindow : ToolWindowPane
    {
        public LogView View { get; private set; }

        public ErrorLogToolWindow() : base(null)
        {
            Caption = "K-ErrorLog";
            View = new LogView();
            Content = View;
        }

        public override void OnToolWindowCreated()
        {
            base.OnToolWindowCreated();
            var package = Package as KErrorLogPackage;
            if (package != null) Attach(package);
        }

        /// <summary>パッケージを結びつける。リンクを開く処理と、「再読み込み」が使う。</summary>
        public void Attach(KErrorLogPackage package)
        {
            View.RefreshRequested = () => package.Refresh(true);
            View.LinkClicked = package.OnLink;
            package.PushPending(this);
        }
    }
}

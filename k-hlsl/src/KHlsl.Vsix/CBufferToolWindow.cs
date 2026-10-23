using System;
using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;

namespace KHlsl.Vsix
{
    /// <summary>「K-HLSL 定数バッファ」のツール ウィンドウ。</summary>
    [Guid("9d4f7a21-3c58-4b6e-8a90-1e2b5c7d4f63")]
    public sealed class CBufferToolWindow : ToolWindowPane
    {
        public CBufferView View { get; private set; }

        public CBufferToolWindow() : base(null)
        {
            Caption = "K-HLSL 定数バッファ";
            View = new CBufferView();
            Content = View;
        }

        public override void OnToolWindowCreated()
        {
            base.OnToolWindowCreated();
            View.Initialize(Package as IServiceProvider);
        }
    }
}

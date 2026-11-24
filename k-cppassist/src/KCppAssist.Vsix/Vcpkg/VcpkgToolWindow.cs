using System.Runtime.InteropServices;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist.Vcpkg
{
    /// <summary>vcpkg のパッケージ ブラウザーの窓(エディターと同じ場所に、タブとして開く)。</summary>
    [Guid("6c1f2d84-5b3a-4e7d-9a60-2f8d1c4e7b95")]
    public sealed class VcpkgToolWindow : ToolWindowPane
    {
        internal VcpkgView View { get; private set; }

        public VcpkgToolWindow() : base(null)
        {
            Caption = "K-vcpkg";
            View = new VcpkgView();
            Content = View;
        }

        public override void OnToolWindowCreated()
        {
            base.OnToolWindowCreated();
            var package = Package as KCppAssistPackage;
            if (package != null) package.AttachVcpkg(View);
        }
    }
}

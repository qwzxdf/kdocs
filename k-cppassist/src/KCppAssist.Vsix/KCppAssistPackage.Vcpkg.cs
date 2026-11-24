using System;
using System.Collections.Generic;
using System.IO;
using System.ComponentModel.Design;
using EnvDTE;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using KCppAssist.Vcpkg;

namespace KCppAssist
{
    /// <summary>vcpkg のパッケージ ブラウザー(K-vcpkg)を開くコマンドと、ソリューションの情報を窓へ渡す部分。</summary>
    public sealed partial class KCppAssistPackage
    {
        internal const int CmdVcpkg = 0x0116;

        private void RegisterVcpkgCommand(OleMenuCommandService commands)
        {
            commands.AddCommand(new OleMenuCommand((s, e) => ShowVcpkgWindow(), new CommandID(CmdSet, CmdVcpkg)));
        }

        private void ShowVcpkgWindow()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var window = FindToolWindow(typeof(VcpkgToolWindow), 0, true) as VcpkgToolWindow;
                if (window == null || window.Frame == null) return;
                AttachVcpkg(window.View);
                var frame = (IVsWindowFrame)window.Frame;
                // ドッキングせず、独立した窓として開く
                frame.SetProperty((int)__VSFPROPID.VSFPROPID_FrameMode, VSFRAMEMODE.VSFM_Float);
                frame.Show();
            }
            catch (Exception ex) { Log("vcpkg window failed: " + ex.Message); }
        }

        internal void AttachVcpkg(VcpkgView view)
        {
            view.SolutionDir = () => SolutionDirectory();
            view.ProjectDirs = () => ProjectDirectories();
        }

        private string SolutionDirectory()
        {
            try
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                string full = _dte != null && _dte.Solution != null ? _dte.Solution.FullName : null;
                return string.IsNullOrEmpty(full) ? null : Path.GetDirectoryName(full);
            }
            catch { return null; }
        }

        /// <summary>ソリューションの C++ プロジェクトなどの、(名前, フォルダ)。ソリューション フォルダの中も、たどる。</summary>
        private List<KeyValuePair<string, string>> ProjectDirectories()
        {
            var list = new List<KeyValuePair<string, string>>();
            try
            {
                ThreadHelper.ThrowIfNotOnUIThread();
                if (_dte == null || _dte.Solution == null) return list;
                foreach (Project p in _dte.Solution.Projects) CollectProjects(p, list, 0);
            }
            catch (Exception ex) { Log("vcpkg projects failed: " + ex.Message); }
            return list;
        }

        private static void CollectProjects(Project p, List<KeyValuePair<string, string>> list, int depth)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (p == null || depth > 8) return;
            const string solutionFolder = "{66A26720-8FB5-11D2-AA7E-00C04F688DDE}";
            if (string.Equals(p.Kind, solutionFolder, StringComparison.OrdinalIgnoreCase))
            {
                if (p.ProjectItems == null) return;
                foreach (ProjectItem item in p.ProjectItems) CollectProjects(item.SubProject, list, depth + 1);
                return;
            }
            string full = null;
            try { full = p.FullName; } catch { }
            if (string.IsNullOrEmpty(full)) return;
            string dir = Path.GetDirectoryName(full);
            if (!string.IsNullOrEmpty(dir) && Directory.Exists(dir)) list.Add(new KeyValuePair<string, string>(p.Name, dir));
        }
    }
}

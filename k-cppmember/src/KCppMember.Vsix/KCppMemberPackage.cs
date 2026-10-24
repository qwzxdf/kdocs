using System;
using System.ComponentModel.Design;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;
using System.Threading;
using Microsoft.VisualStudio;
using Microsoft.VisualStudio.ComponentModelHost;
using Microsoft.VisualStudio.Editor;
using Microsoft.VisualStudio.Language.Intellisense;
using Microsoft.VisualStudio.Shell;
using Microsoft.VisualStudio.Shell.Interop;
using Microsoft.VisualStudio.Text;
using Microsoft.VisualStudio.Text.Adornments;
using Microsoft.VisualStudio.Text.Editor;
using Microsoft.VisualStudio.TextManager.Interop;
using Task = System.Threading.Tasks.Task;

namespace KCppMember
{
    /// <summary>
    /// 宣言していない変数への代入に、型を付ける。
    /// Alt+Q はローカル変数、Alt+W はクラスのメンバー変数にする。
    /// 今は最小版で、右辺の関数呼び出しの Quick Info を取って、ログに出すだけ。
    /// </summary>
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [InstalledProductRegistration("K-CppMember", "宣言していない変数に型を付ける", "0.1.0")]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.SolutionExists_string, PackageAutoLoadFlags.BackgroundLoad)]
    [Guid(PackageGuid)]
    public sealed class KCppMemberPackage : AsyncPackage
    {
        public const string PackageGuid = "b2f6c1a8-3d47-4e09-9a5c-81e7d0f4b362";
        private static readonly Guid CmdSet = new Guid("e5a93d17-0c82-4b6f-a1d4-6f27b8c30e95");
        private const int CmdLocal = 0x0100;
        private const int CmdMember = 0x0101;

        internal static void Log(string text)
        {
            try
            {
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-CppMember");
                Directory.CreateDirectory(dir);
                File.AppendAllText(Path.Combine(dir, "vsix.log"), DateTime.Now.ToString("HH:mm:ss.fff") + " " + text + Environment.NewLine);
            }
            catch (Exception) { }
        }

        protected override async Task InitializeAsync(CancellationToken cancellationToken, IProgress<ServiceProgressData> progress)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync(cancellationToken);
            var commands = await GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            if (commands != null)
            {
                commands.AddCommand(new MenuCommand((s, e) => Run(false), new CommandID(CmdSet, CmdLocal)));
                commands.AddCommand(new MenuCommand((s, e) => Run(true), new CommandID(CmdSet, CmdMember)));
            }
            Log("package initialized");
        }

        private void Run(bool member)
        {
            JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunAsync(member); }
                catch (Exception ex) { Fail("例外: " + ex.Message); Log(ex.ToString()); }
            });
        }

        private void Fail(string message)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            Log("FAIL " + message);
            var bar = GetService(typeof(SVsStatusbar)) as IVsStatusbar;
            if (bar != null) bar.SetText("K-CppMember: " + message);
        }

        private async Task RunAsync(bool member)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var broker = model.GetService<IAsyncQuickInfoBroker>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { Fail("アクティブなエディターがありません"); return; }

            ITextSnapshot snap = view.TextSnapshot;
            ITextSnapshotLine line = view.Caret.Position.BufferPosition.GetContainingLine();
            string text = line.GetText();
            int caretCol = view.Caret.Position.BufferPosition.Position - line.Start.Position;

            string name = IdentifierAt(text, caretCol);
            if (name == null) { Fail("カーソルの下に識別子がありません"); return; }

            // 「name = 右辺;」の形だけ扱う
            int nameEnd = text.IndexOf(name, StringComparison.Ordinal) + name.Length;
            int eq = text.IndexOf('=', nameEnd);
            if (eq < 0) { Fail("同じ行に代入 (=) がありません"); return; }
            string rhs = text.Substring(eq + 1).Trim().TrimEnd(';').Trim();

            // 右辺のいちばん外側の関数呼び出し。最初の '(' の直前の識別子の位置で Quick Info を引く
            int rhsStart = line.Start.Position + eq + 1;
            int paren = rhs.IndexOf('(');
            string info = "(関数呼び出しなし)";
            if (paren > 0)
            {
                int callEnd = text.IndexOf(rhs, eq + 1, StringComparison.Ordinal) + paren; // '(' の位置
                int pos = line.Start.Position + callEnd - 1;
                var tp = snap.CreateTrackingPoint(pos, PointTrackingMode.Positive);
                IAsyncQuickInfoSession session = await broker.TriggerQuickInfoAsync(view, tp, QuickInfoSessionOptions.None);
                info = session == null ? "(Quick Info なし)" : Flatten(session.Content);
                if (session != null) await session.DismissAsync();
            }

            Log("mode=" + (member ? "member" : "local") + " name=" + name + " rhs=" + rhs);
            Log("quickinfo: " + info);
            var bar = GetService(typeof(SVsStatusbar)) as IVsStatusbar;
            if (bar != null) bar.SetText("K-CppMember: " + name + " ← " + info.Replace("\r", " ").Replace("\n", " "));
        }

        private static string IdentifierAt(string s, int col)
        {
            if (col > s.Length) col = s.Length;
            int a = col, b = col;
            while (a > 0 && IsId(s[a - 1])) a--;
            while (b < s.Length && IsId(s[b])) b++;
            return b > a ? s.Substring(a, b - a) : null;
        }

        private static bool IsId(char c) { return char.IsLetterOrDigit(c) || c == '_'; }

        /// <summary>Quick Info の内容(ContainerElement の入れ子)を、文字だけの 1 本にする。</summary>
        private static string Flatten(object content)
        {
            var sb = new StringBuilder();
            Walk(content, sb);
            return sb.ToString();
        }

        private static void Walk(object o, StringBuilder sb)
        {
            if (o == null) return;
            var run = o as ClassifiedTextRun;
            if (run != null) { sb.Append(run.Text); return; }
            var text = o as ClassifiedTextElement;
            if (text != null) { foreach (var r in text.Runs) sb.Append(r.Text); sb.Append('\n'); return; }
            var container = o as ContainerElement;
            if (container != null) { foreach (var e in container.Elements) Walk(e, sb); return; }
            sb.Append(o.ToString()).Append('\n');
        }
    }
}

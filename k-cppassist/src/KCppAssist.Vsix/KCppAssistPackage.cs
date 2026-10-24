using System;
using System.Collections;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading;
using System.Windows;
using System.Windows.Controls;
using EnvDTE;
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

namespace KCppAssist
{
    /// <summary>
    /// 宣言していない変数への代入に、型を付ける。
    /// Alt+Q はローカル変数(その場に型を足す)、Alt+W はクラスのメンバー変数(ヘッダーに足す)。
    /// </summary>
    [PackageRegistration(UseManagedResourcesOnly = true, AllowsBackgroundLoading = true)]
    [InstalledProductRegistration("K-CppAssist", "宣言していない変数に型を付ける", "0.5.0")]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [ProvideOptionPage(typeof(OptionsPage), "K-CppAssist", "全般", 0, 0, true)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.SolutionExists_string, PackageAutoLoadFlags.BackgroundLoad)]
    [Guid(PackageGuid)]
    public sealed class KCppAssistPackage : AsyncPackage
    {
        public const string PackageGuid = "b2f6c1a8-3d47-4e09-9a5c-81e7d0f4b362";
        internal const string CmdSetGuid = "e5a93d17-0c82-4b6f-a1d4-6f27b8c30e95";
        private static readonly Guid CmdSet = new Guid(CmdSetGuid);
        internal const int CmdLocal = 0x0100;
        internal const int CmdMember = 0x0101;
        internal const int CmdAccessor = 0x0102;
        private const int CmdSettings = 0x0103;

        internal static void Log(string text)
        {
            try
            {
                string dir = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData), "K-CppAssist");
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
                commands.AddCommand(new MenuCommand((s, e) => RunAccessor(), new CommandID(CmdSet, CmdAccessor)));
                commands.AddCommand(new MenuCommand((s, e) => ShowOptionPage(typeof(OptionsPage)), new CommandID(CmdSet, CmdSettings)));
            }
            Log("package initialized");
        }

        private void Run(bool member)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunAsync(member); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        private async Task ReportAsync(string message, bool failed)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            Log((failed ? "FAIL " : "OK ") + message);
            var bar = await GetServiceAsync(typeof(SVsStatusbar)) as IVsStatusbar;
            if (bar != null) bar.SetText("K-CppAssist: " + message);
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
            if (view == null) { await ReportAsync("アクティブなエディターがありません", true); return; }

            ITextSnapshot snap = view.TextSnapshot;
            SnapshotPoint caret = view.Caret.Position.BufferPosition;
            ITextSnapshotLine line = caret.GetContainingLine();
            string text = line.GetText();

            // カーソルが行のどこにあっても、行頭の「name = 右辺;」(this-> は付いていてもよい)を対象にする
            var assign = Regex.Match(text, @"^\s*(this\s*->\s*)?([A-Za-z_]\w*)\s*=(?!=)\s*(.*?)\s*;?\s*$");
            if (!assign.Success || assign.Groups[3].Length == 0)
            { await ReportAsync("この行は「名前 = 右辺;」の形ではありません", true); return; }
            string name = assign.Groups[2].Value;
            int nameStart = assign.Groups[2].Index;
            string rhs = assign.Groups[3].Value;
            int rhsStart = assign.Groups[3].Index;
            if (!member && assign.Groups[1].Success) { await ReportAsync("this-> の付いた代入は、ローカル変数にできません", true); return; }

            string className = null;
            if (member)
            {
                className = CppScan.EnclosingClass(snap.GetText(), caret.Position);
                if (className == null) { await ReportAsync("Class::Func の形のメンバー関数の中ではありません", true); return; }
            }

            // 型を決める。式 → Quick Info → 聞く の順
            // 「cond ? A : B」なら、枝を 1 つずつ試す。{} や nullptr の枝は型が決まらないので飛ばす
            string type = null;
            string how = "式";
            var candidates = TypeInference.TernaryBranches(rhs) ?? new List<KeyValuePair<string, int>> { new KeyValuePair<string, int>(rhs, 0) };
            foreach (var cand in candidates)
            {
                if (Regex.IsMatch(cand.Key, @"^(\{.*\}|nullptr|NULL)$")) continue;
                type = TypeInference.FromExpression(cand.Key);
                how = "式";
                if (type == null)
                {
                    type = await FromQuickInfoAsync(view, broker, snap, line.Start.Position + rhsStart + cand.Value, cand.Key);
                    how = "Quick Info";
                }
                if (type != null) break;
            }
            if (type == null)
            {
                if (!member) { type = "auto"; how = "auto"; }
                else
                {
                    type = Ask("型を決められませんでした。" + name + " の型を入力してください。", "");
                    how = "入力";
                    if (string.IsNullOrWhiteSpace(type)) { await ReportAsync("型を決められませんでした (右辺: " + rhs + ")", true); return; }
                    type = type.Trim();
                }
            }
            Log("mode=" + (member ? "member" : "local") + " name=" + name + " rhs=" + rhs + " type=" + type + " by=" + how);

            if (!member)
            {
                // 行頭の識別子の前に型を足す。1 回の編集なので、Undo も 1 回
                int pos = line.Start.Position + nameStart;
                view.TextBuffer.Insert(pos, type + " ");
                await ReportAsync(type + " " + name + " にしました (" + how + ")", false);
                return;
            }

            await AddMemberAsync(view, className, type + " " + name + ";", type, name, how);
        }

        // ---- メンバー変数 ----

        private async Task AddMemberAsync(IWpfTextView cppView, string className, string declaration, string type, string name, string how)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var dte = (DTE)await GetServiceAsync(typeof(DTE));
            string cppPath = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            string root = SolutionDir(dte, cppPath);
            string header = FindHeader(root, cppPath, className);
            if (header == null) { await ReportAsync("クラス " + className + " の宣言 (.h) が見つかりません", true); return; }

            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();

            IVsUIHierarchy hier; uint itemId; IVsWindowFrame frame;
            Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, header, Guid.Empty, out hier, out itemId, out frame);
            IVsTextView hv = frame == null ? null : Microsoft.VisualStudio.Shell.VsShellUtilities.GetTextView(frame);
            IWpfTextView view = hv == null ? null : adapters.GetWpfTextView(hv);
            if (view == null) { await ReportAsync(Path.GetFileName(header) + " を開けませんでした", true); return; }

            ITextSnapshot snap = view.TextSnapshot;
            string all = snap.GetText();
            if (Regex.IsMatch(all, @"\b" + Regex.Escape(name) + @"\b"))
            {
                // 同じ名前が宣言の中にすでにあるかもしれない。クラスの本文だけで確かめるのは難しいので、断る
                if (Regex.IsMatch(all, @"[\w>*&]\s+\*?&?" + Regex.Escape(name) + @"\s*(;|=|\{)"))
                { await ReportAsync(name + " は " + Path.GetFileName(header) + " にすでにあります", true); return; }
            }
            string eol = all.Contains("\r\n") ? "\r\n" : "\n";
            var edit = HeaderEditor.Plan(all, className, declaration, eol);
            if (edit == null) { await ReportAsync(Path.GetFileName(header) + " の中でクラス " + className + " の本体を読めませんでした", true); return; }

            view.TextBuffer.Insert(edit.Position, edit.Text);
            // 作業していた cpp に戻る
            if (cppPath != null)
            {
                try { Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, cppPath, Guid.Empty, out hier, out itemId, out frame); }
                catch (Exception) { }
            }
            await ReportAsync(declaration + " を " + Path.GetFileName(header) + " に追加しました (" + how + ")", false);
        }

        // ---- ゲッター・セッター ----

        private void RunAccessor()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunAccessorAsync(); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        /// <summary>
        /// ヘッダーの宣言行(UINT stride_;)か、cpp の代入行(stride_ = ...;)にカーソルがあれば、
        /// そのメンバー変数の GetStride / SetStride を、クラスの public: の末尾に足す。
        /// </summary>
        private async Task RunAccessorAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync("アクティブなエディターがありません", true); return; }

            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            string ext = path == null ? "" : Path.GetExtension(path).ToLowerInvariant();
            bool inHeader = ext == ".h" || ext == ".hpp" || ext == ".hh" || ext == ".hxx";

            ITextSnapshot snap = view.TextSnapshot;
            SnapshotPoint caret = view.Caret.Position.BufferPosition;
            ITextSnapshotLine line = caret.GetContainingLine();
            string lineText = line.GetText();

            string member;
            string className;
            IWpfTextView target;      // 編集するヘッダーのビュー
            if (inHeader)
            {
                member = AccessorEditor.NameFromDeclarationLine(lineText);
                if (member == null) { await ReportAsync("この行はメンバー変数の宣言ではありません", true); return; }
                var span = AccessorEditor.ClassAt(snap.GetText(), caret.Position);
                if (span == null) { await ReportAsync("この行は、クラスの中ではありません", true); return; }
                className = span.Name;
                target = view;
            }
            else
            {
                var assign = Regex.Match(lineText, @"^\s*(?:this\s*->\s*)?([A-Za-z_]\w*)\s*=(?!=)");
                if (!assign.Success) { await ReportAsync("この行は「名前 = 右辺;」の形ではありません", true); return; }
                member = assign.Groups[1].Value;
                className = CppScan.EnclosingClass(snap.GetText(), caret.Position);
                if (className == null) { await ReportAsync("Class::Func の形のメンバー関数の中ではありません", true); return; }
                string header = FindHeader(SolutionDir(dte, path), path, className);
                if (header == null) { await ReportAsync("クラス " + className + " の宣言 (.h) が見つかりません", true); return; }
                IVsUIHierarchy hier; uint itemId; IVsWindowFrame frame;
                Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, header, Guid.Empty, out hier, out itemId, out frame);
                IVsTextView hv = frame == null ? null : Microsoft.VisualStudio.Shell.VsShellUtilities.GetTextView(frame);
                target = hv == null ? null : adapters.GetWpfTextView(hv);
                if (target == null) { await ReportAsync(Path.GetFileName(header) + " を開けませんでした", true); return; }
            }

            string all = target.TextSnapshot.GetText();
            var cls = AccessorEditor.Find(all, className);
            if (cls == null) { await ReportAsync("クラス " + className + " の本体を読めませんでした", true); return; }
            bool readOnly;
            string type = AccessorEditor.FindMemberType(all, cls, member, out readOnly);
            if (type == null) { await ReportAsync(className + " の中に、" + member + " の宣言が見つかりません (配列と static は未対応)", true); return; }

            var skipped = new List<string>();
            var page = (OptionsPage)GetDialogPage(typeof(OptionsPage));
            string refused;
            var lines = AccessorEditor.MakeLines(all, cls, member, type, readOnly, page.BlankLineBetweenAccessors, skipped, out refused);
            if (lines == null) { await ReportAsync(refused, true); return; }
            if (lines.Count == 0) { await ReportAsync(string.Join("、", skipped) + " はすでにあります", true); return; }
            string eol = all.Contains("\r\n") ? "\r\n" : "\n";
            var edit = AccessorEditor.PlanPublic(all, cls, lines, eol, page.BlankLineBetweenAccessors);
            target.TextBuffer.Insert(edit.Position, edit.Text);

            if (!inHeader && path != null)
            {
                IVsUIHierarchy h2; uint i2; IVsWindowFrame f2;
                try { Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, path, Guid.Empty, out h2, out i2, out f2); }
                catch (Exception) { }
            }
            await ReportAsync(string.Join(" / ", lines.Where(l => l.Length > 0).Select(l => l.Substring(0, l.IndexOf('{')).Trim())) + " を追加しました", false);
        }

        /// <summary>
        /// ヘッダーを探す。cpp と同じ名前の .h を優先し、なければ「class クラス名」を含む .h を探す。
        /// 探す範囲はソリューションのフォルダー(なければ cpp のあるフォルダー)の下。
        /// </summary>
        private static string FindHeader(string root, string cppPath, string className)
        {
            var skip = new HashSet<string>(StringComparer.OrdinalIgnoreCase) { ".git", ".vs", "bin", "obj", "x64", "Debug", "Release", "vcpkg_installed", "node_modules", "packages" };
            var headers = new List<string>();
            var stack = new Stack<string>();
            stack.Push(root);
            while (stack.Count > 0 && headers.Count < 20000)
            {
                string dir = stack.Pop();
                try
                {
                    foreach (string f in Directory.GetFiles(dir))
                    {
                        string ext = Path.GetExtension(f).ToLowerInvariant();
                        if (ext == ".h" || ext == ".hpp" || ext == ".hh" || ext == ".hxx" || ext == ".ixx") headers.Add(f);
                    }
                    foreach (string d in Directory.GetDirectories(dir))
                        if (!skip.Contains(Path.GetFileName(d))) stack.Push(d);
                }
                catch (Exception) { }
            }
            var re = new Regex(@"\b(class|struct)\s+(?:[A-Za-z_]\w*\s+)*?" + Regex.Escape(className) + @"\b[^;{]*\{");
            string stem = cppPath == null ? "" : Path.GetFileNameWithoutExtension(cppPath);
            foreach (string h in headers.OrderBy(h => string.Equals(Path.GetFileNameWithoutExtension(h), stem, StringComparison.OrdinalIgnoreCase) ? 0 : 1))
            {
                try { if (re.IsMatch(File.ReadAllText(h))) return h; }
                catch (Exception) { }
            }
            return null;
        }

        private static string SolutionDir(DTE dte, string cppPath)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                string sln = dte.Solution.FullName;
                if (!string.IsNullOrEmpty(sln)) return Path.GetDirectoryName(sln);
            }
            catch (Exception) { }
            return cppPath == null ? "" : Path.GetDirectoryName(cppPath);
        }

        /// <summary>カーソルの行から上へ、「Class::Func(」の関数の定義を探して、Class を返す。</summary>
        private static string EnclosingClass(ITextSnapshot snap, int lineNumber)
        {
            var re = new Regex(@"(?<![\w:])(?:[A-Za-z_]\w*(?:<[^<>]*>)?::)*([A-Za-z_]\w*(?:<[^<>]*>)?)::~?[A-Za-z_]\w*\s*\(");
            for (int n = lineNumber; n >= 0 && n > lineNumber - 300; n--)
            {
                string t = snap.GetLineFromLineNumber(n).GetText();
                // 字下げのない行(関数の頭)か、namespace の中の字下げ 0 の行だけを見る
                if (t.Length == 0 || char.IsWhiteSpace(t[0]) || t[0] == '}' || t[0] == '/') continue;
                var m = re.Match(t);
                if (m.Success) return Regex.Replace(m.Groups[1].Value, @"<.*>", "");
            }
            return null;
        }

        // ---- Quick Info ----

        private async System.Threading.Tasks.Task<string> FromQuickInfoAsync(IWpfTextView view, IAsyncQuickInfoBroker broker, ITextSnapshot snap, int rhsStartAbs, string rhs)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            // 右辺が「最初の ( の閉じ括弧で終わる」呼び出しなら関数、そうでなければ最後の識別子を調べる
            int paren = rhs.IndexOf('(');
            bool isCall = paren > 0 && MatchingParen(rhs, paren) == rhs.Length - 1 && Regex.IsMatch(rhs.Substring(0, paren), @"^[\w:<>\.\->\s\[\]]*\w\s*$");
            string target;
            int pos;
            if (isCall)
            {
                string before = rhs.Substring(0, paren).TrimEnd();
                var id = Regex.Match(before, @"(\w+)$");
                target = id.Value;
                pos = rhsStartAbs + id.Index + id.Length - 1;
            }
            else if (Regex.IsMatch(rhs, @"^[\w:\.\->]+$"))
            {
                var id = Regex.Match(rhs, @"(\w+)$");
                target = id.Value;
                pos = rhsStartAbs + id.Index + id.Length - 1;
            }
            else return null;

            var tp = snap.CreateTrackingPoint(pos, PointTrackingMode.Positive);
            IAsyncQuickInfoSession session = await broker.TriggerQuickInfoAsync(view, tp, QuickInfoSessionOptions.None);
            string info = session == null ? "" : Flatten(session.Content);
            if (session != null) await session.DismissAsync();
            Log("quickinfo(" + target + "): " + info.Replace("\n", " | "));
            return isCall ? TypeInference.FromFunctionInfo(info, target) : TypeInference.FromVariableInfo(info, target);
        }

        private static int MatchingParen(string s, int open)
        {
            int depth = 0;
            for (int i = open; i < s.Length; i++)
            {
                if (s[i] == '(') depth++;
                else if (s[i] == ')') { depth--; if (depth == 0) return i; }
            }
            return -1;
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

        /// <summary>Quick Info の内容(入れ子のリスト・ContainerElement)を、文字だけの 1 本にする。</summary>
        private static string Flatten(object content)
        {
            var sb = new StringBuilder();
            Walk(content, sb);
            // Quick Info の文字には、ゼロ幅の文字(U+200B など)が混ざっている
            return Regex.Replace(sb.ToString(), "[​-‏⁠﻿]", "");
        }

        private static void Walk(object o, StringBuilder sb)
        {
            if (o == null) return;
            var str = o as string;
            if (str != null) { sb.Append(str).Append('\n'); return; }
            var run = o as ClassifiedTextRun;
            if (run != null) { sb.Append(run.Text); return; }
            var text = o as ClassifiedTextElement;
            if (text != null) { foreach (var r in text.Runs) sb.Append(r.Text); sb.Append('\n'); return; }
            var container = o as ContainerElement;
            if (container != null) { foreach (var e in container.Elements) Walk(e, sb); return; }
            var list = o as IEnumerable;
            if (list != null) { foreach (var e in list) Walk(e, sb); return; }
            sb.Append("<" + o.GetType().Name + ">\n");
        }

        // ---- 型の入力欄 ----

        private static string Ask(string message, string initial)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            string result = null;
            var box = new TextBox { Text = initial, Margin = new Thickness(0, 8, 0, 8), MinWidth = 320 };
            var ok = new Button { Content = "OK", IsDefault = true, Width = 80, HorizontalAlignment = HorizontalAlignment.Right };
            var panel = new StackPanel { Margin = new Thickness(12) };
            panel.Children.Add(new TextBlock { Text = message, TextWrapping = TextWrapping.Wrap, MaxWidth = 360 });
            panel.Children.Add(box);
            panel.Children.Add(ok);
            var w = new System.Windows.Window
            {
                Title = "K-CppAssist",
                Content = panel,
                SizeToContent = SizeToContent.WidthAndHeight,
                WindowStartupLocation = WindowStartupLocation.CenterScreen,
                ResizeMode = ResizeMode.NoResize,
                Topmost = true,
            };
            ok.Click += (s, e) => { result = box.Text; w.Close(); };
            w.Loaded += (s, e) => box.Focus();
            w.ShowDialog();
            return result;
        }
    }
}

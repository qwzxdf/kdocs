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
    [InstalledProductRegistration("K-CppAssist", "宣言していない変数に型を付ける", "0.7.0")]
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
        internal const int CmdInclude = 0x0104;
        internal const int CmdSync = 0x0105;

        internal static KCppAssistPackage Instance { get; private set; }

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
            Instance = this;
            var commands = await GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            if (commands != null)
            {
                commands.AddCommand(new MenuCommand((s, e) => Run(false), new CommandID(CmdSet, CmdLocal)));
                commands.AddCommand(new MenuCommand((s, e) => Run(true), new CommandID(CmdSet, CmdMember)));
                commands.AddCommand(new MenuCommand((s, e) => RunAccessor(), new CommandID(CmdSet, CmdAccessor)));
                commands.AddCommand(new MenuCommand((s, e) => RunInclude(), new CommandID(CmdSet, CmdInclude)));
                commands.AddCommand(new MenuCommand((s, e) => RunSync(), new CommandID(CmdSet, CmdSync)));
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
            string allText = snap.GetText();

            // カーソルのある文が「名前 = 右辺;」の形なら対象にする。右辺が複数行でも、ラムダの中の 1 文でもよい
            var assign = AssignScan.Find(allText, caret.Position);
            if (assign == null)
            { await ReportAsync("この文は「名前 = 右辺;」の形ではありません", true); return; }
            string name = assign.Name;
            string rhs = assign.Rhs;
            if (!member && assign.HasThis) { await ReportAsync("this-> の付いた代入は、ローカル変数にできません", true); return; }

            ClassRef classRef = null;
            if (member)
            {
                classRef = CppScan.EnclosingClassRef(allText, caret.Position);
                if (classRef == null) { await ReportAsync("メンバー関数の中ではありません (Class::Func の形の定義か、クラスの中に書いた関数が対象です)", true); return; }
            }

            // 型を決める。式 → Quick Info → 式の組み合わせ → 聞く の順
            var inferred = await InferAsync(view, broker, snap, rhs, assign.RhsStart, 0);
            string type = inferred.Key;
            string how = inferred.Value;
            if (type == null)
            {
                if (!member) { type = "auto"; how = "auto"; }
                else
                {
                    type = Ask("型を決められませんでした。" + name + " の型を入力してください。", "");
                    how = "入力";
                    if (string.IsNullOrWhiteSpace(type)) { await ReportAsync("型を決められませんでした (右辺: " + Regex.Replace(rhs, @"\s+", " ") + ")", true); return; }
                    type = type.Trim();
                }
            }
            Log("mode=" + (member ? "member" : "local") + " name=" + name + " rhs=" + Regex.Replace(rhs, @"\s+", " ") + " type=" + type + " by=" + how);

            if (!member)
            {
                // 文の頭の識別子の前に型を足す。1 回の編集なので、Undo も 1 回
                view.TextBuffer.Insert(assign.NameStart, type + " ");
                await ReportAsync(type + " " + name + " にしました (" + how + ")", false);
                return;
            }

            await AddMemberAsync(view, classRef, type + " " + name + ";", type, name, how);
        }

        /// <summary>
        /// 右辺 expr(snap の abs から始まる)の型を決める。式そのもの → Quick Info → 演算子を含む式は部分の型から組み立てる。
        /// 「cond ? A : B」は、枝を 1 つずつ試す({} と nullptr の枝は型がないので飛ばす)。型は Key、決め方は Value。決められなければ Key が null。
        /// </summary>
        private async System.Threading.Tasks.Task<KeyValuePair<string, string>> InferAsync(IWpfTextView view, IAsyncQuickInfoBroker broker, ITextSnapshot snap, string expr, int abs, int depth)
        {
            var none = new KeyValuePair<string, string>(null, "式");
            if (depth > 8) return none;
            int off;
            string e = ExprType.StripParens(expr, out off);
            abs += off;
            if (e.Length == 0 || Regex.IsMatch(e, @"^(\{.*\}|nullptr|NULL)$", RegexOptions.Singleline)) return none;

            var branches = TypeInference.TernaryBranches(e);
            if (branches != null)
            {
                foreach (var b in branches)
                {
                    var r = await InferAsync(view, broker, snap, b.Key, abs + b.Value, depth + 1);
                    if (r.Key != null) return r;
                }
                return none;
            }

            string flat = Regex.Replace(e, @"\s+", " ");
            var bin = ExprType.SplitBinary(e);
            if (bin != null)
            {
                var types = new List<string>();
                foreach (var o in bin.Operands)
                    types.Add((await InferAsync(view, broker, snap, o.Key, abs + o.Value, depth + 1)).Key);
                string result = ExprType.BinaryResult(bin, types);
                if (result != null) return new KeyValuePair<string, string>(result, "式の組み合わせ");
                return none;
            }

            string t = TypeInference.FromExpression(flat);
            if (t != null) return new KeyValuePair<string, string>(t, "式");

            t = await FromQuickInfoAsync(view, broker, snap, abs, e);
            if (t != null) return new KeyValuePair<string, string>(t, "Quick Info");

            string op; int uo;
            string operand = ExprType.Unary(e, out op, out uo);
            if (operand != null)
            {
                if (op == "!") return new KeyValuePair<string, string>("bool", "式の組み合わせ");
                var inner = await InferAsync(view, broker, snap, operand, abs + uo, depth + 1);
                t = ExprType.UnaryResult(op, inner.Key);
                if (t != null) return new KeyValuePair<string, string>(t, "式の組み合わせ");
            }

            t = ExprType.CastType(e);
            if (t != null) return new KeyValuePair<string, string>(t, "キャスト");
            return none;
        }

        // ---- メンバー変数 ----

        private async Task AddMemberAsync(IWpfTextView cppView, ClassRef classRef, string declaration, string type, string name, string how)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var dte = (DTE)await GetServiceAsync(typeof(DTE));
            string cppPath = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;

            var loc = await LocateClassAsync(dte, cppPath, cppView, classRef);
            if (loc == null) return;

            string all = loc.Text;
            string body = all.Substring(loc.Scope.Open, loc.Scope.Close - loc.Scope.Open);
            if (Regex.IsMatch(body, @"[\w>*&]\s+\*?&?" + Regex.Escape(name) + @"\s*(;|=|\{)"))
            { await ReportAsync(name + " は " + Path.GetFileName(loc.File) + " の " + classRef.Name + " にすでにあります", true); return; }

            string eol = all.Contains("\r\n") ? "\r\n" : "\n";
            var edit = HeaderEditor.PlanAt(all, loc.Scope.Open, declaration, eol);
            if (edit == null) { await ReportAsync(Path.GetFileName(loc.File) + " の中でクラス " + classRef.Name + " の本体を読めませんでした", true); return; }

            loc.View.TextBuffer.Insert(edit.Position, edit.Text);
            ReturnTo(cppPath, loc.File);
            await ReportAsync(declaration + " を " + Path.GetFileName(loc.File) + " に追加しました (" + how + ")", false);
        }

        /// <summary>開いたファイルから、作業中のファイルへ戻る(同じファイルなら何もしない)。</summary>
        private void ReturnTo(string workPath, string openedPath)
        {
            if (workPath == null || string.Equals(workPath, openedPath, StringComparison.OrdinalIgnoreCase)) return;
            try
            {
                IVsUIHierarchy hier; uint itemId; IVsWindowFrame frame;
                Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, workPath, Guid.Empty, out hier, out itemId, out frame);
            }
            catch (Exception) { }
        }

        private sealed class Located
        {
            public IWpfTextView View;       // クラスのあるファイルのエディター
            public Scopes.Scope Scope;      // そのファイルの文字(Text)の中での、クラスの範囲
            public string Text;
            public string File;
        }

        private sealed class ClassSite
        {
            public string File;
            public string Chain;            // 名前空間とクラスの並び(「game::Outer::Inner」)
            public int Score;
            public bool SameStem;
        }

        /// <summary>
        /// cpp の関数が属するクラスの定義を探して、そのファイルを開く。クラスがいまのファイルの中にあれば、そのまま使う。
        /// 修飾(Outer::Inner)と cpp を囲む namespace に合うものを選び、同点が複数あれば選ぶ欄を出す。
        /// </summary>
        private async System.Threading.Tasks.Task<Located> LocateClassAsync(DTE dte, string cppPath, IWpfTextView cppView, ClassRef r)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            string curText = cppView.TextSnapshot.GetText();

            string file, chain = null;
            if (r.InFileOpen >= 0) file = cppPath;
            else
            {
                string root = SolutionDir(dte, cppPath);
                var sites = await System.Threading.Tasks.Task.Run(() => FindClassSites(root, cppPath, curText, r));
                await JoinableTaskFactory.SwitchToMainThreadAsync();
                if (sites.Count == 0) { await ReportAsync("クラス " + r.Qualified + " の宣言 (.h) が見つかりません", true); return null; }
                int top = sites.Max(s => s.Score);
                var best = sites.Where(s => s.Score == top).ToList();
                ClassSite pick = best[0];
                if (best.Count > 1)
                {
                    var names = new Dictionary<string, ClassSite>();
                    foreach (var s in best) names[s.Chain + "  —  " + s.File] = s;
                    string choice = Choose(r.Name + " の宣言が複数あります。足し先のクラスを選んでください。", names.Keys.ToList());
                    if (choice == null) { await ReportAsync("やめました", true); return null; }
                    pick = names[choice];
                }
                file = pick.File;
                chain = pick.Chain;
            }

            IWpfTextView view = cppView;
            if (cppPath == null || !string.Equals(file, cppPath, StringComparison.OrdinalIgnoreCase))
            {
                IVsUIHierarchy hier; uint itemId; IVsWindowFrame frame;
                Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, file, Guid.Empty, out hier, out itemId, out frame);
                IVsTextView hv = frame == null ? null : Microsoft.VisualStudio.Shell.VsShellUtilities.GetTextView(frame);
                view = hv == null ? null : adapters.GetWpfTextView(hv);
                if (view == null) { await ReportAsync(Path.GetFileName(file) + " を開けませんでした", true); return null; }
            }

            // 開いたあとの文字(保存前の編集を含む)で、クラスの範囲を取り直す
            string live = view.TextSnapshot.GetText();
            var scopes = Scopes.Parse(live).Where(s => s.IsClass).ToList();
            Scopes.Scope scope = r.InFileOpen >= 0
                ? scopes.FirstOrDefault(s => s.Open == r.InFileOpen)
                : scopes.FirstOrDefault(s => string.Join("::", s.Chain()) == chain);
            if (scope == null) { await ReportAsync("クラス " + r.Qualified + " の本体を読めませんでした", true); return null; }
            return new Located { View = view, Scope = scope, Text = live, File = file };
        }

        // ---- #include ----

        private void RunInclude()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunIncludeAsync(); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        /// <summary>カーソルの識別子(std::vector、ComPtr、Camera など)を宣言したヘッダーを探して、#include を足す。</summary>
        private async Task RunIncludeAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var opt = IncludeService.Options;
            if (opt.IncludeMode == IncludeMode.Off) { await ReportAsync("#include の機能は、設定で Off になっています", true); return; }

            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync("アクティブなエディターがありません", true); return; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null) { await ReportAsync("ファイルを開いていません", true); return; }

            string text = view.TextSnapshot.GetText();
            string masked = CppText.Mask(text);
            int pos = view.Caret.Position.BufferPosition.Position;
            int a = pos, b = pos;
            while (a > 0 && IsId(masked[a - 1])) a--;
            while (b < masked.Length && IsId(masked[b])) b++;
            if (b <= a) { await ReportAsync("カーソルの位置に識別子がありません (コメントや文字列の中かもしれません)", true); return; }

            int chainStart;
            string chain = CppText.Chain(masked, a, b, out chainStart);
            if (chain == null) { await ReportAsync("名前を読めませんでした", true); return; }

            string root = IncludeService.RootFor(path);
            var skip = IncludeService.SkipDirs(opt);
            await Task.Run(() => IncludeService.Index.Refresh(root, skip, true));
            await JoinableTaskFactory.SwitchToMainThreadAsync();

            var res = IncludeService.Resolve(chain, path, root, opt, true);
            if (res == null) { await ReportAsync(chain + " を宣言したヘッダーが見つかりません", true); return; }

            string token = res.Token;
            string file = res.File;
            if (token == null)
            {
                var items = res.Choices.Keys.OrderBy(k => k, StringComparer.OrdinalIgnoreCase).ToList();
                token = Choose(chain + " の宣言が複数あります。足すヘッダーを選んでください。", items);
                if (token == null) { await ReportAsync("やめました", true); return; }
                res.Choices.TryGetValue(token, out file);
            }
            if (IncludeService.WouldCycle(file, path)) { await ReportAsync(token + " は、このヘッダーを #include しているので、足すと循環します", true); return; }

            string eol = text.Contains("\r\n") ? "\r\n" : "\n";
            string stem = IncludeService.IsHeader(path) ? null : Path.GetFileNameWithoutExtension(path);
            var edit = IncludeEditor.Plan(text, token, stem, eol);
            if (edit == null) { await ReportAsync(token + " はすでに #include されています", true); return; }

            IncludeService.Apply(view.TextBuffer, edit.Position, edit.Text, undo, "K-CppAssist: #include を追加");
            await ReportAsync(chain + " のために " + token + " を追加しました (" + res.Source + ")", false);
        }

        // ---- 宣言と定義の引数を合わせる ----

        private void RunSync()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunSyncAsync(); }
                catch (Exception ex) { await ReportAsync("例外: " + ex.Message, true); Log(ex.ToString()); }
            });
        }

        /// <summary>
        /// カーソルのある関数(ヘッダーの宣言、または cpp の定義)の引数を、相手の定義(宣言)に写す。
        /// 開いていなければ開く。引数が違うものが複数あれば、選ぶ。
        /// </summary>
        private async Task RunSyncAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var opt = SyncService.Options;
            if (opt.SyncMode == SyncMode.Off) { await ReportAsync("引数の同期は、設定で Off になっています", true); return; }

            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync("アクティブなエディターがありません", true); return; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null) { await ReportAsync("ファイルを開いていません", true); return; }

            string text = view.TextSnapshot.GetText();
            int caret = view.Caret.Position.BufferPosition.Position;
            ITextSnapshotLine line = view.Caret.Position.BufferPosition.GetContainingLine();
            var sig = FunctionScan.Scan(text).FirstOrDefault(s => (caret >= s.Open && caret <= s.Close + 1) || (s.Open >= line.Start.Position && s.Open <= line.End.Position));
            if (sig == null) { await ReportAsync("カーソルの行に、関数の宣言か定義が見つかりません", true); return; }
            if (sig.HasBody && sig.InClass) { await ReportAsync("クラスの中に本体のある関数には、相手がありません", true); return; }

            var thisList = SignatureSync.SplitParams(sig.Inner(text));
            if (thisList == null) { await ReportAsync("引数を読めませんでした (書きかけかもしれません)", true); return; }
            bool wantDef = !sig.HasBody;
            string label = (sig.Class == null ? "" : sig.Class + "::") + sig.Name;

            string root = IncludeService.RootFor(path);
            var skip = IncludeService.SkipDirs(opt);
            List<string> files = await Task.Run(() =>
            {
                if (!wantDef) IncludeService.Index.Refresh(root, skip, true);
                return SyncService.Candidates(path, sig.Class, root, wantDef, opt);
            });
            await JoinableTaskFactory.SwitchToMainThreadAsync();

            var thisKeys = SignatureSync.TypeKeys(thisList);
            var targets = SyncService.FindTargets(files, wantDef, sig.Class, sig.Name, adapters)
                .Where(t => !(string.Equals(t.File, path, StringComparison.OrdinalIgnoreCase) && t.Sig.Open == sig.Open))
                .ToList();
            if (targets.Count == 0) { await ReportAsync(label + " の" + (wantDef ? "定義" : "宣言") + "が見つかりません", true); return; }

            Func<SyncService.Target, List<string>> keysOf = t => { var l = SignatureSync.SplitParams(t.Inner); return l == null ? null : SignatureSync.TypeKeys(l); };
            if (targets.Any(t => SyncService.SameKeys(keysOf(t), thisKeys))) { await ReportAsync(label + " の引数は、すでに合っています", false); return; }

            SyncService.Target target = targets[0];
            if (targets.Count > 1)
            {
                var names = targets.ToDictionary(t => Path.GetFileName(t.File) + ": " + label + "(" + SignatureSync.Norm(t.Inner) + ")" + " #" + t.Sig.Open, t => t);
                string pick = Choose(label + " の" + (wantDef ? "定義" : "宣言") + "が複数あります。引数を写す先を選んでください。", names.Keys.ToList());
                if (pick == null) { await ReportAsync("やめました", true); return; }
                target = names[pick];
            }

            var cpList = SignatureSync.SplitParams(target.Inner);
            if (cpList == null) { await ReportAsync("相手の引数を読めませんでした", true); return; }
            string newInner = SignatureSync.Rebuild(cpList, thisList, cpList, !wantDef, target.Inner);

            ITextBuffer buf = target.Buffer ?? SyncService.OpenForEdit(target.File, adapters);
            if (buf == null) { await ReportAsync(Path.GetFileName(target.File) + " を開けませんでした", true); return; }
            if (buf.CurrentSnapshot.Length != target.Text.Length) { await ReportAsync(Path.GetFileName(target.File) + " が読み込み中に変わりました。もう一度押してください", true); return; }
            SyncService.Replace(buf, target.Sig.Open + 1, target.Sig.Close - target.Sig.Open - 1, newInner, undo, "K-CppAssist: 引数を合わせる");
            SyncPreview.Show(view, Path.GetFileName(target.File), buf.CurrentSnapshot, target.Sig.Open, newInner.Length, target.Inner);

            if (target.Buffer == null)
            {
                IVsUIHierarchy hier; uint id; IVsWindowFrame frame;
                try { Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, path, Guid.Empty, out hier, out id, out frame); }
                catch (Exception) { }
            }
            await ReportAsync(label + " の引数を " + Path.GetFileName(target.File) + " に写しました", false);
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
            string curText = snap.GetText();

            string member = null;
            Located loc = null;
            AccessorEditor.ClassSpan cls = null;
            if (inHeader)
            {
                // ヘッダーのメンバー変数の宣言行にカーソルがあるとき
                member = AccessorEditor.NameFromDeclarationLine(lineText);
                if (member != null)
                {
                    cls = AccessorEditor.ClassAt(curText, caret.Position);
                    if (cls == null) { await ReportAsync("この行は、クラスの中ではありません", true); return; }
                    loc = new Located { View = view, Text = curText, File = path };
                }
            }
            if (member == null)
            {
                // cpp の「名前 = 右辺;」の文(クラスの中に書いた関数や、ラムダの中でもよい)にカーソルがあるとき
                var assign = AssignScan.Find(curText, caret.Position);
                if (assign == null) { await ReportAsync(inHeader ? "この行は、メンバー変数の宣言でも「名前 = 右辺;」の文でもありません" : "この文は「名前 = 右辺;」の形ではありません", true); return; }
                member = assign.Name;
                var cref = CppScan.EnclosingClassRef(curText, caret.Position);
                if (cref == null) { await ReportAsync("メンバー関数の中ではありません (Class::Func の形の定義か、クラスの中に書いた関数が対象です)", true); return; }
                loc = await LocateClassAsync(dte, path, view, cref);
                if (loc == null) return;
                cls = AccessorEditor.All(loc.Text).FirstOrDefault(c => c.Open == loc.Scope.Open) ?? AccessorEditor.Find(loc.Text, cref.Name);
            }
            IWpfTextView target = loc.View;
            string className = cls == null ? "" : cls.Name;

            string all = loc.Text;
            if (cls == null) { await ReportAsync("クラスの本体を読めませんでした", true); return; }
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
        /// クラス r を定義しているクラスを探す。いまのファイルの中にあればそれだけ、なければソリューションのフォルダー
        /// (なければ cpp のあるフォルダー)の下のヘッダー。cpp と同じ名前の .h を先に見て、それに 1 つだけ合えば、ほかは読まない。
        /// 修飾と namespace の合い具合の点を付けて返す。
        /// </summary>
        private static List<ClassSite> FindClassSites(string root, string cppPath, string curText, ClassRef r)
        {
            var sites = new List<ClassSite>();
            var nameRe = new Regex(@"\b(class|struct)\s+(?:[A-Za-z_]\w*\s+)*?" + Regex.Escape(r.Name) + @"\b[^;{]*\{");

            if (cppPath != null && nameRe.IsMatch(curText))
            {
                foreach (var pm in Scopes.Matches(curText, r))
                    sites.Add(new ClassSite { File = cppPath, Chain = string.Join("::", pm.Key.Chain()), Score = pm.Value, SameStem = true });
                if (sites.Count > 0) return sites;
            }

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

            string stem = cppPath == null ? "" : Path.GetFileNameWithoutExtension(cppPath);
            foreach (string h in headers.OrderBy(h => string.Equals(Path.GetFileNameWithoutExtension(h), stem, StringComparison.OrdinalIgnoreCase) ? 0 : 1))
            {
                string t;
                try { t = File.ReadAllText(h); }
                catch (Exception) { continue; }
                if (!nameRe.IsMatch(t)) continue;
                bool same = string.Equals(Path.GetFileNameWithoutExtension(h), stem, StringComparison.OrdinalIgnoreCase);
                int before = sites.Count;
                foreach (var pm in Scopes.Matches(t, r))
                    sites.Add(new ClassSite { File = h, Chain = string.Join("::", pm.Key.Chain()), Score = pm.Value, SameStem = same });
                if (same && before == 0 && sites.Count == 1) break;      // 同じ名前のヘッダーに 1 つだけ合ったら、それで決める
            }
            return sites;
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

        // ---- 選ぶ欄 ----

        private static string Choose(string message, IList<string> items)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            string result = null;
            var list = new ListBox { Margin = new Thickness(0, 8, 0, 8), MinWidth = 360, MaxHeight = 240 };
            foreach (string s in items) list.Items.Add(s);
            list.SelectedIndex = 0;
            var ok = new Button { Content = "OK", IsDefault = true, Width = 80, HorizontalAlignment = HorizontalAlignment.Right };
            var panel = new StackPanel { Margin = new Thickness(12) };
            panel.Children.Add(new TextBlock { Text = message, TextWrapping = TextWrapping.Wrap, MaxWidth = 400 });
            panel.Children.Add(list);
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
            ok.Click += (s, e) => { result = list.SelectedItem as string; w.Close(); };
            list.MouseDoubleClick += (s, e) => { if (list.SelectedItem != null) { result = list.SelectedItem as string; w.Close(); } };
            w.Loaded += (s, e) => list.Focus();
            w.ShowDialog();
            return result;
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

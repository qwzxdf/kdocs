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
    [InstalledProductRegistration("K-CppUltimateAssist", "C++ の宣言・include・引数の同期・ファイル名の同期・呼び出しのチェック・エラーログ・書き換えと生成", "0.32.4")]
    [ProvideMenuResource("Menus.ctmenu", 1)]
    [ProvideOptionPage(typeof(OptionsPage), "K-CppUltimateAssist", "全般", 0, 0, true)]
    [ProvideToolWindow(typeof(KCppAssist.Vcpkg.VcpkgToolWindow), Style = VsDockStyle.Float, Transient = true, Width = 1100, Height = 760)]
    [ProvideToolWindow(typeof(KCppAssist.ErrorLog.ErrorLogToolWindow), Style = VsDockStyle.Tabbed, Window = "34E76E81-EE4A-11D0-AE2E-00A0C90FFFC3")]
    [ProvideAutoLoad(VSConstants.UICONTEXT.SolutionExists_string, PackageAutoLoadFlags.BackgroundLoad)]
    [ProvideAutoLoad(VSConstants.UICONTEXT.NoSolution_string, PackageAutoLoadFlags.BackgroundLoad)]
    [Guid(PackageGuid)]
    public sealed partial class KCppAssistPackage : AsyncPackage
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
        internal const int CmdCreate = 0x0106;
        internal const int CmdMove = 0x0109;

        internal static KCppAssistPackage Instance { get; private set; }

        /// <summary>設定の「ログを残す」。ログは別のスレッドからも書くので、設定の値を、ここに写して持つ。</summary>
        internal static volatile bool LogEnabled = true;

        // メニューの文字(.vsct の ButtonText)。ID → 日本語。表示のときに、いまの言語に訳す
        private static readonly System.Collections.Generic.Dictionary<int, string> MenuTexts = new System.Collections.Generic.Dictionary<int, string>
        {
            [0x010E] = L.T("K-Cpp: 使い方..."),
            [0x010A] = L.T("K-Cpp: #include を整理（プロジェクト全体）"),
            [0x010B] = L.T("K-Cpp: 使っていない #include を消す（プロジェクト全体）"),
            [0x010D] = L.T("K-Cpp: このファイルの #include を整理"),
            [0x010C] = L.T("K-Cpp: #include を前方宣言にする (Forward / Alt+F)"),
            [0x0111] = L.T("K-Cpp: メンバーからコンストラクターを作る (Constructor / Alt+C)"),
            [0x0112] = L.T("K-Cpp: 基底クラスの仮想関数を override する (Override / Alt+O)"),
            [0x0113] = L.T("K-Cpp: 呼び出しから関数を作る (Usage / Alt+U)"),
            [0x0114] = L.T("K-Cpp: ファイルの文字コードをそろえる..."),
            [0x0115] = L.T("K-Cpp: この位置の書き換え・生成の一覧... (eXplore / Alt+X)"),
            [0x0100] = "ローカル変数に型を付ける (Qualify type / Alt+Q)",
            [0x0101] = "メンバー変数として宣言する (Write member / Alt+W)",
            [0x0102] = "Getter・Setter を作る (Getter / Alt+G)",
            [0x0104] = "#include を足す (Include / Alt+I)",
            [0x0105] = "宣言と定義の引数を合わせる (Sync / Alt+S)",
            [0x0106] = "宣言・定義の相手を作る (Resolve / Alt+R)",
            [0x0109] = "関数を ヘッダー ⇄ cpp に移す (Move / Alt+M)",
            [0x0108] = "ファイル名をまとめて変える (Name / Alt+N)",
            [0x0107] = "K-ErrorLog (エラーログ)を開く",
            [0x0103] = L.T("K-Cpp: 設定..."),
            [0x0116] = "K-Cpp: vcpkg パッケージ...",
        };

        /// <summary>メニューの文字を、いまの言語にする。表示のたびに読み直すので、設定で言語を変えると、次に開いたメニューから変わる。</summary>
        private static void ApplyMenuTexts(OleMenuCommandService commands)
        {
            foreach (var kv in MenuTexts)
            {
                var cmd = commands.FindCommand(new CommandID(CmdSet, kv.Key)) as OleMenuCommand;
                if (cmd == null) continue;
                string ja = kv.Value;
                cmd.Text = L.T(ja);
                cmd.BeforeQueryStatus += (s, e) => { var c = s as OleMenuCommand; if (c != null) c.Text = L.T(ja); };
            }
        }

        /// <summary>
        /// 表示する言語を決める。初期値は日本語。初めて起動したとき(設定に言語を保存していないとき)だけ、PC(Windows)の表示言語に合わせて、保存する。
        /// </summary>
        private void InitLanguage()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var page = (OptionsPage)GetDialogPage(typeof(OptionsPage));
                if (!page.LanguageInitialized)
                {
                    page.Language = L.FromCulture(System.Globalization.CultureInfo.InstalledUICulture);
                    page.LanguageInitialized = true;
                    page.SaveSettingsToStorage();
                    Log("language: first run, set to " + page.Language + " (" + System.Globalization.CultureInfo.InstalledUICulture.Name + ")");
                }
                L.Current = page.Language;
            }
            catch (Exception ex) { Log("language init failed: " + ex.Message); }
        }

        internal static void Log(string text)
        {
            if (!LogEnabled) return;
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
            LogEnabled = ((OptionsPage)GetDialogPage(typeof(OptionsPage))).WriteLog;
            InitLanguage();
            bool commonProps = ((OptionsPage)GetDialogPage(typeof(OptionsPage))).CommonPropsPage;
            System.Threading.Tasks.Task.Run(() => CommonProps.Apply(commonProps));
            var commands = await GetServiceAsync(typeof(IMenuCommandService)) as OleMenuCommandService;
            if (commands != null)
            {
                commands.AddCommand(new OleMenuCommand((s, e) => Run(false), new CommandID(CmdSet, CmdLocal)));
                commands.AddCommand(new OleMenuCommand((s, e) => Run(true), new CommandID(CmdSet, CmdMember)));
                commands.AddCommand(new OleMenuCommand((s, e) => RunAccessor(), new CommandID(CmdSet, CmdAccessor)));
                commands.AddCommand(new OleMenuCommand((s, e) => RunInclude(), new CommandID(CmdSet, CmdInclude)));
                commands.AddCommand(new OleMenuCommand((s, e) => RunSync(), new CommandID(CmdSet, CmdSync)));
                commands.AddCommand(new OleMenuCommand((s, e) => ShowWindow(true, true), new CommandID(CmdSet, CmdErrorLog)));
                commands.AddCommand(new OleMenuCommand((s, e) => RunRename(), new CommandID(CmdSet, CmdRename)));
                commands.AddCommand(new OleMenuCommand((s, e) => RunCreate(), new CommandID(CmdSet, CmdCreate)));
                commands.AddCommand(new OleMenuCommand((s, e) => RunMove(), new CommandID(CmdSet, CmdMove)));
                RegisterTidyCommands(commands);
                RegisterGenCommands(commands);
                RegisterRefactorCommands(commands);
                RegisterHelpCommand(commands);
                RegisterVcpkgCommand(commands);
                RegisterEncodingCommand(commands);
                commands.AddCommand(new OleMenuCommand((s, e) => ShowOptionPage(typeof(OptionsPage)), new CommandID(CmdSet, CmdSettings)));
                ApplyMenuTexts(commands);
            }
            try { ((OptionsPage)GetDialogPage(typeof(OptionsPage))).MigrateKeyScopes(); }
            catch (Exception ex) { Log("migrate keys failed: " + ex.Message); }
            try { ((OptionsPage)GetDialogPage(typeof(OptionsPage))).MigrateDefaults(); }
            catch (Exception ex) { Log("migrate defaults failed: " + ex.Message); }
            await InitializeErrorLogAsync();
            await InitializeRenameAsync();
            Log("package initialized");
        }

        internal void Run(bool member)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunAsync(member); }
                catch (Exception ex) { await ReportAsync(L.F("例外: {0}", ex.Message), true); Log(ex.ToString()); }
            });
        }

        private async Task ReportAsync(string message, bool failed)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            Log((failed ? "FAIL " : "OK ") + message);
            if (!failed && !((OptionsPage)GetDialogPage(typeof(OptionsPage))).ShowStatusMessages) return;
            var bar = await GetServiceAsync(typeof(SVsStatusbar)) as IVsStatusbar;
            if (bar != null) bar.SetText("K-Cpp: " + message);
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
            if (view == null) { await ReportAsync(L.T("アクティブなエディターがありません"), true); return; }

            ITextSnapshot snap = view.TextSnapshot;
            SnapshotPoint caret = view.Caret.Position.BufferPosition;
            string allText = snap.GetText();

            // カーソルのある文が「名前 = 右辺;」の形なら対象にする。右辺が複数行でも、ラムダの中の 1 文でもよい
            var assign = AssignScan.Find(allText, caret.Position);
            if (assign == null)
            { await ReportAsync(L.T("この文は「名前 = 右辺;」の形ではありません"), true); return; }
            string name = assign.Name;
            string rhs = assign.Rhs;
            if (!member && assign.HasThis) { await ReportAsync(L.T("this-> の付いた代入は、ローカル変数にできません"), true); return; }

            ClassRef classRef = null;
            if (member)
            {
                classRef = CppScan.EnclosingClassRef(allText, caret.Position);
                if (classRef == null) { await ReportAsync(L.T("メンバー関数の中ではありません (Class::Func の形の定義か、クラスの中に書いた関数が対象です)"), true); return; }
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
                    type = Ask(L.F("型を決められませんでした。{0} の型を入力してください。", name), "");
                    how = "入力";
                    if (string.IsNullOrWhiteSpace(type)) { await ReportAsync(L.F("型を決められませんでした (右辺: {0})", Regex.Replace(rhs, @"\s+", " ")), true); return; }
                    type = type.Trim();
                }
            }
            Log("mode=" + (member ? "member" : "local") + " name=" + name + " rhs=" + Regex.Replace(rhs, @"\s+", " ") + " type=" + type + " by=" + how);

            if (!member)
            {
                // 文の頭の識別子の前に型を足す。1 回の編集なので、Undo も 1 回
                // Quick Info を待つ間に、文字が変わっていることがある。snap の位置を、今の位置へ写してから入れる
                int at = snap.CreateTrackingPoint(assign.NameStart, PointTrackingMode.Positive).GetPosition(view.TextBuffer.CurrentSnapshot);
                view.TextBuffer.Insert(at, type + " ");
                await ReportAsync(L.F("{0} {1} にしました ({2})", type, name, L.T(how)), false);
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
            { await ReportAsync(L.F("{0} は {1} の {2} にすでにあります", name, Path.GetFileName(loc.File), classRef.Name), true); return; }

            string eol = CppText.Eol(all);
            var edit = HeaderEditor.PlanAt(all, loc.Scope.Open, declaration, eol);
            if (edit == null) { await ReportAsync(L.F("{0} の中でクラス {1} の本体を読めませんでした", Path.GetFileName(loc.File), classRef.Name), true); return; }

            loc.View.TextBuffer.Insert(edit.Position, edit.Text);
            ReturnTo(cppPath, loc.File);
            await ReportAsync(L.F("{0} を {1} に追加しました ({2})", declaration, Path.GetFileName(loc.File), L.T(how)), false);
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
                if (sites.Count == 0) { await ReportAsync(L.F("クラス {0} の宣言 (.h) が見つかりません", r.Qualified), true); return null; }
                int top = sites.Max(s => s.Score);
                var best = sites.Where(s => s.Score == top).ToList();
                ClassSite pick = best[0];
                if (best.Count > 1)
                {
                    var names = new Dictionary<string, ClassSite>();
                    foreach (var s in best) names[s.Chain + "  —  " + s.File] = s;
                    string choice = Choose(L.F("{0} の宣言が複数あります。足し先のクラスを選んでください。", r.Name), names.Keys.ToList());
                    if (choice == null) { await ReportAsync(L.T("やめました"), true); return null; }
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
                if (view == null) { await ReportAsync(L.F("{0} を開けませんでした", Path.GetFileName(file)), true); return null; }
            }

            // 開いたあとの文字(保存前の編集を含む)で、クラスの範囲を取り直す
            string live = view.TextSnapshot.GetText();
            var scopes = Scopes.Parse(live).Where(s => s.IsClass).ToList();
            Scopes.Scope scope = r.InFileOpen >= 0
                ? scopes.FirstOrDefault(s => s.Open == r.InFileOpen)
                : scopes.FirstOrDefault(s => string.Join("::", s.Chain()) == chain);
            if (scope == null) { await ReportAsync(L.F("クラス {0} の本体を読めませんでした", r.Qualified), true); return null; }
            return new Located { View = view, Scope = scope, Text = live, File = file };
        }

        // ---- #include ----

        internal void RunInclude()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunIncludeAsync(); }
                catch (Exception ex) { await ReportAsync(L.F("例外: {0}", ex.Message), true); Log(ex.ToString()); }
            });
        }

        /// <summary>カーソルの識別子(std::vector、ComPtr、Camera など)を宣言したヘッダーを探して、#include を足す。</summary>
        private async Task RunIncludeAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var opt = IncludeService.Options;
            if (opt.IncludeMode == IncludeMode.Off) { await ReportAsync(L.T("#include の機能は、設定で Off になっています"), true); return; }

            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync(L.T("アクティブなエディターがありません"), true); return; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null) { await ReportAsync(L.T("ファイルを開いていません"), true); return; }

            string text = view.TextSnapshot.GetText();
            string masked = CppText.Mask(text);
            int pos = view.Caret.Position.BufferPosition.Position;
            int a = pos, b = pos;
            while (a > 0 && CppText.IsId(masked[a - 1])) a--;
            while (b < masked.Length && CppText.IsId(masked[b])) b++;
            if (b <= a) { await ReportAsync(L.T("カーソルの位置に識別子がありません (コメントや文字列の中かもしれません)"), true); return; }

            int chainStart;
            string chain = CppText.Chain(masked, a, b, out chainStart);
            if (chain == null) { await ReportAsync(L.T("名前を読めませんでした"), true); return; }

            string root = IncludeService.RootFor(path);
            var skip = IncludeService.SkipDirs(opt);
            await Task.Run(() => IncludeService.Index.Refresh(root, skip, true));
            await JoinableTaskFactory.SwitchToMainThreadAsync();

            var res = IncludeService.Resolve(chain, path, root, opt, true);
            if (res == null) { await ReportAsync(L.F("{0} を宣言したヘッダーが見つかりません", chain), true); return; }

            string token = res.Token;
            string file = res.File;
            if (token == null)
            {
                var items = res.Choices.Keys.OrderBy(k => k, StringComparer.OrdinalIgnoreCase).ToList();
                token = Choose(L.F("{0} の宣言が複数あります。足すヘッダーを選んでください。", chain), items);
                if (token == null) { await ReportAsync(L.T("やめました"), true); return; }
                res.Choices.TryGetValue(token, out file);
            }
            if (IncludeService.WouldCycle(file, path)) { await ReportAsync(L.F("{0} は、このヘッダーを #include しているので、足すと循環します", token), true); return; }

            string eol = CppText.Eol(text);
            string stem = IncludeService.IsHeader(path) ? null : Path.GetFileNameWithoutExtension(path);
            var edit = IncludeEditor.Plan(text, token, stem, eol);
            if (edit == null) { await ReportAsync(L.F("{0} はすでに #include されています", token), true); return; }

            IncludeService.Apply(view.TextBuffer, edit.Position, edit.Text, undo, L.T("K-Cpp: #include を追加"));
            await ReportAsync(L.F("{0} のために {1} を追加しました ({2})", chain, token, L.T(res.Source)), false);
        }

        // ---- 宣言と定義の引数を合わせる ----

        internal void RunSync()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunSyncAsync(); }
                catch (Exception ex) { await ReportAsync(L.F("例外: {0}", ex.Message), true); Log(ex.ToString()); }
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
            if (opt.SyncMode == SyncMode.Off) { await ReportAsync(L.T("引数の同期は、設定で Off になっています"), true); return; }

            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync(L.T("アクティブなエディターがありません"), true); return; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null) { await ReportAsync(L.T("ファイルを開いていません"), true); return; }

            string text = view.TextSnapshot.GetText();
            int caret = view.Caret.Position.BufferPosition.Position;
            ITextSnapshotLine line = view.Caret.Position.BufferPosition.GetContainingLine();
            var sig = FunctionScan.Scan(text).FirstOrDefault(s => (caret >= s.Open && caret <= s.Close + 1) || (s.Open >= line.Start.Position && s.Open <= line.End.Position));
            if (sig == null) { await ReportAsync(L.T("カーソルの行に、関数の宣言か定義が見つかりません"), true); return; }
            if (sig.HasBody && sig.InClass) { await ReportAsync(L.T("クラスの中に本体のある関数には、相手がありません"), true); return; }

            var thisVariants = SignatureSync.KeyVariants(sig.Inner(text));
            if (thisVariants.Count == 0) { await ReportAsync(L.T("引数を読めませんでした (書きかけかもしれません)"), true); return; }
            bool thisHasIf = SignatureSync.HasDirectives(sig.Inner(text));
            var thisList = thisHasIf ? null : SignatureSync.SplitParams(sig.Inner(text));
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

            var targets = SyncService.FindTargets(files, wantDef, sig, adapters)
                .Where(t => !(string.Equals(t.File, path, StringComparison.OrdinalIgnoreCase) && t.Sig.Open == sig.Open))
                .ToList();
            if (targets.Count > 0) { int top = targets.Max(t => t.Score); targets = targets.Where(t => t.Score == top).ToList(); }
            if (targets.Count == 0) { await ReportAsync(L.F("{0} の{1}が見つかりません", label, (wantDef ? L.T("定義") : L.T("宣言"))), true); return; }

            Func<SyncService.Target, List<List<string>>> keysOf = t => SignatureSync.KeyVariants(t.Inner);
            if (targets.Any(t => SyncPlan.SameKeysAny(keysOf(t), thisVariants))) { await ReportAsync(L.F("{0} の引数は、すでに合っています", label), false); return; }

            SyncService.Target target = targets[0];
            if (targets.Count > 1)
            {
                var names = targets.ToDictionary(t => Path.GetFileName(t.File) + ": " + label + "(" + SignatureSync.Norm(t.Inner) + ")" + " #" + t.Sig.Open, t => t);
                string pick = Choose(L.F("{0} の{1}が複数あります。引数を写す先を選んでください。", label, (wantDef ? L.T("定義") : L.T("宣言"))), names.Keys.ToList());
                if (pick == null) { await ReportAsync(L.T("やめました"), true); return; }
                target = names[pick];
            }

            if (thisHasIf || SignatureSync.HasDirectives(target.Inner))
            { await ReportAsync(L.F("引数の途中に #if があるので、自動では書き換えません。{0} は手で合わせてください", Path.GetFileName(target.File)), true); return; }
            var cpList = SignatureSync.SplitParams(target.Inner);
            if (cpList == null) { await ReportAsync(L.T("相手の引数を読めませんでした"), true); return; }
            string newInner = SignatureSync.Rebuild(cpList, thisList, cpList, !wantDef, target.Inner);

            ITextBuffer buf = target.Buffer ?? SyncService.OpenForEdit(target.File, adapters);
            if (buf == null) { await ReportAsync(L.F("{0} を開けませんでした", Path.GetFileName(target.File)), true); return; }
            if (buf.CurrentSnapshot.Length != target.Text.Length) { await ReportAsync(L.F("{0} が読み込み中に変わりました。もう一度押してください", Path.GetFileName(target.File)), true); return; }
            SyncService.Replace(buf, target.Sig.Open + 1, target.Sig.Close - target.Sig.Open - 1, newInner, undo, L.T("K-Cpp: 引数を合わせる"));
            SyncPreview.Show(view, SyncPreview.NameStart(view.TextSnapshot, sig.Open), Path.GetFileName(target.File), buf.CurrentSnapshot, target.Sig.Open, newInner.Length, target.Inner);

            if (target.Buffer == null)
            {
                IVsUIHierarchy hier; uint id; IVsWindowFrame frame;
                try { Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, path, Guid.Empty, out hier, out id, out frame); }
                catch (Exception) { }
            }
            var writtenList = SignatureSync.SplitParams(newInner);
            string warnText = !wantDef && writtenList != null && SignatureSync.DefaultsOutOfOrder(writtenList) ? L.T("(注意: 既定値のある引数のあとに、既定値のない引数があります)") : "";
            await ReportAsync(L.F("{0} の引数を {1} に写しました{2}", label, Path.GetFileName(target.File), warnText), false);
        }

        // ---- 定義・宣言を作る ----

        internal void RunCreate()
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunCreateAsync(); }
                catch (Exception ex) { await ReportAsync(L.F("例外: {0}", ex.Message), true); Log(ex.ToString()); }
            });
        }

        /// <summary>
        /// ヘッダーの宣言にカーソルがあれば、cpp に定義の雛形を足す。cpp の定義(Class::Func)にカーソルがあれば、ヘッダーのクラスに宣言を足す。
        /// 相手がすでにあれば、何もしない。
        /// </summary>
        private async Task RunCreateAsync()
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var undo = model.GetService<Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync(L.T("アクティブなエディターがありません"), true); return; }
            string path = dte.ActiveDocument != null ? dte.ActiveDocument.FullName : null;
            if (path == null) { await ReportAsync(L.T("ファイルを開いていません"), true); return; }

            string text = view.TextSnapshot.GetText();
            int caret = view.Caret.Position.BufferPosition.Position;
            ITextSnapshotLine line = view.Caret.Position.BufferPosition.GetContainingLine();
            var sig = FunctionScan.Scan(text).FirstOrDefault(s => (caret >= s.NameStart && caret <= s.Close + 1) || (s.Open >= line.Start.Position && s.Open <= line.End.Position));
            if (sig == null) { await ReportAsync(L.T("カーソルの行に、関数の宣言か定義が見つかりません"), true); return; }
            string label = (sig.Class == null ? "" : sig.Class + "::") + sig.Name;

            if (!sig.HasBody) await CreateDefinitionAsync(view, path, text, sig, label, adapters, undo, dte);
            else await CreateDeclarationAsync(view, path, text, sig, label, adapters, undo, dte);
        }

        private async Task CreateDefinitionAsync(IWpfTextView view, string path, string text, FunctionScan.Sig sig, string label,
            IVsEditorAdaptersFactoryService adapters, Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry undo, DTE dte)
        {
            if (!IncludeService.IsHeader(path)) { await ReportAsync(L.T("宣言から定義を作るのは、ヘッダーで押してください"), true); return; }
            var opt = SyncService.Options;
            string root = IncludeService.RootFor(path);
            List<string> files = await Task.Run(() => SyncService.Candidates(path, sig.Class, root, true, opt));
            await JoinableTaskFactory.SwitchToMainThreadAsync();

            var keys = SignatureSync.KeyVariants(sig.Inner(text));
            var existing = SyncService.FindTargets(files, true, sig, adapters).Where(t => SyncPlan.SameKeysAny(SignatureSync.KeyVariants(t.Inner), keys)).ToList();
            if (existing.Count > 0) { await ReportAsync(L.F("{0} の定義は、すでに {1} にあります", label, Path.GetFileName(existing[0].File)), true); return; }

            var sources = files.Where(f => !IncludeService.IsHeader(f)).ToList();
            if (sources.Count == 0) { await ReportAsync(L.F("{0} の定義を足す .cpp が見つかりません ({1}.cpp を作ってください)", label, Path.GetFileNameWithoutExtension(path)), true); return; }
            string cppFile = sources[0];
            if (sources.Count > 1)
            {
                var names = sources.ToDictionary(f => f, f => f);
                string pick = Choose(L.F("{0} の定義を足す .cpp を選んでください。", label), names.Keys.ToList());
                if (pick == null) { await ReportAsync(L.T("やめました"), true); return; }
                cppFile = names[pick];
            }

            ITextBuffer buf = SyncService.OpenForEdit(cppFile, adapters);
            if (buf == null) { await ReportAsync(L.F("{0} を開けませんでした", Path.GetFileName(cppFile)), true); return; }
            string cppText = buf.CurrentSnapshot.GetText();
            string eol = CppText.Eol(cppText, CppText.Eol(text));

            string why;
            var edit = DefinitionGen.PlanDefinition(text, sig, cppText, eol, out why);
            if (edit == null) { await ReportAsync(label + ": " + why, true); return; }
            SyncService.Insert(buf, edit.Position, edit.Text, undo, L.T("K-Cpp: 定義を作る"));

            // 足した関数の本体へカーソルを置く(cpp がアクティブのまま)
            try
            {
                IVsTextView hv; manager_GetActive(out hv);
                IWpfTextView cv = hv == null ? null : adapters.GetWpfTextView(hv);
                if (cv != null && cv.TextBuffer == buf)
                {
                    int body = edit.Position + edit.Text.IndexOf('{') + 1 + eol.Length;
                    cv.Caret.MoveTo(new SnapshotPoint(cv.TextSnapshot, Math.Min(body, cv.TextSnapshot.Length)));
                    cv.ViewScroller.EnsureSpanVisible(new SnapshotSpan(cv.TextSnapshot, Math.Min(body, cv.TextSnapshot.Length), 0), Microsoft.VisualStudio.Text.Editor.EnsureSpanVisibleOptions.AlwaysCenter);
                }
            }
            catch (Exception ex) { Log("move caret failed: " + ex.Message); }
            await ReportAsync(L.F("{0} の定義を {1} に足しました", label, Path.GetFileName(cppFile)), false);
        }

        private void manager_GetActive(out IVsTextView view)
        {
            var manager = (IVsTextManager)GetService(typeof(SVsTextManager));
            manager.GetActiveView(1, null, out view);
        }

        private async Task CreateDeclarationAsync(IWpfTextView view, string path, string text, FunctionScan.Sig sig, string label,
            IVsEditorAdaptersFactoryService adapters, Microsoft.VisualStudio.Text.Operations.ITextUndoHistoryRegistry undo, DTE dte)
        {
            string why;
            string declaration = DefinitionGen.DeclarationFor(text, sig, out why);
            if (declaration == null) { await ReportAsync(label + ": " + why, true); return; }

            // どのクラスの宣言か。Class::Func の修飾と、cpp を囲む namespace から探す
            var cref = CppScan.EnclosingClassRef(text, sig.End);
            if (cref == null) { await ReportAsync(L.F("{0}: どのクラスのメンバーか読めませんでした", label), true); return; }
            var loc = await LocateClassAsync(dte, path, view, cref);
            if (loc == null) return;

            // すでに宣言があるか(同じ名前・同じ引数の型)
            var keys = SignatureSync.KeyVariants(sig.Inner(text));
            var inClass = FunctionScan.Scan(loc.Text).Where(s => !s.HasBody && s.Open > loc.Scope.Open && s.Close < loc.Scope.Close && s.Name == sig.Name && s.IsConst == sig.IsConst
                && SyncPlan.SameKeysAny(SignatureSync.KeyVariants(s.Inner(loc.Text)), keys)).ToList();
            if (inClass.Count > 0) { await ReportAsync(L.F("{0} の宣言は、すでに {1} にあります", label, Path.GetFileName(loc.File)), true); return; }

            string eol = CppText.Eol(loc.Text);
            var edit = DefinitionGen.PlanPublicMember(loc.Text, loc.Scope.Open, loc.Scope.IsStruct, declaration, eol);
            if (edit == null) { await ReportAsync(L.F("{0} の中でクラス {1} の本体を読めませんでした", Path.GetFileName(loc.File), cref.Name), true); return; }
            SyncService.Insert(loc.View.TextBuffer, edit.Position, edit.Text, undo, L.T("K-Cpp: 宣言を作る"));
            ReturnTo(path, loc.File);
            await ReportAsync(L.F("{0} を {1} の {2} に足しました (public)", declaration, Path.GetFileName(loc.File), cref.Name), false);
        }

        // ---- Getter・Setter ----

        /// <summary>getter / setter: どちらを作るか(両方 true が「Getter・Setter を作る」)。</summary>
        internal void RunAccessor(bool getter = true, bool setter = true)
        {
            _ = JoinableTaskFactory.RunAsync(async () =>
            {
                try { await RunAccessorAsync(getter, setter); }
                catch (Exception ex) { await ReportAsync(L.F("例外: {0}", ex.Message), true); Log(ex.ToString()); }
            });
        }

        /// <summary>
        /// ヘッダーの宣言行(UINT stride_;)か、cpp の代入行(stride_ = ...;)にカーソルがあれば、
        /// そのメンバー変数の GetStride / SetStride を、クラスの public: の末尾に足す。
        /// </summary>
        private async Task RunAccessorAsync(bool wantGetter, bool wantSetter)
        {
            await JoinableTaskFactory.SwitchToMainThreadAsync();
            var model = (IComponentModel)await GetServiceAsync(typeof(SComponentModel));
            var adapters = model.GetService<IVsEditorAdaptersFactoryService>();
            var manager = (IVsTextManager)await GetServiceAsync(typeof(SVsTextManager));
            var dte = (DTE)await GetServiceAsync(typeof(DTE));

            IVsTextView vsView;
            manager.GetActiveView(1, null, out vsView);
            IWpfTextView view = vsView == null ? null : adapters.GetWpfTextView(vsView);
            if (view == null) { await ReportAsync(L.T("アクティブなエディターがありません"), true); return; }

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
                    if (cls == null) { await ReportAsync(L.T("この行は、クラスの中ではありません"), true); return; }
                    loc = new Located { View = view, Text = curText, File = path };
                }
            }
            if (member == null)
            {
                // cpp の「名前 = 右辺;」の文(クラスの中に書いた関数や、ラムダの中でもよい)にカーソルがあるとき
                var assign = AssignScan.Find(curText, caret.Position);
                if (assign == null) { await ReportAsync(inHeader ? L.T("この行は、メンバー変数の宣言でも「名前 = 右辺;」の文でもありません") : L.T("この文は「名前 = 右辺;」の形ではありません"), true); return; }
                member = assign.Name;
                var cref = CppScan.EnclosingClassRef(curText, caret.Position);
                if (cref == null) { await ReportAsync(L.T("メンバー関数の中ではありません (Class::Func の形の定義か、クラスの中に書いた関数が対象です)"), true); return; }
                loc = await LocateClassAsync(dte, path, view, cref);
                if (loc == null) return;
                cls = AccessorEditor.All(loc.Text).FirstOrDefault(c => c.Open == loc.Scope.Open) ?? AccessorEditor.Find(loc.Text, cref.Name);
            }
            IWpfTextView target = loc.View;
            string className = cls == null ? "" : cls.Name;

            string all = loc.Text;
            if (cls == null) { await ReportAsync(L.T("クラスの本体を読めませんでした"), true); return; }
            bool readOnly;
            string type = AccessorEditor.FindMemberType(all, cls, member, out readOnly);
            if (type == null) { await ReportAsync(L.F("{0} の中に、{1} の宣言が見つかりません (配列と static は未対応)", className, member), true); return; }

            var skipped = new List<string>();
            var page = (OptionsPage)GetDialogPage(typeof(OptionsPage));
            string refused;
            var lines = AccessorEditor.MakeLines(all, cls, member, type, readOnly, page.BlankLineBetweenAccessors, skipped, out refused, wantGetter, wantSetter);
            if (lines == null) { await ReportAsync(refused, true); return; }
            if (lines.Count == 0) { await ReportAsync(L.F("{0} はすでにあります", string.Join("、", skipped)), true); return; }
            string eol = CppText.Eol(all);
            var edit = AccessorEditor.PlanPublic(all, cls, lines, eol, page.BlankLineBetweenAccessors);
            target.TextBuffer.Insert(edit.Position, edit.Text);

            if (!inHeader && path != null)
            {
                IVsUIHierarchy h2; uint i2; IVsWindowFrame f2;
                try { Microsoft.VisualStudio.Shell.VsShellUtilities.OpenDocument(this, path, Guid.Empty, out h2, out i2, out f2); }
                catch (Exception) { }
            }
            await ReportAsync(L.F("{0} を追加しました", string.Join(" / ", lines.Where(l => l.Length > 0).Select(l => l.Substring(0, l.IndexOf('{')).Trim()))), false);
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
            return KDialog.Choose("選んでください", message, items);
        }

        // ---- 型の入力欄 ----

        private static string Ask(string message, string initial)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            return KDialog.Input("名前を入力", message, initial);
        }
    }
}

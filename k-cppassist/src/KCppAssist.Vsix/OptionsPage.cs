using System;
using System.ComponentModel;
using System.Windows.Forms;
using EnvDTE;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist
{
    public enum IncludeMode { Off, ManualOnly, Auto }

    public enum SyncMode { Off, ManualOnly, Auto }

    public enum RenameMode { Off, ManualOnly, Auto }

    public enum CallCheckSeverity { Error, Warning }

    /// <summary>ツール → オプション → K-CppAssist → 全般</summary>
    public class OptionsPage : DialogPage
    {
        [Category("ゲッター・セッター")]
        [DisplayName("ゲッターとセッターの間に空行を入れる")]
        [Description("True のとき、Alt+E で作るゲッターとセッターの間と、その前の行との間に、空行を 1 行入れます。")]
        public bool BlankLineBetweenAccessors { get; set; } = true;

        [Category("#include")]
        [DisplayName("#include を足すしかた")]
        [Description("Off: 何もしない。ManualOnly: Alt+F を押したときだけ足す。Auto: Alt+F に加えて、入力中に未定義の型を見つけると、自動で足す。")]
        public IncludeMode IncludeMode { get; set; } = IncludeMode.ManualOnly;

        [Category("#include")]
        [DisplayName("自動で足す前の待ち時間 (ミリ秒)")]
        [Description("識別子を打ち終えてから、この時間だけ入力が止まったら調べます。")]
        public int IncludeDelayMs { get; set; } = 900;

        [Category("#include")]
        [DisplayName("自動で足さない名前")]
        [Description("カンマ区切り。ソリューションのヘッダーから引くときだけ、この名前の型は自動で足しません(Alt+F では足せます)。標準ライブラリの名前には効きません。")]
        public string IncludeDeny { get; set; } = "Instance,Get,Create,Data,Type,Result,Init,Value,Node,Item,State,Info,Name,Id,Key,Index,Context,Config,Manager,Handle,Callback,Function,Object,Base,Impl,Self";

        [Category("#include")]
        [DisplayName("ヘッダーを探さないフォルダー")]
        [Description("カンマ区切りのフォルダー名。この名前のフォルダーの下は、型の索引に入れません。")]
        public string IncludeSkipDirs { get; set; } = "third_party,external,extern,build,out,node_modules,vendor";

        [Category("引数の同期")]
        [DisplayName("宣言と定義の引数を合わせるしかた")]
        [Description("Off: 何もしない。ManualOnly: Alt+G を押したときだけ合わせる。Auto: Alt+G に加えて、ヘッダーの宣言か cpp の定義の引数を変えると、相手の引数を自動で書き換える(相手が開いていなければ開く)。")]
        public SyncMode SyncMode { get; set; } = SyncMode.Auto;

        [Category("引数の同期")]
        [DisplayName("自動で合わせるまでの待ち(ミリ秒)")]
        [Description("最後に入力してから、相手の引数を書き換えるまでの待ち。0 なら、打つそばから(次の入力の処理が終わり次第)相手が変わります。初期値は 0。")]
        public int SyncDelayMs { get; set; } = 0;

        [Category("引数の同期")]
        [DisplayName("書き換えた場所を小さなウィンドウで見せる")]
        [Description("True のとき、引数を相手のファイルへ写すと、書き換えた場所をエディターの右上に約 3 秒だけ見せます。")]
        public bool ShowSyncPreview { get; set; } = true;

        [Category("ファイル名の同期")]
        [DisplayName("ヘッダー・cpp の名前を変えたときのしかた")]
        [Description("Off: 何もしない。ManualOnly: Alt+N でまとめて変えたときだけ、相手・#include・CMake を直す。Auto: 名前を変えたことを自動で見つけて(Solution Explorer、フォルダー ビュー、エクスプローラー)、直す。Alt+N も使えます。")]
        public RenameMode RenameMode { get; set; } = RenameMode.Auto;

        [Category("ファイル名の同期")]
        [DisplayName("相手のファイルも同じ名前にする")]
        [Description("True のとき、Foo.h の名前を Bar.h に変えると、同じフォルダーの Foo.cpp も Bar.cpp にします(逆も同じ)。")]
        public bool RenamePair { get; set; } = true;

        [Category("ファイル名の同期")]
        [DisplayName("CMake の書き方も直す")]
        [Description("True のとき、CMakeLists.txt と .cmake の中の、古いファイル名(src/Foo.cpp など)も、新しい名前に直します。")]
        public bool RenameBuildFiles { get; set; } = true;

        [Category("呼び出しのチェック")]
        [DisplayName("引数の個数をビルド前にチェックする")]
        [Description("True のとき、std::make_unique<T>(…)、std::make_shared<T>(…)、new T(…) の引数の個数が、T のどのコンストラクターにも合わないと、ビルドの前に、エディターで波線を引きます。型の細かい違い(const・暗黙の変換)は見ません。コンストラクターを書いていないクラス、テンプレート、継承したコンストラクター、マクロのあるクラスは調べません。")]
        public bool CallCheckEnabled { get; set; } = true;

        [Category("呼び出しのチェック")]
        [DisplayName("波線の色")]
        [Description("Error: 赤い波線(エラー)。Warning: 緑の波線(警告)。どちらも、ビルドの結果には影響しません。")]
        public CallCheckSeverity CallCheckSeverity { get; set; } = CallCheckSeverity.Error;

        [Category("呼び出しのチェック")]
        [DisplayName("入力が止まってから調べるまでの待ち(ミリ秒)")]
        [Description("最後に入力してから、この時間だけ待って調べます。短くすると、すぐに波線が出ます。")]
        public int CallCheckDelayMs { get; set; } = 700;

        [Category("呼び出しのチェック")]
        [DisplayName("make_unique / make_shared を調べる")]
        [Description("std::make_unique<T>(…) と std::make_shared<T>(…) を調べます。")]
        public bool CallCheckMake { get; set; } = true;

        [Category("呼び出しのチェック")]
        [DisplayName("new T(…) を調べる")]
        [Description("new T(…) を調べます(配置 new と new T[n] は調べません)。")]
        public bool CallCheckNew { get; set; } = true;

        [Category("呼び出しのチェック")]
        [DisplayName("調べないクラス")]
        [Description("カンマ区切りのクラス名。誤って波線が出るクラスがあれば、ここに書くと出なくなります。")]
        public string CallCheckIgnore { get; set; } = "";

        [Category("キー")]
        [DisplayName("ファイル名をまとめて変える")]
        [Description(KeyHelp)]
        public string RenameKey { get; set; } = "Alt+N";

        [Category("全般")]
        [DisplayName("ステータスバーに知らせる")]
        [Description("True のとき、#include を足した、引数を写した、ファイル名を直した、などをステータスバーに 1 行出します。False でも、失敗の知らせは出ます。")]
        public bool ShowStatusMessages { get; set; } = true;

        [Category("全般")]
        [DisplayName("ログを残す")]
        [Description("True のとき、動作の記録を %LOCALAPPDATA%\\K-CppAssist\\vsix.log に書きます。不具合のとき、これを見ると原因が分かります。")]
        public bool WriteLog { get; set; } = true;

        [Category("#include")]
        [DisplayName("標準・Windows・DirectX の表を使う")]
        [Description("True のとき、std::vector → <vector> のような、組み込みの対応表で、ヘッダーを決めます。")]
        public bool IncludeUseTable { get; set; } = true;

        [Category("#include")]
        [DisplayName("ソリューションのヘッダーの索引を使う")]
        [Description("True のとき、ソリューションの下のヘッダーから、class / struct / enum / using の定義を集めて、型の名前からヘッダーを決めます。")]
        public bool IncludeUseIndex { get; set; } = true;

        [Category("#include")]
        [DisplayName("自分で決める対応 (名前=ヘッダー)")]
        [Description("「名前=ヘッダー」を、; か改行で区切って書きます。組み込みの表より先に使います。例: Vec3=\"math/vec3.h\";Json=<nlohmann/json.hpp>")]
        public string IncludeCustom { get; set; } = "";

        [Category("#include")]
        [DisplayName(".h でも、ソリューションの型を自動で足す")]
        [Description("False のとき、ヘッダーに自動で足すのは、標準・Windows・DirectX の表と、自分で決めた対応のものだけです(循環 include を避けるため)。True にすると、ソリューションの型も足します。")]
        public bool IncludeAutoInHeaders { get; set; } = false;

        [Category("#include")]
        [DisplayName("自動で足した #include を戻すまでの秒数")]
        [Description("自動で足した直後に、その識別子を消したら、足した #include も戻します。その猶予の秒数です。0 で、戻さないようにします。")]
        public int IncludeRevertSeconds { get; set; } = 40;

        [Category("ファイル名の同期")]
        [DisplayName("#include も新しい名前に直す")]
        [Description("True のとき、ソリューションの全ファイルの #include を、新しい名前に直します。")]
        public bool RenameUpdateIncludes { get; set; } = true;

        [Category("ファイル名の同期")]
        [DisplayName("ファイルの名前変更を、フォルダーの監視でも見つける")]
        [Description("True のとき、Solution Explorer 以外(フォルダー ビュー、エクスプローラー、別のツール)での名前変更も見つけて、自動で直します。")]
        public bool RenameWatchFiles { get; set; } = true;

        [Category("ファイル名の同期")]
        [DisplayName("多数の名前変更を、自動では直さない件数")]
        [Description("3 秒の間に、この件数より多くの名前変更が起きたら、git のブランチ切り替えなどの一括操作とみなして、自動では直しません。")]
        public int RenameBulkLimit { get; set; } = 4;

        [Category("ファイル名の同期")]
        [DisplayName("直す前に確認する")]
        [Description("True のとき、自動で直す前に、確認のダイアログを出します。")]
        public bool RenameConfirm { get; set; } = false;

        [Category("エラーログ")]
        [DisplayName("先頭に「まず一番上から」の案内を出す")]
        [Description("エラーが複数あるとき、先頭に、一番上のエラーから直す案内を出します。")]
        public bool ErrorLogShowOrderAdvice { get; set; } = true;

        [Category("エラーログ")]
        [DisplayName("連鎖の可能性を示す")]
        [Description("True のとき、上のエラーの影響で出ていそうなエラーに、「連鎖の可能性」と書きます。")]
        public bool ErrorLogShowCascade { get; set; } = true;

        [Category("エラーログ")]
        [DisplayName("直し方の例を出す")]
        [Description("True のとき、主なエラーに、修正前と修正後のコードの例を出します。")]
        public bool ErrorLogShowExamples { get; set; } = true;

        [Category("エラーログ")]
        [DisplayName("一度に出すエラーの数の上限")]
        [Description("これを超えるエラーは、省略します(「原文」表示では、全部読めます)。")]
        public int ErrorLogMaxItems { get; set; } = 400;

        [Category("エラーログ")]
        [DisplayName("エラーログを使う")]
        [Description("False にすると、ビルドが終わってもエラーログを作りません(窓も自動では開きません)。")]
        public bool ErrorLogEnabled { get; set; } = true;

        [Category("エラーログ")]
        [DisplayName("エラーがあるとき、窓を自動で前に出す")]
        [Description("True のとき、ビルドが終わってエラーがあれば、窓を前に出します(入力は奪いません)。False のときは、拡張機能 メニューから開きます。")]
        public bool ErrorLogAutoShow { get; set; } = true;

        [Category("エラーログ")]
        [DisplayName("原因を探す (.lib とソースの検索)")]
        [Description("True のとき、未解決の外部シンボル(LNK2019 など)について、ソリューションの .lib とソースを探して、原因を言い当てます。時間がかかるときは False にしてください。")]
        public bool ErrorLogFindLibs { get; set; } = true;

        [Category("エラーログ")]
        [DisplayName("探す時間の上限 (秒)")]
        [Description("原因を探す処理の、1 回あたりの時間の上限です。")]
        public int ErrorLogSearchSeconds { get; set; } = 6;

        [Category("エラーログ")]
        [DisplayName("読む .lib の数の上限")]
        [Description("原因を探すとき、読む .lib の数の上限です。")]
        public int ErrorLogMaxLibs { get; set; } = 800;

        [Category("エラーログ")]
        [DisplayName("型名を短くする")]
        [Description("True のとき、std::basic_string<char, …> を std::string のように、読みやすい形にします。")]
        public bool ErrorLogShortenTypes { get; set; } = true;

        [Category("エラーログ")]
        [DisplayName("日本語のヒントを出す")]
        [Description("True のとき、エラー コードごとの見出しの下に、対処のヒントを出します。")]
        public bool ErrorLogShowHints { get; set; } = true;

        [Category("エラーログ (窓の初期値)")]
        [DisplayName("警告も表示")]
        [Description("窓を開いたときの、「警告も表示」の初期値です。")]
        public bool ErrorLogShowWarnings { get; set; } = false;

        [Category("エラーログ (窓の初期値)")]
        [DisplayName("経路を全部表示")]
        [Description("窓を開いたときの、「経路を全部表示」の初期値です。")]
        public bool ErrorLogFullTrace { get; set; } = false;

        [Category("エラーログ (窓の初期値)")]
        [DisplayName("原文を併記")]
        [Description("窓を開いたときの、「原文を併記」の初期値です。")]
        public bool ErrorLogAttachRaw { get; set; } = false;

        [Category("エラーログ (窓の初期値)")]
        [DisplayName("原文")]
        [Description("窓を開いたときの、「原文」(整理せずに色だけ付ける)の初期値です。")]
        public bool ErrorLogRawMode { get; set; } = false;

        private const string KeyHelp = "「Alt+Q」「Ctrl+Alt+M」のように書きます。空にすると、キーを外します。OK を押すと、Visual Studio のキー割り当てに反映されます。";

        [Category("キー")]
        [DisplayName("ローカル変数に型を付ける")]
        [Description(KeyHelp)]
        public string LocalKey { get; set; } = "Alt+Q";

        [Category("キー")]
        [DisplayName("メンバー変数として宣言する")]
        [Description(KeyHelp)]
        public string MemberKey { get; set; } = "Alt+W";

        [Category("キー")]
        [DisplayName("ゲッター・セッターを作る")]
        [Description(KeyHelp)]
        public string AccessorKey { get; set; } = "Alt+E";

        [Category("キー")]
        [DisplayName("#include を足す")]
        [Description(KeyHelp)]
        public string IncludeKey { get; set; } = "Alt+F";

        [Category("キー")]
        [DisplayName("宣言と定義の引数を合わせる")]
        [Description(KeyHelp)]
        public string SyncKey { get; set; } = "Alt+G";

        [Category("キー")]
        [DisplayName("宣言・定義の相手を作る")]
        [Description(KeyHelp)]
        public string CreateKey { get; set; } = "Alt+R";

        [Category("キー")]
        [DisplayName("関数をヘッダー ⇄ cpp に移す")]
        [Description(KeyHelp)]
        public string MoveKey { get; set; } = "Alt+M";

        [Category("Quick Fix")]
        [DisplayName("電球(Quick Fix)に出す")]
        [Description("true: Ctrl+. の電球に、宣言・定義の相手を作る、引数を合わせる、変数に型を付ける、を出す。")]
        public bool ShowQuickFix { get; set; } = true;

        /// <summary>設定画面を開いたとき、Visual Studio に今割り当てられているキーを表示する。</summary>
        protected override void OnActivate(CancelEventArgs e)
        {
            base.OnActivate(e);
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                LocalKey = Current(KCppAssistPackage.CmdLocal);
                MemberKey = Current(KCppAssistPackage.CmdMember);
                AccessorKey = Current(KCppAssistPackage.CmdAccessor);
                IncludeKey = Current(KCppAssistPackage.CmdInclude);
                SyncKey = Current(KCppAssistPackage.CmdSync);
                RenameKey = Current(KCppAssistPackage.CmdRename);
                CreateKey = Current(KCppAssistPackage.CmdCreate);
                MoveKey = Current(KCppAssistPackage.CmdMove);
            }
            catch (Exception ex) { KCppAssistPackage.Log("read keys failed: " + ex.Message); }
        }

        /// <summary>OK を押したとき、変わっていたキーを割り当て直す。</summary>
        protected override void OnApply(PageApplyEventArgs e)
        {
            base.OnApply(e);
            ThreadHelper.ThrowIfNotOnUIThread();
            KCppAssistPackage.LogEnabled = WriteLog;
            if (e.ApplyBehavior != ApplyKind.Apply) return;
            try
            {
                Assign(KCppAssistPackage.CmdLocal, LocalKey);
                Assign(KCppAssistPackage.CmdMember, MemberKey);
                Assign(KCppAssistPackage.CmdAccessor, AccessorKey);
                Assign(KCppAssistPackage.CmdInclude, IncludeKey);
                Assign(KCppAssistPackage.CmdSync, SyncKey);
                Assign(KCppAssistPackage.CmdRename, RenameKey);
                Assign(KCppAssistPackage.CmdCreate, CreateKey);
                Assign(KCppAssistPackage.CmdMove, MoveKey);
            }
            catch (Exception ex)
            {
                KCppAssistPackage.Log("assign keys failed: " + ex);
                MessageBox.Show("キーを割り当てられませんでした。\n" + ex.Message, "K-CppAssist");
            }
        }

        private static Command Find(int id)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var dte = (DTE)Package.GetGlobalService(typeof(DTE));
            return dte.Commands.Item("{" + KCppAssistPackage.CmdSetGuid + "}", id);
        }

        private static string Current(int id)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var bindings = Find(id).Bindings as object[];
            if (bindings == null || bindings.Length == 0) return "";
            string s = (string)bindings[0];
            int k = s.IndexOf("::", StringComparison.Ordinal);
            return k >= 0 ? s.Substring(k + 2) : s;
        }

        private static void Assign(int id, string key)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            key = (key ?? "").Trim();
            if (key == Current(id)) return;
            Find(id).Bindings = key.Length == 0 ? new object[0] : new object[] { "Global::" + key };
        }
    }
}

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Linq;
using System.Windows.Forms;
using EnvDTE;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist
{
    public enum IncludeMode { Off, ManualOnly, Auto }

    public enum SyncMode { Off, ManualOnly, Auto }

    public enum RenameMode { Off, ManualOnly, Auto }

    public enum SymbolRenameMode { Off, OnLeave, Auto }

    public enum CallCheckSeverity { Error, Warning }

    /// <summary>新しいファイルの namespace。Auto: 既存のヘッダーで一番多いもの。Fixed: 設定の名前。None: 書かない。</summary>
    public enum NewFileNamespaceMode { Auto, Fixed, None }

    /// <summary>ファイル名からクラス名を決める規則。SameAsFile: ファイル名のまま。</summary>
    public enum ClassNaming { SameAsFile, PascalCase, SnakeCase, CamelCase }

    // HeaderEditor.cs の ConstantPlacement を使う
    public enum IndentKind { Auto, Tab, Spaces2, Spaces4 }

    public enum GuardKind { PragmaOnce, IncludeGuard }

    /// <summary>ツール → オプション → K-CppUltimateAssist → 全般</summary>
    public class OptionsPage : DialogPage
    {
        [LocCategory("言語")]
        [LocDisplayName("表示する言語")]
        [LocDescription("メニュー・電球・ダイアログ・この設定の画面の言語。初期値は日本語で、初めて起動したときだけ、PC の表示言語に合わせます(対応していない言語のときは English)。設定の画面の文字は、Visual Studio を開き直すと変わります。")]
        public UiLanguage Language { get; set; } = UiLanguage.Japanese;

        /// <summary>初めて起動したときに、PC の言語から Language を決めたか。</summary>
        [Browsable(false)]
        public bool LanguageInitialized { get; set; } = false;

        [LocCategory("Getter・Setter")]
        [LocDisplayName("Getter と Setter の間に空行を入れる")]
        [LocDescription("True のとき、Alt+G で作る Getter と Setter の間と、その前の行との間と、足した行の下(すぐ次が別のメンバーや private: のとき)に、空行を 1 行入れます。")]
        public bool BlankLineBetweenAccessors { get; set; } = true;

        [LocCategory("#include")]
        [LocDisplayName("#include を足すしかた")]
        [LocDescription("Off: 何もしない。ManualOnly: Alt+I (Include) を押したときだけ足す。Auto: Alt+I に加えて、入力中に未定義の型を見つけると、自動で足す。")]
        public IncludeMode IncludeMode { get; set; } = IncludeMode.Auto;

        [LocCategory("#include")]
        [LocDisplayName("自動で足す前の待ち時間 (ミリ秒)")]
        [LocDescription("識別子を打ち終えてから、この時間だけ入力が止まったら調べます。")]
        public int IncludeDelayMs { get; set; } = 900;

        [LocCategory("#include")]
        [LocDisplayName("自動で足さない名前")]
        [LocDescription("カンマ区切り。ソリューションのヘッダーから引くときだけ、この名前の型は自動で足しません(Alt+I では足せます)。標準ライブラリの名前には効きません。")]
        public string IncludeDeny { get; set; } = "Instance,Get,Create,Data,Type,Result,Init,Value,Node,Item,State,Info,Name,Id,Key,Index,Context,Config,Manager,Handle,Callback,Function,Object,Base,Impl,Self";

        [LocCategory("#include")]
        [LocDisplayName("ヘッダーを探さないフォルダー")]
        [LocDescription("カンマ区切りのフォルダー名。この名前のフォルダーの下は、型の索引に入れません。")]
        public string IncludeSkipDirs { get; set; } = "third_party,external,extern,build,out,node_modules,vendor";

        [LocCategory("引数の同期")]
        [LocDisplayName("宣言と定義の引数を合わせるしかた")]
        [LocDescription("Off: 何もしない。ManualOnly: Alt+S を押したときだけ合わせる。Auto: Alt+S に加えて、ヘッダーの宣言か cpp の定義の引数を変えると、相手の引数を自動で書き換える(相手が開いていなければ開く)。")]
        public SyncMode SyncMode { get; set; } = SyncMode.Auto;

        [LocCategory("引数の同期")]
        [LocDisplayName("自動で合わせるまでの待ち(ミリ秒)")]
        [LocDescription("最後に入力してから、相手の引数を書き換えるまでの待ち。0 なら、打つそばから(次の入力の処理が終わり次第)相手が変わります。初期値は 0。")]
        public int SyncDelayMs { get; set; } = 0;

        [LocCategory("引数の同期")]
        [LocDisplayName("書き換えた場所に点線を出す")]
        [LocDescription("True のとき、引数を相手のファイルへ写したときや、名前を変えたときに、書き換えた名前の下に、点線を約 3 秒だけ出します(C# の名前の変更と同じ見せかたで、ウィンドウは出しません)。点線が出るのは、いま開いているエディターの中の場所だけです。")]
        public bool ShowSyncPreview { get; set; } = true;

        [LocCategory("名前の変更")]
        [LocDisplayName("宣言の名前を変えたら、使っている場所も変える")]
        [LocDescription("Off: 何もしない。OnLeave: カーソルが名前から離れたときに、まとめて変える。Auto: 打つそばから変える。対象は、ローカル変数・引数・メンバー変数・メンバー関数・関数の、宣言(と定義)の名前。使っている側の名前を書き換えても、ほかは変えません。")]
        public SymbolRenameMode SymbolMode { get; set; } = SymbolRenameMode.Auto;

        [LocCategory("名前の変更")]
        [LocDisplayName("型が分からない obj.name も変える")]
        [LocDescription("False(既定): obj.name や p->name のうち、obj の型を宣言から読めて、同じクラスだと分かるものだけ変える。分からないものは変えずに、出力ウィンドウの K-Cpp に一覧を出す。True: 分からないものも、同じ名前なら変える(別のクラスの同じ名前のメンバーも変わることがあります)。")]
        public bool SymbolAmbiguous { get; set; } = false;

        [LocCategory("名前の変更")]
        [LocDisplayName("一緒に変わる場所を枠で囲む")]
        [LocDescription("True(既定): 宣言の名前を書き換えている間、一緒に変わる場所を点線の枠で囲む(書き換えている宣言は実線)。名前の変更が終わると消える。色は ツール → オプション → 環境 → フォントおよび色 の「K-Cpp: 一緒に変わる場所」で変えられます。")]
        public bool SymbolMarks { get; set; } = true;

        [LocCategory("名前の変更")]
        [LocDisplayName("引数の並べ替え・削除を、呼び出しにも写す")]
        [LocDescription("True のとき、関数の引数を並べ替えるか消して、カーソルが括弧の外へ出ると、その関数の呼び出しの引数も同じ並びに直します。足した引数に渡す値は決められないので、その呼び出しは直さずに、出力ウィンドウの K-Cpp に一覧を出します。")]
        public bool CallArgSync { get; set; } = true;

        [LocCategory("ファイル名の同期")]
        [LocDisplayName("ヘッダー・cpp の名前を変えたときのしかた")]
        [LocDescription("Off: 何もしない。ManualOnly: Alt+N でまとめて変えたときだけ、相手・#include・CMake を直す。Auto: 名前を変えたことを自動で見つけて(Solution Explorer、フォルダー ビュー、エクスプローラー)、直す。Alt+N も使えます。")]
        public RenameMode RenameMode { get; set; } = RenameMode.Auto;

        [LocCategory("ファイル名の同期")]
        [LocDisplayName("相手のファイルも同じ名前にする")]
        [LocDescription("True のとき、Foo.h の名前を Bar.h に変えると、同じフォルダーの Foo.cpp も Bar.cpp にします(逆も同じ)。")]
        public bool RenamePair { get; set; } = true;

        [LocCategory("ファイル名の同期")]
        [LocDisplayName("CMake の書き方も直す")]
        [LocDescription("True のとき、CMakeLists.txt と .cmake の中の、古いファイル名(src/Foo.cpp など)も、新しい名前に直します。")]
        public bool RenameBuildFiles { get; set; } = true;

        [LocCategory("呼び出しのチェック")]
        [LocDisplayName("引数の個数をビルド前にチェックする")]
        [LocDescription("True のとき、std::make_unique<T>(…)、std::make_shared<T>(…)、new T(…) の引数の個数が、T のどのコンストラクターにも合わないと、ビルドの前に、エディターで波線を引きます。型の細かい違い(const・暗黙の変換)は見ません。コンストラクターを書いていないクラス、テンプレート、継承したコンストラクター、マクロのあるクラスは調べません。")]
        public bool CallCheckEnabled { get; set; } = true;

        [LocCategory("呼び出しのチェック")]
        [LocDisplayName("波線の色")]
        [LocDescription("Error: 赤い波線(エラー)。Warning: 緑の波線(警告)。どちらも、ビルドの結果には影響しません。")]
        public CallCheckSeverity CallCheckSeverity { get; set; } = CallCheckSeverity.Error;

        [LocCategory("呼び出しのチェック")]
        [LocDisplayName("入力が止まってから調べるまでの待ち(ミリ秒)")]
        [LocDescription("最後に入力してから、この時間だけ待って調べます。短くすると、すぐに波線が出ます。")]
        public int CallCheckDelayMs { get; set; } = 700;

        [LocCategory("呼び出しのチェック")]
        [LocDisplayName("make_unique / make_shared を調べる")]
        [LocDescription("std::make_unique<T>(…) と std::make_shared<T>(…) を調べます。")]
        public bool CallCheckMake { get; set; } = true;

        [LocCategory("呼び出しのチェック")]
        [LocDisplayName("new T(…) を調べる")]
        [LocDescription("new T(…) を調べます(配置 new と new T[n] は調べません)。")]
        public bool CallCheckNew { get; set; } = true;

        [LocCategory("呼び出しのチェック")]
        [LocDisplayName("調べないクラス")]
        [LocDescription("カンマ区切りのクラス名。誤って波線が出るクラスがあれば、ここに書くと出なくなります。")]
        public string CallCheckIgnore { get; set; } = "";

        [LocCategory("キー")]
        [LocDisplayName("ファイル名をまとめて変える (Name)")]
        [Description(KeyHelp)]
        public string RenameKey { get; set; } = "Alt+N";

        [LocCategory("全般")]
        [LocDisplayName("ステータスバーに知らせる")]
        [LocDescription("True のとき、#include を足した、引数を写した、ファイル名を直した、などをステータスバーに 1 行出します。False でも、失敗の知らせは出ます。")]
        public bool ShowStatusMessages { get; set; } = true;

        [LocCategory("全般")]
        [LocDisplayName("ログを残す")]
        [LocDescription("True のとき、動作の記録を %LOCALAPPDATA%\\K-CppAssist\\vsix.log に書きます。不具合のとき、これを見ると原因が分かります。")]
        public bool WriteLog { get; set; } = true;

        [LocCategory("全般")]
        [LocDisplayName("「よく使うプロパティ」のページを出す")]
        [LocDescription("True のとき、プロジェクトのプロパティの「構成プロパティ」の先頭に、「よく使うプロパティ」のページを足します。項目は C/C++・リンカーなどの元の設定と同じ値で、ここで変えると元の設定も変わります。変えたあとは、VS を再起動してください。")]
        public bool CommonPropsPage { get; set; } = true;

        [LocCategory("#include")]
        [LocDisplayName("標準・Windows・DirectX の表を使う")]
        [LocDescription("True のとき、std::vector → <vector> のような、組み込みの対応表で、ヘッダーを決めます。")]
        public bool IncludeUseTable { get; set; } = true;

        [LocCategory("#include")]
        [LocDisplayName("ソリューションのヘッダーの索引を使う")]
        [LocDescription("True のとき、ソリューションの下のヘッダーから、class / struct / enum / using の定義を集めて、型の名前からヘッダーを決めます。")]
        public bool IncludeUseIndex { get; set; } = true;

        [LocCategory("#include")]
        [LocDisplayName("自分で決める対応 (名前=ヘッダー)")]
        [LocDescription("「名前=ヘッダー」を、; か改行で区切って書きます。組み込みの表より先に使います。例: Vec3=\"math/vec3.h\";Json=<nlohmann/json.hpp>")]
        public string IncludeCustom { get; set; } = "";

        [LocCategory("#include")]
        [LocDisplayName(".h でも、ソリューションの型を自動で足す")]
        [LocDescription("False のとき、ヘッダーに自動で足すのは、標準・Windows・DirectX の表と、自分で決めた対応のものだけです(循環 include を避けるため)。True にすると、ソリューションの型も足します。")]
        public bool IncludeAutoInHeaders { get; set; } = false;

        [LocCategory("#include")]
        [LocDisplayName("自動で足した #include を戻すまでの秒数")]
        [LocDescription("自動で足した直後に、その識別子を消したら、足した #include も戻します。その猶予の秒数です。0 で、戻さないようにします。")]
        public int IncludeRevertSeconds { get; set; } = 40;

        [LocCategory("ファイル名の同期")]
        [LocDisplayName("#include も新しい名前に直す")]
        [LocDescription("True のとき、ソリューションの全ファイルの #include を、新しい名前に直します。")]
        public bool RenameUpdateIncludes { get; set; } = true;

        [LocCategory("ファイル名の同期")]
        [LocDisplayName("ファイルの名前変更を、フォルダーの監視でも見つける")]
        [LocDescription("True のとき、Solution Explorer 以外(フォルダー ビュー、エクスプローラー、別のツール)での名前変更も見つけて、自動で直します。")]
        public bool RenameWatchFiles { get; set; } = true;

        [LocCategory("ファイル名の同期")]
        [LocDisplayName("多数の名前変更を、自動では直さない件数")]
        [LocDescription("3 秒の間に、この件数より多くの名前変更が起きたら、git のブランチ切り替えなどの一括操作とみなして、自動では直しません。")]
        public int RenameBulkLimit { get; set; } = 4;

        [LocCategory("ファイル名の同期")]
        [LocDisplayName("直す前に確認する")]
        [LocDescription("True(既定)のとき、自動で直す前に、何を何に直すかを見せるダイアログを出します(相手・#include・CMake と、クラス名を直すかを、項目ごとに選べます)。False なら、確認せずに、ダイアログの初期値どおりに直します(相手・#include・CMake と、ファイル名と同じだったクラス名)。ダイアログの「次から確認しない」に印を付けて反映すると、False になります。")]
        public bool RenameConfirm { get; set; } = true;

        [LocCategory("エラーログ")]
        [LocDisplayName("先頭に「まず一番上から」の案内を出す")]
        [LocDescription("エラーが複数あるとき、先頭に、一番上のエラーから直す案内を出します。")]
        public bool ErrorLogShowOrderAdvice { get; set; } = true;

        [LocCategory("エラーログ")]
        [LocDisplayName("連鎖の可能性を示す")]
        [LocDescription("True のとき、上のエラーの影響で出ていそうなエラーに、「連鎖の可能性」と書きます。")]
        public bool ErrorLogShowCascade { get; set; } = true;

        [LocCategory("エラーログ")]
        [LocDisplayName("直し方の例を出す")]
        [LocDescription("True のとき、主なエラーに、修正前と修正後のコードの例を出します。")]
        public bool ErrorLogShowExamples { get; set; } = true;

        [LocCategory("エラーログ")]
        [LocDisplayName("一度に出すエラーの数の上限")]
        [LocDescription("これを超えるエラーは、省略します(「原文」表示では、全部読めます)。")]
        public int ErrorLogMaxItems { get; set; } = 400;

        [LocCategory("エラーログ")]
        [LocDisplayName("エラーログを使う")]
        [LocDescription("False にすると、ビルドが終わってもエラーログを作りません(窓も自動では開きません)。")]
        public bool ErrorLogEnabled { get; set; } = true;

        [LocCategory("エラーログ")]
        [LocDisplayName("エラーがあるとき、窓を自動で前に出す")]
        [LocDescription("True のとき、ビルドが終わってエラーがあれば、窓を前に出します(入力は奪いません)。False(既定)のときは、拡張機能 メニューから開きます。")]
        public bool ErrorLogAutoShow { get; set; } = false;

        [LocCategory("エラーログ")]
        [LocDisplayName("原因を探す (.lib とソースの検索)")]
        [LocDescription("True のとき、未解決の外部シンボル(LNK2019 など)について、ソリューションの .lib とソースを探して、原因を言い当てます。時間がかかるときは False にしてください。")]
        public bool ErrorLogFindLibs { get; set; } = true;

        [LocCategory("エラーログ")]
        [LocDisplayName("探す時間の上限 (秒)")]
        [LocDescription("原因を探す処理の、1 回あたりの時間の上限です。")]
        public int ErrorLogSearchSeconds { get; set; } = 6;

        [LocCategory("エラーログ")]
        [LocDisplayName("読む .lib の数の上限")]
        [LocDescription("原因を探すとき、読む .lib の数の上限です。")]
        public int ErrorLogMaxLibs { get; set; } = 800;

        [LocCategory("エラーログ")]
        [LocDisplayName("型名を短くする")]
        [LocDescription("True のとき、std::basic_string<char, …> を std::string のように、読みやすい形にします。")]
        public bool ErrorLogShortenTypes { get; set; } = true;

        [LocCategory("エラーログ")]
        [LocDisplayName("ヒントを出す")]
        [LocDescription("True のとき、エラー コードごとの見出しの下に、対処のヒントを出します。")]
        public bool ErrorLogShowHints { get; set; } = true;

        [LocCategory("エラーログ (窓の初期値)")]
        [LocDisplayName("警告も表示")]
        [LocDescription("窓を開いたときの、「警告も表示」の初期値です。")]
        public bool ErrorLogShowWarnings { get; set; } = false;

        [LocCategory("エラーログ (窓の初期値)")]
        [LocDisplayName("経路を全部表示")]
        [LocDescription("窓を開いたときの、「経路を全部表示」の初期値です。")]
        public bool ErrorLogFullTrace { get; set; } = false;

        [LocCategory("エラーログ (窓の初期値)")]
        [LocDisplayName("原文を併記")]
        [LocDescription("窓を開いたときの、「原文を併記」の初期値です。")]
        public bool ErrorLogAttachRaw { get; set; } = false;

        [LocCategory("エラーログ (窓の初期値)")]
        [LocDisplayName("原文")]
        [LocDescription("窓を開いたときの、「原文」(整理せずに色だけ付ける)の初期値です。")]
        public bool ErrorLogRawMode { get; set; } = false;

        private const string KeyHelp = "「Alt+Q」「Ctrl+Alt+M」のように書きます。空にすると、キーを外します。OK を押すと、Visual Studio のキー割り当てに反映されます。";

        [LocCategory("キー")]
        [LocDisplayName("ローカル変数に型を付ける (Qualify type)")]
        [Description(KeyHelp)]
        public string LocalKey { get; set; } = "Alt+Q";

        [LocCategory("キー")]
        [LocDisplayName("メンバー変数として宣言する (Write member)")]
        [Description(KeyHelp)]
        public string MemberKey { get; set; } = "Alt+W";

        [LocCategory("キー")]
        [LocDisplayName("Getter・Setter を作る (Getter)")]
        [Description(KeyHelp)]
        public string AccessorKey { get; set; } = "Alt+G";

        [LocCategory("キー")]
        [LocDisplayName("#include を足す (Include)")]
        [Description(KeyHelp)]
        public string IncludeKey { get; set; } = "Alt+I";

        [LocCategory("キー")]
        [LocDisplayName("宣言と定義の引数を合わせる (Sync)")]
        [Description(KeyHelp)]
        public string SyncKey { get; set; } = "Alt+S";

        [LocCategory("キー")]
        [LocDisplayName("宣言・定義の相手を作る (Resolve)")]
        [Description(KeyHelp)]
        public string CreateKey { get; set; } = "Alt+R";

        [LocCategory("キー")]
        [LocDisplayName("関数をヘッダー ⇄ cpp に移す (Move)")]
        [Description(KeyHelp)]
        public string MoveKey { get; set; } = "Alt+M";

        [LocCategory("キー")]
        [LocDisplayName("#include を前方宣言にする (Forward)")]
        [Description(KeyHelp)]
        public string ForwardKey { get; set; } = "Alt+F";

        [LocCategory("キー")]
        [LocDisplayName("メンバーからコンストラクターを作る (Constructor)")]
        [Description(KeyHelp)]
        public string CtorKey { get; set; } = "Alt+C";

        [LocCategory("キー")]
        [LocDisplayName("基底クラスの仮想関数を override する (Override)")]
        [Description(KeyHelp)]
        public string OverrideKey { get; set; } = "Alt+O";

        [LocCategory("キー")]
        [LocDisplayName("呼び出しから関数を作る (Usage)")]
        [Description(KeyHelp)]
        public string UsageKey { get; set; } = "Alt+U";

        [LocCategory("キー")]
        [LocDisplayName("この位置の書き換え・生成の一覧 (eXplore)")]
        [Description(KeyHelp)]
        public string RefactorKey { get; set; } = "Alt+X";

        [LocCategory("include 整理")]
        [LocDisplayName("使っていない #include を、ヘッダーからも消す")]
        [LocDescription("false(既定): 使っていない #include の削除は、cpp だけ。true: ヘッダーも対象にする(他のファイルが、そのヘッダー経由で include を受け取っていると、ビルドが通らなくなることがあります)。")]
        public bool RemoveUnusedInHeaders { get; set; } = false;

        [LocCategory("Quick Fix")]
        [LocDisplayName("電球(Quick Fix)に出す")]
        [LocDescription("true: Ctrl+. の電球に、宣言・定義の相手を作る、引数を合わせる、変数に型を付ける、を出す。")]
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
                ForwardKey = Current(KCppAssistPackage.CmdForward);
                CtorKey = Current(KCppAssistPackage.CmdCtor);
                OverrideKey = Current(KCppAssistPackage.CmdOverride);
                UsageKey = Current(KCppAssistPackage.CmdUsage);
                RefactorKey = Current(KCppAssistPackage.CmdRefactor);
            }
            catch (Exception ex) { KCppAssistPackage.Log("read keys failed: " + ex.Message); }
        }

        /// <summary>OK を押したとき、変わっていたキーを割り当て直す。</summary>
        protected override void OnApply(PageApplyEventArgs e)
        {
            base.OnApply(e);
            ThreadHelper.ThrowIfNotOnUIThread();
            KCppAssistPackage.LogEnabled = WriteLog;
            if (e.ApplyBehavior == ApplyKind.Apply) L.Current = Language;
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
                Assign(KCppAssistPackage.CmdForward, ForwardKey);
                Assign(KCppAssistPackage.CmdCtor, CtorKey);
                Assign(KCppAssistPackage.CmdOverride, OverrideKey);
                Assign(KCppAssistPackage.CmdUsage, UsageKey);
                Assign(KCppAssistPackage.CmdRefactor, RefactorKey);
            }
            catch (Exception ex)
            {
                KCppAssistPackage.Log("assign keys failed: " + ex);
                MessageBox.Show("キーを割り当てられませんでした。\n" + ex.Message, "K-Cpp");
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
            string old = Current(id);
            if (key == old && !IsGlobal(id)) return;
            // 先頭(この設定画面で見せているキー)だけを入れ替えて、ほかに自分で足した割り当ては残す
            var list = Bindings(id);
            if (list.Count > 0) list.RemoveAt(0);
            if (key.Length > 0) list.Insert(0, EditorScope() + "::" + key);
            Find(id).Bindings = list.Cast<object>().ToArray();
        }

        private static List<string> Bindings(int id)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var arr = Find(id).Bindings as object[];
            var list = new List<string>();
            if (arr != null) foreach (object o in arr) if (o is string) list.Add((string)o);
            return list;
        }

        /// <summary>
        /// キーの範囲「テキスト エディター」の名前。日本語の VS では「テキスト エディター」と、表示の言語で名前が変わるので、
        /// エディターだけで使う既存のコマンド(Edit.CharLeft)の割り当てから読む。
        /// </summary>
        private static string EditorScope()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            return ScopeOf("Edit.CharLeft") ?? "Text Editor";
        }

        private static string GlobalScope()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            return ScopeOf("File.SaveAll") ?? "Global";
        }

        private static string ScopeOf(string command)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            try
            {
                var dte = (DTE)Package.GetGlobalService(typeof(DTE));
                var bindings = dte.Commands.Item(command).Bindings as object[];
                if (bindings == null) return null;
                foreach (object o in bindings)
                {
                    string s = o as string;
                    int k = s == null ? -1 : s.IndexOf("::", StringComparison.Ordinal);
                    if (k > 0) return s.Substring(0, k);
                }
            }
            catch (Exception) { }
            return null;
        }

        private static bool IsGlobal(int id)
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var bindings = Find(id).Bindings as object[];
            if (bindings == null || bindings.Length == 0) return false;
            string s = (string)bindings[0];
            return s.StartsWith(GlobalScope() + "::", StringComparison.Ordinal) || s.StartsWith("Global::", StringComparison.Ordinal);
        }

        /// <summary>
        /// 0.20.1 までは、キーをグローバルに割り当てていた(Alt+F でファイル メニューが開かなくなる)。
        /// 起動したときに 1 回だけ、グローバルの割り当てを「テキスト エディター」に移す。
        /// </summary>
        internal void MigrateKeyScopes()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (KeyScopeMigrated) return;
            int[] ids =
            {
                KCppAssistPackage.CmdLocal, KCppAssistPackage.CmdMember, KCppAssistPackage.CmdAccessor, KCppAssistPackage.CmdInclude,
                KCppAssistPackage.CmdSync, KCppAssistPackage.CmdRename, KCppAssistPackage.CmdCreate, KCppAssistPackage.CmdMove,
                KCppAssistPackage.CmdForward, KCppAssistPackage.CmdCtor, KCppAssistPackage.CmdOverride,
                KCppAssistPackage.CmdUsage,
            };
            foreach (int id in ids)
            {
                try
                {
                    // グローバルの割り当てだけを、テキスト エディターに移す(ほかの範囲の割り当ては、そのまま)
                    string global = GlobalScope() + "::";
                    var list = Bindings(id);
                    bool changed = false;
                    for (int k = 0; k < list.Count; k++)
                    {
                        string s = list[k];
                        string rest = s.StartsWith(global, StringComparison.Ordinal) ? s.Substring(global.Length)
                            : s.StartsWith("Global::", StringComparison.Ordinal) ? s.Substring("Global::".Length) : null;
                        if (rest == null) continue;
                        list[k] = EditorScope() + "::" + rest;
                        changed = true;
                    }
                    if (changed) Find(id).Bindings = list.Distinct().Cast<object>().ToArray();
                }
                catch (Exception ex) { KCppAssistPackage.Log("migrate key failed: " + ex.Message); }
            }
            KeyScopeMigrated = true;
            SaveSettingsToStorage();
        }

        [LocCategory("書き換えと生成")]
        [LocDisplayName("JSON (nlohmann) の項目を出す")]
        [LocDescription("True のとき、クラスの電球に「JSON に読み書きできるようにする (nlohmann)」を出します。初期値は False(nlohmann を使わないプロジェクトでは邪魔になるため)。")]
        public bool OfferJson { get; set; } = false;

        [LocCategory("書き換えと生成")]
        [LocDisplayName("cereal の項目を出す")]
        [LocDescription("True のとき、クラスの電球に「cereal で保存できるようにする (serialize)」を出します。初期値は False。")]
        public bool OfferCereal { get; set; } = false;

        [LocCategory("書き換えと生成")]
        [LocDisplayName("Natvis の項目を出す")]
        [LocDescription("True のとき、クラスの電球に「デバッガーの表示 (Natvis) を作る」を出します。初期値は False。")]
        public bool OfferNatvis { get; set; } = false;

        [LocCategory("宣言の生成")]
        [LocDisplayName("定数 (static constexpr) を置く位置")]
        [LocDescription("電球で定数として宣言するとき、クラスの区画(public: か private:)のどこに置くか。AfterTypes: 型・using の直後(なければ区画の先頭)。SectionTop: 区画の一番上(型・using よりも前)。BeforeMembers: メンバー変数の直前。")]
        public ConstantPlacement ConstantPlacement { get; set; } = ConstantPlacement.AfterTypes;

        [LocCategory("switch")]
        [LocDisplayName("switch を打ったら、case と default を自動で入れる")]
        [LocDescription("True のとき、enum / enum class の値を switch (値) { で受けて改行すると、本体が空なら、値ごとの「case 値: break;」と「default: break;」を自動で入れます。enum の型が決められない switch(整数など)では、何もしません。Ctrl+Z 1 回で消えます。")]
        public bool AutoSwitch { get; set; } = true;

        [LocCategory("新規ファイル")]
        [LocDisplayName("新しい空のファイルに、ひな形を書く")]
        [LocDescription("True のとき、プロジェクトに新しく足した空のヘッダーに #pragma once・namespace・class を、空の cpp に #include と namespace を書きます(作ってから 2 分以内の、空のファイルだけ)。")]
        public bool NewFileTemplate { get; set; } = true;

        [LocCategory("新規ファイル")]
        [LocDisplayName("ヘッダーに class を書く")]
        [LocDescription("True のとき、ヘッダーに「class クラス名 {」から「};」までを書きます。False なら、namespace だけ。")]
        public bool NewFileClass { get; set; } = true;

        [LocCategory("新規ファイル")]
        [LocDisplayName("class にコンストラクター・デストラクターを = default で書く")]
        [LocDescription("True(初期値)のとき、新しいヘッダーのひな形と、VS の「クラスの追加」で作ったクラスの public: に、「Foo() = default;」と「~Foo() = default;」を書きます。VS がすでにコンストラクター・デストラクターを書いていれば、そちらを残します。")]
        public bool NewFileCtorDefault { get; set; } = true;

        [LocCategory("新規ファイル")]
        [LocDisplayName("クラス名の決めかた")]
        [LocDescription("SameAsFile: ファイル名と同じ(初期値)。PascalCase: game_object → GameObject。SnakeCase: GameObject → game_object。CamelCase: game_object → gameObject。")]
        public ClassNaming NewFileClassNaming { get; set; } = ClassNaming.SameAsFile;

        [LocCategory("新規ファイル")]
        [LocDisplayName("namespace の決めかた")]
        [LocDescription("Auto: ソリューションの既存のヘッダーで、行頭の namespace が一番多いもの(初期値)。Fixed: 下の名前を使う。None: 書かない。")]
        public NewFileNamespaceMode NewFileNamespaceMode { get; set; } = NewFileNamespaceMode.Auto;

        [LocCategory("新規ファイル")]
        [LocDisplayName("固定の namespace")]
        [LocDescription("namespace の決めかたが Fixed のときに使う名前。「Game::Core」のように :: でつなげます。")]
        public string NewFileNamespace { get; set; } = "";

        [LocCategory("新規ファイル")]
        [LocDisplayName("字下げ")]
        [LocDescription("Auto: 既存のヘッダーで多いほう(タブか、空白 2 / 4)。判断できなければタブ。")]
        public IndentKind NewFileIndent { get; set; } = IndentKind.Auto;

        [LocCategory("新規ファイル")]
        [LocDisplayName("namespace の中を字下げする")]
        [LocDescription("True(初期値)のとき、namespace の中の class を 1 段字下げします。")]
        public bool NewFileIndentInNamespace { get; set; } = true;

        [LocCategory("新規ファイル")]
        [LocDisplayName("インクルード ガード")]
        [LocDescription("PragmaOnce: #pragma once(初期値)。IncludeGuard: #ifndef / #define / #endif。")]
        public GuardKind NewFileGuard { get; set; } = GuardKind.PragmaOnce;

        [LocCategory("新規ファイル")]
        [LocDisplayName("namespace を閉じる行にコメントを付ける")]
        [LocDescription("True のとき、「}  // namespace 名前」と書きます。False(初期値)なら「}」だけです。")]
        public bool NewFileNamespaceComment { get; set; } = false;

        [LocCategory("新規ファイル")]
        [LocDisplayName("強制インクルードにある pch の #include を書かない")]
        [LocDescription("True(初期値)のとき、プロジェクトの「強制インクルード ファイル」(/FI、ForcedIncludeFiles)に pch.h などがあれば、VS の「クラスの追加」が cpp に書いた #include \"pch.h\" を、書き直すときに消します。/FI で毎回読み込まれるので、書かなくてもビルドできます。")]
        public bool SkipForcedPch { get; set; } = true;

        [Browsable(false)]
        public bool KeyScopeMigrated { get; set; } = false;

        /// <summary>
        /// 既定を変えた設定を、新しい既定に移したバージョン(0 は未移行)。
        /// VS は設定画面で OK を押すと全部の値を保存するので、既定を変えても、古い既定のまま保存された値が勝ってしまう。
        /// </summary>
        [Browsable(false)]
        public int DefaultsVersion { get; set; } = 0;

        /// <summary>
        /// 0.26.0 で既定を変えた「直す前に確認する」(False → True)と「#include を足すしかた」(ManualOnly → Auto)を、
        /// 起動したときに 1 回だけ、新しい既定にする。古い既定のまま保存されていると、確認のダイアログが出ないため。
        /// </summary>
        internal void MigrateDefaults()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            if (DefaultsVersion >= 26) { MigrateDefaults27(); return; }
            if (!RenameConfirm) { RenameConfirm = true; KCppAssistPackage.Log("migrate: RenameConfirm False -> True"); }
            if (IncludeMode == IncludeMode.ManualOnly) { IncludeMode = IncludeMode.Auto; KCppAssistPackage.Log("migrate: IncludeMode ManualOnly -> Auto"); }
            DefaultsVersion = 26;
            SaveSettingsToStorage();
            MigrateDefaults27();
        }

        /// <summary>0.26.3 で既定を変えた、ひな形の namespace(中を字下げする: False → True、閉じる行のコメント: True → False)を、1 回だけ移す。</summary>
        private void MigrateDefaults27()
        {
            if (DefaultsVersion >= 27) return;
            if (!NewFileIndentInNamespace) { NewFileIndentInNamespace = true; KCppAssistPackage.Log("migrate: NewFileIndentInNamespace False -> True"); }
            if (NewFileNamespaceComment) { NewFileNamespaceComment = false; KCppAssistPackage.Log("migrate: NewFileNamespaceComment True -> False"); }
            DefaultsVersion = 27;
            SaveSettingsToStorage();
        }
    }
}

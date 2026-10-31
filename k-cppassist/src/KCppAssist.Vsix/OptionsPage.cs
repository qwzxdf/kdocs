using System;
using System.ComponentModel;
using System.Windows.Forms;
using EnvDTE;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist
{
    public enum IncludeMode { Off, ManualOnly, Auto }

    public enum SyncMode { Off, ManualOnly, Auto }

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
        [Description("最後に入力してから、相手の引数を書き換えるまでの待ち。短いほど、打つそばから相手が変わります。初期値は 250。")]
        public int SyncDelayMs { get; set; } = 250;

        [Category("引数の同期")]
        [DisplayName("書き換えた場所を小さなウィンドウで見せる")]
        [Description("True のとき、引数を相手のファイルへ写すと、書き換えた場所をエディターの右上に約 3 秒だけ見せます。")]
        public bool ShowSyncPreview { get; set; } = true;

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
            }
            catch (Exception ex) { KCppAssistPackage.Log("read keys failed: " + ex.Message); }
        }

        /// <summary>OK を押したとき、変わっていたキーを割り当て直す。</summary>
        protected override void OnApply(PageApplyEventArgs e)
        {
            base.OnApply(e);
            ThreadHelper.ThrowIfNotOnUIThread();
            if (e.ApplyBehavior != ApplyKind.Apply) return;
            try
            {
                Assign(KCppAssistPackage.CmdLocal, LocalKey);
                Assign(KCppAssistPackage.CmdMember, MemberKey);
                Assign(KCppAssistPackage.CmdAccessor, AccessorKey);
                Assign(KCppAssistPackage.CmdInclude, IncludeKey);
                Assign(KCppAssistPackage.CmdSync, SyncKey);
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

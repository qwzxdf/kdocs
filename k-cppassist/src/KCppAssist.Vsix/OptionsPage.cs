using System;
using System.ComponentModel;
using System.Windows.Forms;
using EnvDTE;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist
{
    /// <summary>ツール → オプション → K-CppAssist → 全般</summary>
    public class OptionsPage : DialogPage
    {
        [Category("ゲッター・セッター")]
        [DisplayName("ゲッターとセッターの間に空行を入れる")]
        [Description("True のとき、Alt+E で作るゲッターとセッターの間と、その前の行との間に、空行を 1 行入れます。")]
        public bool BlankLineBetweenAccessors { get; set; } = true;

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

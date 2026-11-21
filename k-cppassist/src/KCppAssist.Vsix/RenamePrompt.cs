using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Media;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist
{
    /// <summary>名前を変えたあとに、「何を何に直すか」を見せて、項目ごとにチェックで選ばせる小さなダイアログ。</summary>
    internal static class RenamePrompt
    {
        public sealed class Item
        {
            public string Text;         // チェックの横の文
            public string Detail;       // 「Foo → Bar」のような、小さな補足(null なら出さない)
            public bool Checked;
        }

        /// <summary>
        /// OK なら、項目ごとのチェックの結果を返す。キャンセルなら null。UI スレッドから呼ぶ。
        /// headline は見出し、detail は見出しの下の等幅の箱(「A.h → B.h」など)。
        /// dontAsk は「次から確認しない」に印を付けて OK を押したとき true(キャンセルのときは、印があっても false)。
        /// </summary>
        public static bool[] Show(string headline, string detail, IList<Item> items, out bool dontAsk, string okText = "反映する")
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var f = KDialog.Create(L.T(headline), detail);
            f.Body.Children.Add(f.Text(L.T("ほかのファイルにも反映しますか?"), 13, 0.8));

            // 項目は、1 つずつ薄い面のカードにする(チェックと、その下の等幅の補足)
            var boxes = new List<CheckBox>();
            foreach (var it in items)
            {
                var sp = new StackPanel();
                sp.Children.Add(f.Text(L.T(it.Text), 13.5));
                if (!string.IsNullOrEmpty(it.Detail))
                    sp.Children.Add(new TextBlock
                    {
                        Text = it.Detail,
                        FontFamily = new FontFamily("Cascadia Mono, Consolas"),
                        FontSize = 12,
                        Foreground = new SolidColorBrush(f.P.Muted),
                        Margin = new Thickness(0, 4, 0, 0),
                        TextWrapping = TextWrapping.Wrap,
                    });
                var cb = f.Check(sp, it.Checked);
                boxes.Add(cb);
                f.Body.Children.Add(new Border
                {
                    CornerRadius = new CornerRadius(8),
                    Background = new SolidColorBrush(f.P.Panel),
                    BorderBrush = new SolidColorBrush(f.P.Border),
                    BorderThickness = new Thickness(1),
                    Padding = new Thickness(14, 12, 14, 12),
                    Margin = new Thickness(0, 10, 0, 0),
                    Child = cb,
                });
            }

            // 「次から確認しない」は左下。初期値は印なし(印を付けて反映すると、設定の「直す前に確認する」を False にする)
            var never = f.Check(f.Text(L.T("次から確認しない"), 12, 0.8), false);
            never.VerticalAlignment = VerticalAlignment.Center;
            DockPanel.SetDock(never, Dock.Left);
            f.Footer.Children.Add(never);

            bool[] result = null;
            bool dont = false;
            var ok = f.AddButton(L.T(okText), true, true, false, () =>
            {
                result = new bool[boxes.Count];
                for (int i = 0; i < boxes.Count; i++) result[i] = boxes[i].IsChecked == true;
                dont = never.IsChecked == true;
                f.Window.Close();
            });
            // 何もしないボタンは右端(Esc でも同じ)
            f.AddButton(L.T("何もしない"), false, false, true, () => f.Window.Close());
            f.Window.Loaded += (s, e) => ok.Focus();
            f.Show();
            dontAsk = dont;
            return result;
        }

        /// <summary>「次から確認しない」を選んだので、設定の「直す前に確認する」を False にして保存する。</summary>
        public static void TurnOffConfirm()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var opt = RenameService.Options;
            if (opt == null || !opt.RenameConfirm) return;
            opt.RenameConfirm = false;
            opt.SaveSettingsToStorage();
            KCppAssistPackage.Log("rename: confirm turned off from the dialog");
        }
    }
}

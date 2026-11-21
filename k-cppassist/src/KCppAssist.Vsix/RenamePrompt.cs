using System;
using System.Collections.Generic;
using System.Windows;
using System.Windows.Controls;
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
        /// dontAsk は「次から確認しない」に印を付けて OK を押したとき true(キャンセルのときは、印があっても false)。
        /// </summary>
        public static bool[] Show(string headline, string detail, IList<Item> items, out bool dontAsk, string okText = "反映する")
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            bool[] result = null;
            bool dont = false;
            var panel = new StackPanel { Margin = new Thickness(16) };
            panel.Children.Add(new TextBlock { Text = headline, FontSize = 15, FontWeight = FontWeights.SemiBold, TextWrapping = TextWrapping.Wrap, MaxWidth = 460 });
            if (!string.IsNullOrEmpty(detail))
                panel.Children.Add(new TextBlock { Text = detail, Opacity = 0.75, Margin = new Thickness(0, 4, 0, 0), TextWrapping = TextWrapping.Wrap, MaxWidth = 460 });
            var boxes = new List<CheckBox>();
            foreach (var it in items)
            {
                var sp = new StackPanel();
                sp.Children.Add(new TextBlock { Text = it.Text, TextWrapping = TextWrapping.Wrap, MaxWidth = 430 });
                if (!string.IsNullOrEmpty(it.Detail))
                    sp.Children.Add(new TextBlock { Text = it.Detail, FontFamily = new System.Windows.Media.FontFamily("Consolas"), Opacity = 0.8, Margin = new Thickness(0, 2, 0, 0), TextWrapping = TextWrapping.Wrap, MaxWidth = 430 });
                var cb = new CheckBox { Content = sp, IsChecked = it.Checked, Margin = new Thickness(0, 12, 0, 0) };
                boxes.Add(cb);
                panel.Children.Add(cb);
            }
            var ok = new Button { Content = okText, IsDefault = true, MinWidth = 90, Padding = new Thickness(10, 3, 10, 3), Margin = new Thickness(0, 0, 8, 0) };
            var no = new Button { Content = "何もしない", IsCancel = true, MinWidth = 90, Padding = new Thickness(10, 3, 10, 3) };
            // 「次から確認しない」は左端、ボタンは右端。初期値は印なし(印を付けて OK を押すと、設定の「直す前に確認する」を False にする)
            var never = new CheckBox { Content = "次から確認しない", IsChecked = false, VerticalAlignment = VerticalAlignment.Center, Margin = new Thickness(0, 0, 24, 0), Opacity = 0.85 };
            var buttons = new StackPanel { Orientation = Orientation.Horizontal };
            buttons.Children.Add(ok);
            buttons.Children.Add(no);
            var row = new DockPanel { LastChildFill = false, Margin = new Thickness(0, 18, 0, 0) };
            DockPanel.SetDock(never, Dock.Left);
            DockPanel.SetDock(buttons, Dock.Right);
            row.Children.Add(never);
            row.Children.Add(buttons);
            panel.Children.Add(row);
            var w = new Window
            {
                Title = "K-CppAssist",
                Content = panel,
                SizeToContent = SizeToContent.WidthAndHeight,
                WindowStartupLocation = WindowStartupLocation.CenterScreen,
                ResizeMode = ResizeMode.NoResize,
                Topmost = true,
                ShowInTaskbar = false,
            };
            ok.Click += (s, e) =>
            {
                result = new bool[boxes.Count];
                for (int i = 0; i < boxes.Count; i++) result[i] = boxes[i].IsChecked == true;
                dont = never.IsChecked == true;
                w.Close();
            };
            w.Loaded += (s, e) => ok.Focus();
            w.ShowDialog();
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

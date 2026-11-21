using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.Windows;
using System.Windows.Controls;
using Microsoft.VisualStudio.Shell;

namespace KCppAssist
{
    /// <summary>拡張機能 メニューの「K-CppAssist の使い方...」。機能とキーの早見表を、その場で見せる。</summary>
    public sealed partial class KCppAssistPackage
    {
        internal const int CmdHelp = 0x010E;
        private const string DocsUrl = "https://qwzxdf.github.io/kdocs/kcppassist/";

        private void RegisterHelpCommand(OleMenuCommandService commands)
        {
            commands.AddCommand(new MenuCommand((s, e) => ShowHelp(), new CommandID(CmdSet, CmdHelp)));
        }

        private sealed class HelpItem
        {
            public string Key, Title, Desc;
            public HelpItem(string key, string title, string desc) { Key = key; Title = title; Desc = desc; }
        }

        private sealed class HelpSection
        {
            public string Icon, Title;
            public List<HelpItem> Items = new List<HelpItem>();
            public HelpSection(string icon, string title, params HelpItem[] items) { Icon = icon; Title = title; Items.AddRange(items); }
        }

        private static HelpItem H(string key, string title, string desc) { return new HelpItem(key, title, desc); }

        private static readonly List<HelpSection> HelpSections = new List<HelpSection>
        {
            new HelpSection("🔤", "変数まわり",
                H("Alt+Q", "ローカル変数に型を付ける (Qualify type)", "count = 0;  →  int count = 0;"),
                H("Alt+W", "メンバー変数として宣言する (Write member)", "cpp の stride_ = 1; から、ヘッダーのクラスに UINT stride_; を足す"),
                H("Alt+G", "ゲッター・セッターを作る (Getter)", "ヘッダーのメンバー変数の行で押すと、public: の末尾に GetXxx / SetXxx を足す")),
            new HelpSection("📎", "#include",
                H("Alt+I", "#include を足す (Include)", "カーソルの型名 (std::vector、ComPtr、自作クラス) のヘッダーを、cpp / ヘッダーの先頭に足す"),
                H("Alt+F", "#include を前方宣言にする (Forward)", "ヘッダーの #include \"x.h\" を class X; にして、#include を cpp に移す (ポインター・参照・shared_ptr だけで使っている型が対象)"),
                H("メニュー", "整理・不要の削除", "このファイル／プロジェクト全体の #include を整理、使っていない #include を消す (#include の行の電球にも出る)")),
            new HelpSection("🧱", "クラスと関数を作る",
                H("Alt+U", "呼び出しから関数を作る (Use)", "Foo(a, 1) の行で押すと、型を読んで宣言と定義の雛形を作る"),
                H("Alt+O", "基底クラスの仮想関数を override する (Override)", "足りない override の宣言を足す (純粋仮想関数を優先)"),
                H("Alt+C", "コンストラクターを作る (Constructor)", "データ メンバーから、初期化リストつきのコンストラクターを作る"),
                H("Alt+Enter", "クラス名の上で", "cpp を作る／コンストラクター・デストラクターを宣言／宣言して cpp に定義／コピー・ムーブを禁止")),
            new HelpSection("🔗", "宣言と定義",
                H("Alt+S", "宣言と定義の引数を合わせる (Sync)", "変えた側に、相手 (開いていなくても) を合わせる。引数を変えると自動でも合う"),
                H("Alt+R", "宣言・定義の相手を作る (Resolve)", "ヘッダーの宣言から cpp の定義の雛形、cpp の定義からヘッダーの宣言"),
                H("Alt+M", "関数を ヘッダー ⇄ cpp に移す (Move)", "ヘッダーの本体を cpp へ／cpp の Class::Func の本体をヘッダーへ")),
            new HelpSection("✏️", "名前の変更 (自動)",
                H("自動", "宣言の名前を書き換える", "ローカル変数・引数・メンバー・関数の名前を書き換えると、使っている場所も打つそばから同じ名前になる"),
                H("自動", "引数を並べ替える・消す", "カーソルが括弧の外へ出たときに、呼び出しの引数も同じ並びに直す"),
                H("Alt+N", "ファイル名をまとめて変える (Name)", "ヘッダー・cpp の片方の名前を変えると、相手・#include・CMake も直す")),
            new HelpSection("🆕", "新しいファイル",
                H("自動", "空のファイルにひな形", "新しく足した空の .h に #pragma once・namespace・class を、空の .cpp に #include と namespace を書く"),
                H("設定", "クラス名・namespace・字下げ", "既定はファイル名＝クラス名。namespace と字下げは、既存のヘッダーで一番多いものを使う (設定で固定・変更できる)")),
            new HelpSection("💡", "書き換え・生成 (Alt+Enter の電球 / Alt+X の一覧)",
                H("行", "書き換え", "NULL → nullptr、typedef → using、C のキャスト → static_cast、添字の for → 範囲 for、if の反転、早期 return、型 → auto"),
                H("クラス", "生成", "コピー禁止・ムーブ可、== と <=>、std::formatter、std::hash、JSON、cereal、Natvis、定義のない関数をまとめて作る、クラスを 名前.h / .cpp に移す"),
                H("その他", "enum・D3D・デバッグ出力", "enum の ToString / FromString、入力レイアウト、定数バッファの詰め物、変数の値を出す行 (// KDBG)")),
            new HelpSection("🛠", "ほか",
                H("自動", "エラーログ (K-ErrorLog)", "ビルド後のエラーを読みやすく並べ、縮小変換は [クリックで修正] できる"),
                H("自動", "引数の個数チェック", "make_unique / make_shared / new の引数の個数が合わないと、波線を引く"),
                H("設定", "拡張機能 → K-CppAssist の設定", "キーの変更、各機能の ON/OFF")),
        };

        private static System.Windows.Media.Brush Themed(System.Windows.Media.Color fallback, Microsoft.VisualStudio.Shell.ThemeResourceKey key)
        {
            try
            {
                var c = Microsoft.VisualStudio.PlatformUI.VSColorTheme.GetThemedColor(key);
                return new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromArgb(c.A, c.R, c.G, c.B));
            }
            catch (Exception) { }
            return new System.Windows.Media.SolidColorBrush(fallback);
        }

        private void ShowHelp()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var bg = Themed(System.Windows.Media.Color.FromRgb(0x1E, 0x1E, 0x1E), Microsoft.VisualStudio.PlatformUI.EnvironmentColors.ToolWindowBackgroundColorKey);
            var fg = Themed(System.Windows.Media.Color.FromRgb(0xDD, 0xDD, 0xDD), Microsoft.VisualStudio.PlatformUI.EnvironmentColors.ToolWindowTextColorKey);
            var border = Themed(System.Windows.Media.Color.FromRgb(0x55, 0x55, 0x55), Microsoft.VisualStudio.PlatformUI.EnvironmentColors.ToolWindowBorderColorKey);
            var dim = Themed(System.Windows.Media.Color.FromRgb(0x99, 0x99, 0x99), Microsoft.VisualStudio.PlatformUI.EnvironmentColors.CommandBarTextInactiveColorKey);
            var accent = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromRgb(0x4C, 0x8B, 0xF5));
            var chipBg = new System.Windows.Media.SolidColorBrush(System.Windows.Media.Color.FromArgb(0x30, 0x4C, 0x8B, 0xF5));
            var font = new System.Windows.Media.FontFamily("Yu Gothic UI, Meiryo UI, Segoe UI");

            var cards = new StackPanel();
            var rows = new List<Tuple<FrameworkElement, string, FrameworkElement>>();     // 行、検索用の文字、属するカード

            foreach (var sec in HelpSections)
            {
                var card = new Border { BorderBrush = border, BorderThickness = new Thickness(1), CornerRadius = new CornerRadius(8), Padding = new Thickness(14, 10, 14, 10), Margin = new Thickness(0, 0, 0, 12) };
                var inner = new StackPanel();
                var title = new StackPanel { Orientation = Orientation.Horizontal, Margin = new Thickness(0, 0, 0, 8) };
                title.Children.Add(new TextBlock { Text = sec.Icon, FontSize = 18, Margin = new Thickness(0, 0, 8, 0), VerticalAlignment = VerticalAlignment.Center });
                title.Children.Add(new TextBlock { Text = sec.Title, FontSize = 15, FontWeight = FontWeights.SemiBold, Foreground = accent, VerticalAlignment = VerticalAlignment.Center });
                inner.Children.Add(title);
                foreach (var it in sec.Items)
                {
                    var row = new Grid { Margin = new Thickness(0, 4, 0, 4) };
                    row.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(92) });
                    row.ColumnDefinitions.Add(new ColumnDefinition { Width = new GridLength(1, GridUnitType.Star) });
                    var chip = new Border { Background = chipBg, CornerRadius = new CornerRadius(5), Padding = new Thickness(6, 2, 6, 2), HorizontalAlignment = HorizontalAlignment.Left, VerticalAlignment = VerticalAlignment.Top };
                    chip.Child = new TextBlock { Text = it.Key, FontFamily = new System.Windows.Media.FontFamily("Consolas, Cascadia Mono"), FontSize = 12, FontWeight = FontWeights.SemiBold, Foreground = accent };
                    Grid.SetColumn(chip, 0);
                    var tx = new StackPanel();
                    tx.Children.Add(new TextBlock { Text = it.Title, FontWeight = FontWeights.SemiBold, Foreground = fg, FontSize = 13, TextWrapping = TextWrapping.Wrap });
                    tx.Children.Add(new TextBlock { Text = it.Desc, Foreground = dim, FontSize = 12, TextWrapping = TextWrapping.Wrap, Margin = new Thickness(0, 1, 0, 0) });
                    Grid.SetColumn(tx, 1);
                    row.Children.Add(chip);
                    row.Children.Add(tx);
                    inner.Children.Add(row);
                    rows.Add(Tuple.Create<FrameworkElement, string, FrameworkElement>(row, (it.Key + " " + it.Title + " " + it.Desc + " " + sec.Title).ToLowerInvariant(), card));
                }
                card.Child = inner;
                cards.Children.Add(card);
            }

            var search = new TextBox { Margin = new Thickness(0, 0, 0, 12), Padding = new Thickness(8, 5, 8, 5), FontSize = 13, Background = bg, Foreground = fg, BorderBrush = border };
            search.ToolTip = "機能名・キーで絞り込み (例: include, Alt+C, cpp)";
            search.TextChanged += (s, e) =>
            {
                string q = search.Text.Trim().ToLowerInvariant();
                var visibleCards = new HashSet<FrameworkElement>();
                foreach (var r in rows)
                {
                    bool show = q.Length == 0 || r.Item2.Contains(q);
                    r.Item1.Visibility = show ? Visibility.Visible : Visibility.Collapsed;
                    if (show) visibleCards.Add(r.Item3);
                }
                foreach (UIElement c in cards.Children) c.Visibility = visibleCards.Contains((FrameworkElement)c) ? Visibility.Visible : Visibility.Collapsed;
            };

            var heading = new StackPanel { Margin = new Thickness(0, 0, 0, 12) };
            heading.Children.Add(new TextBlock { Text = "K-CppAssist", FontSize = 24, FontWeight = FontWeights.Bold, Foreground = fg });
            heading.Children.Add(new TextBlock { Text = "ほとんどの機能は Alt+Enter (電球) でも出ます。キーを覚えなくても、カーソルを置いて Alt+Enter を押してください。", Foreground = dim, FontSize = 13, TextWrapping = TextWrapping.Wrap, Margin = new Thickness(0, 4, 0, 0) });

            var scroll = new ScrollViewer { VerticalScrollBarVisibility = ScrollBarVisibility.Auto, Content = cards };
            var web = new Button { Content = "詳しい説明 (Web) を開く", Padding = new Thickness(14, 5, 14, 5), Margin = new Thickness(0, 0, 8, 0) };
            var close = new Button { Content = "閉じる", IsDefault = true, IsCancel = true, Width = 80, Padding = new Thickness(0, 5, 0, 5) };
            var buttons = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Right, Margin = new Thickness(0, 12, 0, 0) };
            buttons.Children.Add(web);
            buttons.Children.Add(close);

            var top = new StackPanel();
            top.Children.Add(heading);
            top.Children.Add(search);
            var grid = new Grid { Margin = new Thickness(20, 16, 20, 16) };
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            Grid.SetRow(top, 0);
            Grid.SetRow(scroll, 1);
            Grid.SetRow(buttons, 2);
            grid.Children.Add(top);
            grid.Children.Add(scroll);
            grid.Children.Add(buttons);
            var w = new Window
            {
                Title = "K-CppAssist の使い方",
                Content = grid,
                Width = 860,
                Height = 720,
                Background = bg,
                FontFamily = font,
                WindowStartupLocation = WindowStartupLocation.CenterScreen,
            };
            web.Click += (s, e) =>
            {
                try { System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(DocsUrl) { UseShellExecute = true }); }
                catch (Exception ex) { Log("open docs failed: " + ex.Message); }
            };
            close.Click += (s, e) => w.Close();
            w.Loaded += (s, e) => search.Focus();
            w.ShowDialog();
        }
    }
}

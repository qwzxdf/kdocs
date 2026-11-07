using System;
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

        private const string HelpText =
@"■ 変数まわり
  Alt+Q   ローカル変数に型を付ける   count = 0;  →  int count = 0;
  Alt+W   メンバー変数として宣言する  cpp の stride_ = 1; から、ヘッダーのクラスに UINT stride_; を足す
  Alt+E   ゲッター・セッターを作る   ヘッダーのメンバー変数の行で押すと、public: の末尾に GetXxx / SetXxx を足す

■ #include
  Alt+F   #include を足す            カーソルの型名(std::vector、ComPtr、自作クラス)のヘッダーを、cpp / ヘッダーの先頭に足す
  Alt+D   #include を前方宣言にする  ヘッダーの #include ""x.h"" を class X; にして、#include を cpp に移す
          (ポインター・参照・shared_ptr だけで使っている型が対象)
  右クリック(プロジェクト / ソリューション) または 拡張機能 メニュー
          #include を整理（プロジェクト全体）／ 使っていない #include を消す（プロジェクト全体）
  拡張機能 メニュー
          このファイルの #include を整理

■ 宣言と定義
  Alt+G   宣言と定義の引数を合わせる  変えた側に、相手(開いていなくても)を合わせる。引数を変えると自動でも合う
  Alt+R   宣言・定義の相手を作る      ヘッダーの宣言から cpp の定義の雛形、cpp の定義からヘッダーの宣言
  Alt+M   関数を ヘッダー ⇄ cpp に移す  ヘッダーの本体を cpp へ / cpp の Class::Func の本体をヘッダーへ

■ ファイル名
  Alt+N   ファイル名をまとめて変える  ヘッダー・cpp の片方の名前を変えると、相手・#include・CMake も直す(自動でも動く)

■ その他
  Ctrl+.  電球(Quick Fix)に、上の機能が出る(カーソルの位置で使えるものだけ)
  自動    呼び出しの引数の個数チェック(make_unique / make_shared / new)、ビルド後のエラーログ(K-ErrorLog)
  拡張機能 → K-CppAssist の設定...  キーの変更、各機能の ON/OFF

注意: 使っていない #include の削除は、名前の使われ方だけで判断します。削除したあとは、ビルドして確かめてください。";

        private void ShowHelp()
        {
            ThreadHelper.ThrowIfNotOnUIThread();
            var text = new TextBox
            {
                Text = HelpText,
                IsReadOnly = true,
                FontFamily = new System.Windows.Media.FontFamily("Yu Gothic UI, Meiryo UI, Segoe UI"),
                FontSize = 13,
                TextWrapping = TextWrapping.Wrap,
                BorderThickness = new Thickness(0),
                VerticalScrollBarVisibility = ScrollBarVisibility.Auto,
                Margin = new Thickness(0, 0, 0, 8),
            };
            var web = new Button { Content = "詳しい説明(Web)を開く", Padding = new Thickness(12, 4, 12, 4), Margin = new Thickness(0, 0, 8, 0) };
            var close = new Button { Content = "閉じる", IsDefault = true, IsCancel = true, Width = 80 };
            var buttons = new StackPanel { Orientation = Orientation.Horizontal, HorizontalAlignment = HorizontalAlignment.Right };
            buttons.Children.Add(web);
            buttons.Children.Add(close);
            var grid = new Grid { Margin = new Thickness(12) };
            grid.RowDefinitions.Add(new RowDefinition { Height = new GridLength(1, GridUnitType.Star) });
            grid.RowDefinitions.Add(new RowDefinition { Height = GridLength.Auto });
            Grid.SetRow(text, 0);
            Grid.SetRow(buttons, 1);
            grid.Children.Add(text);
            grid.Children.Add(buttons);
            var w = new Window
            {
                Title = "K-CppAssist の使い方",
                Content = grid,
                Width = 820,
                Height = 640,
                WindowStartupLocation = WindowStartupLocation.CenterScreen,
            };
            web.Click += (s, e) =>
            {
                try { System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo(DocsUrl) { UseShellExecute = true }); }
                catch (Exception ex) { Log("open docs failed: " + ex.Message); }
            };
            close.Click += (s, e) => w.Close();
            w.ShowDialog();
        }
    }
}

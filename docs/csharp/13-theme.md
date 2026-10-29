---
title: 第 13 章 見た目のテーマを入れる
tags:
  - C#連携
---

# 第 13 章 見た目のテーマを入れる

第 11 章で、色に名前を付けた `Themes/Dark.xaml` を作りました。パネルの背景や文字の色は、これで暗くなります。ところが、`Button` や `ComboBox`、`TabControl` のような WPF の標準の部品は、白い見た目のままです。標準の部品は、`ControlTemplate` の中に色が書き込まれていて、リソースの色を変えても追従しないからです。

次の章から、`TextBox`、`Button`、`ListBox`、`ComboBox`、`DataGrid` といった標準の部品を、画面にどんどん置いていきます。そのたびに、暗いエディタの中に白いボタンが浮かぶことになります。部品を一つずつ作り直すのは現実的ではないので、先にまるごと見た目を変える**テーマ**を入れてしまいます。この章でやるのは、そのテーマの導入だけです。

!!! info "このページを読む前に"
    - [第 12 章 Prism の導入と起動の流れ](12-prism-bootstrap.md)（前の章。NuGet の入れ方と、書き換えた `App.xaml` が前提になる）
    - [第 11 章 スタイル、リソース、テンプレート、トリガー](11-style-template.md)（`Themes/Dark.xaml` と、標準の部品が暗くならない理由）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `App.xaml`（変更） | テーマを指定する |
    | `Editor.csproj`（変更） | 方法 2 を選んだときだけ、NuGet で `WPF-UI` を入れる |

## 選べる方法は 2 つある

テーマを入れる方法は、大きく 2 つです。

1 つ目は、.NET 9 から WPF に入った **Fluent テーマ**を使う方法です。Windows 11 風の見た目で、ライブラリを足す必要がなく、`App.xaml` に 1 つ属性を書くだけで済みます。ただし、.NET 9 以降が必要です。

2 つ目は、**テーマを提供するライブラリ**を NuGet で入れる方法です。.NET 8 でも使えて、見た目の選択肢も多くなります。そのかわり、依存するパッケージが 1 つ増えます。

使っている .NET が 9 以降なら、1 つ目で足ります。.NET 8 なら、2 つ目です。この章を終えたあとの手順は、どちらを選んでも同じです。

## 方法 1：Fluent テーマ（.NET 9 以降）

`Editor.csproj` の `TargetFramework` が `net9.0-windows` 以降になっているかを、まず確かめます。第 12 章で入れた Prism は、.NET 8 でも 9 以降でも動くので、ここは自分の環境のままで構いません。

`App.xaml` の `prism:PrismApplication` に、`ThemeMode` を書きます。

```xml title="App.xaml（変更：先頭のタグ）"
<prism:PrismApplication x:Class="Editor.App"
                        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                        xmlns:prism="http://prismlibrary.com/"
                        ThemeMode="Dark">
    <!-- Resources は、第 12 章のまま -->
```

`ThemeMode` には、4 つの値があります。`Dark` は暗い Fluent テーマ、`Light` は明るい Fluent テーマです。`System` は、Windows の設定（ライトモードかダークモードか）に合わせて自動で選びます。`None` は、これまでの標準の見た目（Aero2）のままにする指定で、何も書かないときの既定値でもあります。エディタは暗い配色を前提に作っているので、ここでは `Dark` にします。

`ThemeMode` はアプリ全体だけでなく、`Window` にも書けます。ウィンドウ単位で見た目を変えたいときに使います。ただし、アプリ全体で `None` 以外にしたあとは、ウィンドウ側で `None` に戻すことはできません。

コードから `Application.Current.ThemeMode = ThemeMode.Light;` のように切り替えることもできますが、この書き方はまだ実験的な機能で、そのままだと警告 `WPF0001` で止まります。切り替えの画面を作らない限り、XAML の指定だけで足ります。

Fluent テーマは、第 11 章の `Themes/Dark.xaml` と衝突しません。`Dark.xaml` で名前を付けた色は、自分で作ったパネルや文字にそのまま使われます。標準の部品のほうは、Fluent テーマが塗ります。

## 方法 2：WPF-UI を入れる（.NET 8 でも可）

テーマ ライブラリは何種類かありますが、ここでは **WPF-UI** を使います。Windows 11 風の見た目になり、NuGet で入れて、`App.xaml` に 2 行足すだけで済むからです。

1. 「NuGet パッケージの管理」で `WPF-UI` を探して、入れます（第 12 章の Prism と同じ手順です）。
2. `App.xaml` に、名前空間と、テーマの辞書を書きます。

```xml title="App.xaml（変更）"
<prism:PrismApplication x:Class="Editor.App"
                        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                        xmlns:prism="http://prismlibrary.com/"
                        xmlns:ui="http://schemas.lepo.co/wpfui/2022/xaml">
    <prism:PrismApplication.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ui:ThemesDictionary Theme="Dark" />
                <ui:ControlsDictionary />
                <ResourceDictionary Source="Themes/Dark.xaml" />
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </prism:PrismApplication.Resources>
</prism:PrismApplication>
```

`xmlns:ui` は、WPF-UI の部品に `ui:` という接頭辞を付ける宣言です。第 12 章の `xmlns:prism` と同じ働きです。

`ui:ThemesDictionary` は色の一式を読み込むもので、`Theme` に `Dark` か `Light` を書きます。`ui:ControlsDictionary` は、`Button` や `ComboBox` などの標準の部品の見た目を差し替える辞書です。色だけ読み込んで、この 2 つ目を忘れると、色の名前は使えるのに、部品の見た目が変わりません。

自分で作った `Themes/Dark.xaml` を最後に置いているのは、辞書の並びの後ろに書いたものが優先されるからです。ライブラリの色と同じ名前を、自分の辞書で上書きしたいときは、あとに置きます。

ほかにも、MaterialDesignInXamlToolkit（Material Design 風）、MahApps.Metro（Metro 風のウィンドウ）、HandyControl（多数の部品入り）などがあります。どれも、NuGet で入れて、`MergedDictionaries` に読み込む形は同じです。導入の細かい手順は、各ライブラリの README に書かれているので、使う前に確かめてください。

## 動かして確かめる

`F5` で実行して、次を確かめます。

- メニュー、ステータス バー、下のタブが、暗い配色になっている。
- 第 11 章までは白かった、メニューの項目やタブの見出しが、暗い配色に変わっている。
- 自分で作った左右のパネルは、これまでと同じ色のまま。

??? failure "`ThemeMode` が見つからないというエラーになる"
    .NET 8 以前では、`ThemeMode` という属性がありません。`Editor.csproj` の `TargetFramework` を確かめてください。.NET 8 を使い続けるなら、方法 2 にします。

??? failure "WPF-UI を入れたのに、部品が白いまま"
    `ui:ControlsDictionary` を書き忘れていないかを確かめます。`ThemesDictionary` だけでは、色の名前が使えるようになるだけで、標準の部品の見た目は変わりません。

??? failure "ウィンドウの背景だけが白く残る"
    ウィンドウの `Background` が、直接指定されていないかを確かめます。Editor の `MainWindow` は、`Background="#FF1E1E1E"` を直接書いているので、テーマの影響を受けません。テーマの色に合わせたいときは、`Themes/Dark.xaml` の `Window.Background` を `DynamicResource` で指定します。

## ここまでの Editor

```text
Editor/
├─ App.xaml / App.xaml.cs        テーマの指定を足した（ThemeMode か WPF-UI）
├─ MainWindow.xaml(.cs)
├─ MainWindowViewModel.cs
└─ Themes/Dark.xaml
```

## この章のまとめ

- 標準の部品は `ControlTemplate` に色が書き込まれているので、色のリソースだけでは暗くならない。
- .NET 9 以降なら、`App.xaml` に `ThemeMode="Dark"` と書くだけで、Fluent テーマが入る。
- .NET 8 なら、WPF-UI のようなテーマ ライブラリを NuGet で入れて、`ThemesDictionary` と `ControlsDictionary` を読み込む。
- 自分で作った `Themes/Dark.xaml` は、テーマの辞書のあとに置く。

## 関連する章

- [第 11 章 スタイル、リソース、テンプレート、トリガー](11-style-template.md)：リソースと `ControlTemplate`。なぜ色だけでは足りないか
- [第 12 章 Prism の導入と起動の流れ](12-prism-bootstrap.md)：NuGet の入れ方と `App.xaml` の書き換え

次の章から、画面にデータをつないでいきます。標準の部品が暗くなったので、見た目を気にせずに作れます。

[第 14 章 データバインディングと MVVM](14-binding-mvvm.md) へ進みます。

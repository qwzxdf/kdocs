---
title: 第 23 章 アプリの基本（起動・終了・ウィンドウ・コマンド）
tags:
  - C#連携
---

# 第 23 章 アプリの基本（起動・終了・ウィンドウ・コマンド）

本編では、画面とビューモデルの話が中心でした。この章では、その周りにあるアプリそのものの話をまとめます。起動と終了で何が起きるか、ウィンドウの種類、複数のウィンドウを扱う方法、ウィンドウの位置や大きさを覚えておく方法、そして WPF 標準のコマンド（コピー、貼り付けなど）です。

## 起動と終了の流れ

`App.xaml`（`Application` クラス）には、アプリ全体の出来事に対応するイベントや関数があります。

| 名前 | いつ |
| --- | --- |
| `OnStartup` / `Startup` | アプリが起動して、最初のウィンドウを開く前 |
| `OnExit` / `Exit` | アプリが終了するとき |
| `DispatcherUnhandledException` | UI スレッドで、誰も捕まえなかった例外が出たとき（第 44 章） |
| `Activated` / `Deactivated` | アプリがアクティブになった / 非アクティブになった |
| `SessionEnding` | Windows のログオフやシャットダウン |

Prism を使うときは、`OnStartup` の代わりに `PrismApplication` の `OnInitialized` などを使います（第 16 章）。

### いつアプリが終わるか

アプリがいつ終了するかは、`ShutdownMode` で決まります。

| 値 | 終了するとき |
| --- | --- |
| `OnLastWindowClose` | 最後のウィンドウが閉じたとき（既定） |
| `OnMainWindowClose` | メイン ウィンドウが閉じたとき |
| `OnExplicitShutdown` | `Application.Current.Shutdown()` を呼んだとき |

ダイアログを閉じたら、アプリごと終了してしまう、という現象は、メインのつもりのウィンドウが、実は最後のウィンドウだったときに起きます。`OnMainWindowClose` にして対処します。

## ウィンドウの種類

| 種類 | 用途 |
| --- | --- |
| `Window` | 通常のウィンドウ |
| `NavigationWindow`、`Page`、`Frame` | ページ遷移を使うアプリ（Web のように「戻る」「進む」）。エディタでは Prism のリージョン ナビゲーションを使うので、ほぼ使わない |
| ダイアログ | `Window` を `ShowDialog()` で開いたもの。Prism では `IDialogService` |

### 別のウィンドウを開く

ビューモデルから `new Window()` と書くのは、ビューを知ってしまうので避けます。第 18 章の `IDialogService` か、ナビゲーション、または自作のウィンドウ サービスで開きます。

```csharp
public interface IWindowService
{
    void ShowToolWindow<TView>() where TView : Window;
}
```

実装は、DI コンテナーから `TView` を `Resolve` して、`Show()` するだけです。

### ウィンドウの重なり

| プロパティ | 意味 |
| --- | --- |
| `Owner` | 親のウィンドウ。親が最小化されると、一緒に最小化される。子は親の手前に表示される |
| `Topmost` | 常に最前面 |
| `ShowInTaskbar` | タスク バーにボタンを出すか |
| `WindowStartupLocation` | 開く位置（`CenterScreen`、`CenterOwner`） |
| `ResizeMode` | 大きさを変えられるか |
| `WindowStyle` | タイトル バーの形式。`None` で枠なし |

## ウィンドウの位置と大きさを覚える

エディタを閉じて、また開いたときに、前回と同じ位置と大きさで出てほしい。これは、設定ファイルに保存して実現します（第 39 章の設定の保存と同じ要領）。

```csharp
public class WindowPlacement
{
    public double Left { get; set; }
    public double Top { get; set; }
    public double Width { get; set; }
    public double Height { get; set; }
    public WindowState State { get; set; }
}
```

```csharp
// 閉じるとき
var p = new WindowPlacement
{
    Left = RestoreBounds.Left, Top = RestoreBounds.Top,
    Width = RestoreBounds.Width, Height = RestoreBounds.Height,
    State = WindowState,
};
```

最大化したまま保存すると、`Left` / `Width` が画面いっぱいの値になって、復元したときに不自然になります。`RestoreBounds` は、最大化・最小化の前の、通常状態での位置と大きさを返してくれます。

復元するときは、保存された位置が、今の画面の外（外したモニターの上など）になっていないかを確かめます。

```csharp
var screen = SystemParameters.VirtualScreenLeft;     // すべてのモニターを含む領域の左端
bool visible = p.Left < SystemParameters.VirtualScreenWidth && p.Top < SystemParameters.VirtualScreenHeight;
```

## WPF 標準のコマンド

`ICommand` のうち、WPF に最初から用意されているものがあります。

| コマンド | 意味 |
| --- | --- |
| `ApplicationCommands.Copy`、`Cut`、`Paste` | コピー、切り取り、貼り付け |
| `ApplicationCommands.Undo`、`Redo` | 元に戻す、やり直し |
| `ApplicationCommands.Save`、`Open`、`New` | 保存、開く、新規 |
| `ApplicationCommands.Delete`、`SelectAll` | 削除、すべて選択 |
| `NavigationCommands.BrowseBack` | 戻る |

`TextBox` は、`Copy`、`Cut`、`Paste`、`Undo` を最初から処理できます。メニューやボタンの `Command` に指定するだけで、コピー貼り付けが動きます。

```xml
<MenuItem Header="コピー" Command="ApplicationCommands.Copy" />
<MenuItem Header="貼り付け" Command="ApplicationCommands.Paste" />
```

コマンドが、フォーカスのある部品に伝わって実行されるので、`TextBox` を選んでいる間だけ、有効になります。

これは「ルーテッド コマンド」という仕組みで、ビューモデルのコマンド（`DelegateCommand`）とは別物です。`ApplicationCommands.Undo` をエディタのシーンの Undo に使いたい場合は、`CommandBinding` で自分の処理に結び付けます。

```xml
<Window.CommandBindings>
    <CommandBinding Command="ApplicationCommands.Undo"
                    Executed="OnUndoExecuted" CanExecute="OnUndoCanExecute" />
</Window.CommandBindings>
```

ただし、MVVM のアプリは、ビューモデルのコマンドで統一するほうが簡単なので、第 38 章の `UndoCommand` のように、自分で定義したコマンドを使っています。`TextBox` の中での `Ctrl + Z` が、標準のコマンドで優先されるのは、この仕組みのためです。

## アプリの設定を保存する

アプリの設定（ウィンドウの位置、最近開いたファイルなど）の保存先は、いくつかあります。

| 方法 | 内容 |
| --- | --- |
| `%APPDATA%` に JSON を保存 | この教材（第 39 章）の方法。形式が自由で、読みやすい |
| `Properties.Settings` | .NET Framework 時代の標準。`.NET` でも使えるが、手作業の設定が増える |
| レジストリ | 古い方法。避ける |
| アプリのフォルダー | インストール先が書き込み不可のことがあり、避ける |

ユーザーごとの設定は `%APPDATA%`（`Environment.SpecialFolder.ApplicationData`）、ログやキャッシュは `%LOCALAPPDATA%`（`LocalApplicationData`）に置くのが慣習です。

## この章のまとめ

- `App` には、起動・終了・未処理の例外のフックがある。終了のタイミングは `ShutdownMode` で変えられる。
- ウィンドウの開閉は、ビューモデルから直接 `new` せず、サービスやダイアログ サービスを通す。
- ウィンドウの位置は `RestoreBounds` で保存し、復元時に画面内かを確かめる。
- 標準の `ApplicationCommands` は、`TextBox` のコピー貼り付けなどに便利。ビューモデルのコマンドとは別の仕組み。

次の章では、控えめなアニメーションの付け方を扱い、WPF の学習をしめくくります。

[第 24 章 アニメーション](24-animation.md) へ進みます。

---
title: 第 29 章 アプリの基本（起動・終了・ウィンドウ・コマンド）
tags:
  - C#連携
---

# 第 29 章 アプリの基本（起動・終了・ウィンドウ・コマンド）

本編では、画面とビューモデルの話が中心でした。この章では、その周りにあるアプリそのものの話をまとめます。起動と終了で何が起きるか、ウィンドウの種類、複数のウィンドウを扱う方法、ウィンドウの位置や大きさを覚えておく方法、そして WPF 標準のコマンド（コピー、貼り付けなど）です。

!!! info "このページを読む前に"
    - [第 28 章 コードビハインドを減らす（Behaviors）](28-behaviors.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Shared/WindowPlacementStore.cs`（新規） | ウィンドウの位置と大きさを、保存して復元する |
    | `MainWindow.xaml.cs`（変更） | 起動時に復元し、閉じるときに保存する |
    | `App.xaml.cs`（変更） | 二重に起動しないようにする |

    ほかの節は、必要になったときに引く、アプリの基本の紹介です。

## 起動と終了の流れ

`App.xaml`（`Application` クラス）には、アプリ全体の出来事に対応するイベントや関数があります。

| 名前 | いつ |
| --- | --- |
| `OnStartup` / `Startup` | アプリが起動して、最初のウィンドウを開く前 |
| `OnExit` / `Exit` | アプリが終了するとき |
| `DispatcherUnhandledException` | UI スレッドで、誰も捕まえなかった例外が出たとき（第 50 章） |
| `Activated` / `Deactivated` | アプリがアクティブになった / 非アクティブになった |
| `SessionEnding` | Windows のログオフやシャットダウン |

Prism を使うときは、`OnStartup` の代わりに `PrismApplication` の `OnInitialized` などを使います（第 12 章）。

### いつアプリが終わるか

アプリがいつ終了するかは、`ShutdownMode` で決まります。

| 値 | 終了するとき |
| --- | --- |
| `OnLastWindowClose` | 最後のウィンドウが閉じたとき（既定） |
| `OnMainWindowClose` | メイン ウィンドウが閉じたとき |
| `OnExplicitShutdown` | `Application.Current.Shutdown()` を呼んだとき |

ダイアログを閉じたら、アプリごと終了してしまう、という現象は、メインのつもりのウィンドウが実は最後のウィンドウだったときに起きます。`OnMainWindowClose` にして対処します。

## ウィンドウの種類

| 種類 | 用途 |
| --- | --- |
| `Window` | 通常のウィンドウ |
| `NavigationWindow`、`Page`、`Frame` | ページ遷移を使うアプリ（Web のように「戻る」「進む」）。エディタでは Prism のリージョン ナビゲーションを使うので、ほぼ使わない |
| ダイアログ | `Window` を `ShowDialog()` で開いたもの。Prism では `IDialogService` |

### 別のウィンドウを開く

ビューモデルから `new Window()` と書くのは、ビューを知ってしまうので避けます。第 24 章の `IDialogService` か、ナビゲーション、または自作のウィンドウ サービスで開きます。

```csharp title="実験（Editor には入れない）"
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

エディタを閉じて、また開いたときに、前回と同じ位置と大きさで出てほしい。これは、設定ファイルに保存して実現します（第 45 章の設定の保存と同じ要領）。保存の置き場所は、ユーザーごとの設定なので `%APPDATA%` にします。

```csharp title="Shared/WindowPlacementStore.cs（新規）"
using System.IO;
using System.Text.Json;
using System.Windows;

namespace Editor.Shared;

public class WindowPlacement
{
    public double Left { get; set; }
    public double Top { get; set; }
    public double Width { get; set; }
    public double Height { get; set; }
    public WindowState State { get; set; }
}

public static class WindowPlacementStore
{
    private static readonly string s_path = Path.Combine(
        Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData),
        "MiniEngine", "Editor", "window.json");

    public static void Save(Window window)
    {
        var b = window.RestoreBounds;      // 最大化・最小化の前の、通常状態の位置と大きさ
        var p = new WindowPlacement
        {
            Left = b.Left, Top = b.Top, Width = b.Width, Height = b.Height,
            State = window.WindowState == WindowState.Minimized ? WindowState.Normal : window.WindowState,
        };
        Directory.CreateDirectory(Path.GetDirectoryName(s_path)!);
        File.WriteAllText(s_path, JsonSerializer.Serialize(p));
    }

    public static void Restore(Window window)
    {
        if (!File.Exists(s_path)) return;

        WindowPlacement? p;
        try { p = JsonSerializer.Deserialize<WindowPlacement>(File.ReadAllText(s_path)); }
        catch (JsonException) { return; }
        if (p is null) return;

        // 保存された位置が、今の画面の外（外したモニターの上など）なら、使わない
        if (p.Left >= SystemParameters.VirtualScreenLeft + SystemParameters.VirtualScreenWidth
            || p.Top >= SystemParameters.VirtualScreenTop + SystemParameters.VirtualScreenHeight
            || p.Left + p.Width <= SystemParameters.VirtualScreenLeft
            || p.Top + p.Height <= SystemParameters.VirtualScreenTop)
            return;

        window.WindowStartupLocation = WindowStartupLocation.Manual;
        window.Left = p.Left;
        window.Top = p.Top;
        window.Width = p.Width;
        window.Height = p.Height;
        window.WindowState = p.State;
    }
}
```

最大化したまま保存すると、`Left` / `Width` が画面いっぱいの値になって、復元したときに不自然になります。`RestoreBounds` は、最大化・最小化の前の、通常状態での位置と大きさを返してくれます。そのため、状態は `State` に別に持ち、位置と大きさは `RestoreBounds` から取っています。

`SystemParameters.VirtualScreen...` は、すべてのモニターを含む領域です。保存された位置がこの外にあるときは、復元しないで、既定の位置で開きます。

呼ぶのは、ウィンドウ自身のコードビハインドです。ウィンドウの大きさや位置は、画面そのものの話なので、ビューモデルではなく、ビューに書いて構いません（第 14 章の表のとおりです）。

```csharp title="MainWindow.xaml.cs（変更）"
public MainWindow()
{
    InitializeComponent();
    WindowPlacementStore.Restore(this);
    Closing += (_, _) => WindowPlacementStore.Save(this);
}
```

ウィンドウを動かして閉じ、また起動すると、同じ位置と大きさで出ます。

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

```xml title="実験（Editor には入れない）"
<MenuItem Header="コピー" Command="ApplicationCommands.Copy" />
<MenuItem Header="貼り付け" Command="ApplicationCommands.Paste" />
```

コマンドがフォーカスのある部品に伝わって実行されるので、`TextBox` を選んでいる間だけ、有効になります。

これは「ルーテッド コマンド」という仕組みで、ビューモデルのコマンド（`DelegateCommand`）とは別物です。`ApplicationCommands.Undo` をエディタのシーンの Undo に使いたい場合は、`CommandBinding` で自分の処理に結び付けます。

```xml title="実験（Editor には入れない）"
<Window.CommandBindings>
    <CommandBinding Command="ApplicationCommands.Undo"
                    Executed="OnUndoExecuted" CanExecute="OnUndoCanExecute" />
</Window.CommandBindings>
```

ただし、MVVM のアプリは、ビューモデルのコマンドで統一するほうが簡単なので、第 44 章の `UndoCommand` のように、自分で定義したコマンドを使っています。`TextBox` の中での `Ctrl + Z` が、標準のコマンドで優先されるのは、この仕組みのためです。

## アプリの設定を保存する

アプリの設定（ウィンドウの位置、最近開いたファイルなど）の保存先は、いくつかあります。

| 方法 | 内容 |
| --- | --- |
| `%APPDATA%` に JSON を保存 | この教材（第 45 章）の方法。形式が自由で、読みやすい |
| `Properties.Settings` | .NET Framework 時代の標準。`.NET` でも使えるが、手作業の設定が増える |
| レジストリ | 古い方法。避ける |
| アプリのフォルダー | インストール先が書き込み不可のことがあり、避ける |

ユーザーごとの設定は `%APPDATA%`（`Environment.SpecialFolder.ApplicationData`）、ログやキャッシュは `%LOCALAPPDATA%`（`LocalApplicationData`）に置くのが慣習です。

## キーボードとフォーカス

エディタは、マウスだけでなく、キーボードでも操作されます。プロパティ パネルで、X に数字を打ち込んで `Tab` で Y へ進み、また打ち込む、という流れが途切れないようにしておきます。

### Tab で動く順番

`Tab` を押したときの移動先は、基本的に XAML に書いた順（論理ツリーの順）です。順番を変えたいときは、`TabIndex` を使います。小さい値から順に移ります。

```xml title="実験（Editor には入れない）"
<StackPanel KeyboardNavigation.TabNavigation="Cycle">
    <TextBox x:Name="PositionX" TabIndex="0" />
    <TextBox x:Name="PositionY" TabIndex="1" />
    <TextBox x:Name="PositionZ" TabIndex="2" />
    <TextBlock Text="単位: m" IsTabStop="False" />
</StackPanel>
```

| プロパティ | 意味 |
| --- | --- |
| `TabIndex` | `Tab` で移る順番。小さい順 |
| `IsTabStop` | `false` にすると、`Tab` で止まらない。ラベルや装飾の部品に使う |
| `KeyboardNavigation.TabNavigation` | `Tab` の動き方。`Cycle`（最後まで行ったら最初へ戻る）、`Continue`（外側へ続ける）、`Once`（このグループでは 1 回だけ止まる）、`None` |
| `KeyboardNavigation.DirectionalNavigation` | 矢印キーでの移動 |
| `Focusable` | `false` にすると、そもそもフォーカスを受け取らない |

`TabIndex` は、同じ親の中でだけ比べられます。親が違う部品どうしの順番は、親の `TabIndex` で決まります。

### フォーカスを移す

画面が開いたときに入力欄へカーソルを置く、のようにフォーカスを移したいときは、`Focus()` を呼ぶか、XAML で `FocusManager.FocusedElement` を指定します。

```xml title="実験（Editor には入れない）"
<Window FocusManager.FocusedElement="{Binding ElementName=NameBox}">
    <TextBox x:Name="NameBox" />
</Window>
```

コードビハインドで `Focus()` を呼ぶときは、画面が出来上がったあとで呼ばないと効かないことがあります。`Loaded` イベントの中で呼んでください。

```csharp title="実験（Editor には入れない）"
Loaded += (_, _) => NameBox.Focus();
```

### アクセス キー

ラベルに `_` を付けると、`Alt` と組み合わせたキーで、そのラベルの部品へ移れます。メニューの `ファイル(_F)` と同じ仕組みです。入力欄の横のラベルには、`Label` を使います。

```xml title="実験（Editor には入れない）"
<Label Content="名前(_N)" Target="{Binding ElementName=NameBox}" />
<TextBox x:Name="NameBox" />
```

`Alt + N` で、`NameBox` にフォーカスが移ります。`Target` で「ラベルが指す部品」を結ぶのが大事です。

### ショートカットと入力欄がぶつかる

`Delete` や `F2` のようなキーを `InputBindings` に登録すると、入力欄で文字を消そうとしただけで、「オブジェクトを削除」が動くことがあります。`TextBox` は `Delete` や `Backspace` を処理済みにするので、多くは問題になりませんが、`Ctrl + Z` のように、入力欄にも別の意味を持つキーは、衝突しやすいです。

衝突を避けるには、次のいずれかにします。

- コマンドの `CanExecute` で、フォーカスが入力欄にあるときは `false` を返す。
- 登録する場所をリストやツリーといった「文字を打たない部品」の `InputBindings` に限る（第 28 章）。

## ポップアップ、ツールチップ

画面の上に一時的に何かを浮かべる部品は 3 つあります。

| 部品 | 使いどころ |
| --- | --- |
| `ToolTip` | マウスを載せたときの説明。`ToolTip="保存 (Ctrl+S)"` と書くだけ |
| `ContextMenu` | 右クリックのメニュー |
| `Popup` | 自由な中身を浮かべる。`IsOpen` で開閉する |

`ToolTip` は、短い説明なら文字列、中身を作り込みたいなら要素を入れます。表示されるまでの時間は、`ToolTipService` で調整します。

```xml title="実験（Editor には入れない）"
<Button Content="保存" ToolTipService.InitialShowDelay="300">
    <Button.ToolTip>
        <StackPanel>
            <TextBlock FontWeight="Bold" Text="保存" />
            <TextBlock Text="現在のシーンをファイルに書き出します。(Ctrl+S)" />
        </StackPanel>
    </Button.ToolTip>
</Button>
```

`Popup` は、`IsOpen` をバインドして開閉します。

```xml title="実験（Editor には入れない）"
<ToggleButton x:Name="FilterButton" Content="絞り込み" />
<Popup IsOpen="{Binding IsChecked, ElementName=FilterButton}"
       PlacementTarget="{Binding ElementName=FilterButton}"
       Placement="Bottom" StaysOpen="False">
    <Border Background="{DynamicResource Panel.Background}" Padding="8">
        <TextBox Width="160" />
    </Border>
</Popup>
```

`Placement` は、`PlacementTarget` から見てどこに出すか、`StaysOpen="False"` は、外をクリックしたら閉じる、という指定です。`Popup` は、別のウィンドウとして描かれるので、ほかの部品の後ろに隠れず、親の `Clip` にも切られません。そのかわり、親の `DataContext` やリソースを自動では引き継がない場合があります。見た目が崩れたときは、`Popup` の中身に `DynamicResource` で色を指定しているか、確かめてください。

## 二重に起動させない

エディタは、同じものを 2 つ起動されると困ることがあります（同じプロジェクト ファイルを 2 つが同時に書く、など）。Windows の `Mutex`（名前付きの排他オブジェクト）で、起動済みかどうかを確かめます。

```csharp title="App.xaml.cs（変更）"
public partial class App : PrismApplication
{
    private Mutex? _mutex;
    private bool _ownsMutex;

    protected override void OnStartup(StartupEventArgs e)
    {
        // 名前は、他のアプリと重ならない一意な文字列にする
        _mutex = new Mutex(initiallyOwned: true, "MiniEngine.Editor.SingleInstance", out _ownsMutex);
        if (!_ownsMutex)
        {
            MessageBox.Show("MiniEngine Editor は、すでに起動しています。");
            Shutdown();
            return;
        }
        base.OnStartup(e);
    }

    protected override void OnExit(ExitEventArgs e)
    {
        if (_ownsMutex) _mutex?.ReleaseMutex();   // 持っていないものを解放すると例外になる
        _mutex?.Dispose();
        base.OnExit(e);
    }
}
```

`out` で受けた値（`_ownsMutex`）が `false` なら、同じ名前の `Mutex` が、すでにほかのプロセスに作られています。この場合は、`base.OnStartup` を呼ばないで終わります。`PrismApplication` の起動処理（コンテナーの作成など）を無駄に走らせないためです。

すでに起動している側のウィンドウを前に出したいときは、`Process.GetProcessesByName` で相手を探して `SetForegroundWindow` を呼ぶ方法がありますが、ここでは扱いません。

??? failure "ウィンドウを閉じたのに、プロセスが残る"
    ほかのウィンドウが開いたままか、非表示になっているだけで閉じられていない可能性があります。既定の `ShutdownMode` は `OnLastWindowClose` なので、最後のウィンドウが閉じられたときに終了しますが、`Hide()` しただけのウィンドウは「開いている」と数えられます。また、`ShutdownMode` を `OnExplicitShutdown` にしていると、`Shutdown()` を呼ぶまで終わりません。バックグラウンドのスレッドが残っているときも終了しないので、第 51 章を見てください。

## この章のまとめ

- `App` には、起動・終了・未処理の例外のフックがある。終了のタイミングは `ShutdownMode` で変えられる。
- ウィンドウの開閉は、ビューモデルから直接 `new` せず、サービスやダイアログ サービスを通す。
- ウィンドウの位置は `RestoreBounds` で保存し、復元時に画面内かを確かめる。
- キーボードの移動は `TabIndex` と `IsTabStop`、フォーカスは `Focus()` を `Loaded` のあとで呼ぶ。入力欄とショートカットの衝突に注意する。
- 一時的に浮かべる物は、`ToolTip`、`ContextMenu`、`Popup`。二重起動は、名前付きの `Mutex` で防ぐ。
- 標準の `ApplicationCommands` は、`TextBox` のコピー貼り付けなどに便利。ビューモデルのコマンドとは別の仕組み。

次の章では、控えめなアニメーションの付け方を扱い、WPF の学習をしめくくります。

[第 30 章 アニメーション](30-animation.md) へ進みます。

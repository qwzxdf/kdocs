---
title: 第 17 章 リージョン、モジュール、ナビゲーション
tags:
  - C#連携
---

# 第 17 章 リージョン、モジュール、ナビゲーション

第 6 章の `MainWindow.xaml` には、シーン ツリーも、プロパティも、アセットも、全部を直接書きました。機能が増えるにつれて、このファイルはどんどん太ります。複数の人が同時に触ればぶつかりますし、どの機能のコードがどこにあるのかも分かりにくくなります。

!!! info "このページを読む前に"
    - [第 16 章 Prism の導入と起動の流れ](16-prism-bootstrap.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


そこでこの章では、`MainWindow` を「枠だけ」にして、中身は機能ごとに別々の場所から差し込む形に作り直します。使うのは Prism のリージョンとモジュールです。

## 考え方：枠に名前を付けて、中身はあとから差し込む

`MainWindow` には、名前の付いた空きスペース（リージョン）だけを置きます。中身のビューは、各機能が自分で「このリージョンに、私の画面を出してください」と登録します。

```text
MainWindow（枠だけ）
┌──────────────────────────────────────────────┐
│ [SceneTreeRegion] [ViewportRegion] [PropertyRegion] │
│                   [BottomRegion]                    │
└──────────────────────────────────────────────┘
        ▲                ▲                ▲
  SceneTree モジュール  Viewport モジュール  Property モジュール
  （自分のビューを差し込む）
```

| 言葉 | 意味 |
| --- | --- |
| リージョン | 画面の中の、名前の付いた空きスペース |
| ビュー | リージョンに差し込む部品。たいていは `UserControl` |
| リージョン マネージャー | リージョンとビューの対応を管理する（`IRegionManager`） |
| モジュール | 機能のまとまり。ビューやサービスの登録を、まとめて行う |

`MainWindow` は、どんなビューが入るのかを知りません。リージョンの名前だけで中身とつながるので、機能を足したり外したりしても `MainWindow` は変わりません。

## リージョンの名前を決める

リージョンの名前は文字列ですが、タイプミスを避けるために定数にまとめます。

```csharp title="Infrastructure/RegionNames.cs"
namespace Editor.Infrastructure;

public static class RegionNames
{
    public const string SceneTree = "SceneTreeRegion";
    public const string Viewport = "ViewportRegion";
    public const string Property = "PropertyRegion";
    public const string Bottom = "BottomRegion";
}
```

`static class` は、インスタンスを作れず、`static` なメンバーだけを持つクラスです。`const` は、コンパイル時に決まる定数です。

## MainWindow を枠にする

第 6 章のレイアウトはそのままに、中身をリージョンに置き換えます。

```xml title="Views/MainWindow.xaml"
<Window x:Class="Editor.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:prism="http://prismlibrary.com/"
        xmlns:infra="clr-namespace:Editor.Infrastructure"
        prism:ViewModelLocator.AutoWireViewModel="True"
        Title="{Binding Title}" Height="720" Width="1280">
    <DockPanel>
        <Menu DockPanel.Dock="Top">
            <!-- 第 6 章のメニュー -->
        </Menu>
        <StatusBar DockPanel.Dock="Bottom">
            <StatusBarItem Content="{Binding StatusText}" />
        </StatusBar>

        <Grid>
            <Grid.ColumnDefinitions>
                <ColumnDefinition Width="240" MinWidth="120" />
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="*" MinWidth="200" />
                <ColumnDefinition Width="Auto" />
                <ColumnDefinition Width="300" MinWidth="160" />
            </Grid.ColumnDefinitions>

            <ContentControl Grid.Column="0"
                prism:RegionManager.RegionName="{x:Static infra:RegionNames.SceneTree}" />
            <GridSplitter Grid.Column="1" Width="4" HorizontalAlignment="Stretch" />

            <Grid Grid.Column="2">
                <Grid.RowDefinitions>
                    <RowDefinition Height="*" MinHeight="120" />
                    <RowDefinition Height="Auto" />
                    <RowDefinition Height="200" MinHeight="60" />
                </Grid.RowDefinitions>
                <ContentControl Grid.Row="0"
                    prism:RegionManager.RegionName="{x:Static infra:RegionNames.Viewport}" />
                <GridSplitter Grid.Row="1" Height="4" HorizontalAlignment="Stretch" />
                <TabControl Grid.Row="2"
                    prism:RegionManager.RegionName="{x:Static infra:RegionNames.Bottom}" />
            </Grid>

            <GridSplitter Grid.Column="3" Width="4" HorizontalAlignment="Stretch" />
            <ContentControl Grid.Column="4"
                prism:RegionManager.RegionName="{x:Static infra:RegionNames.Property}" />
        </Grid>
    </DockPanel>
</Window>
```

`MainWindowViewModel` には、ステータス バーに出す文字を足します。

```csharp
private string _statusText = "準備完了";
public string StatusText
{
    get => _statusText;
    set => SetProperty(ref _statusText, value);
}
```

`prism:RegionManager.RegionName` は添付プロパティで、これを付けた部品が「その名前のリージョン」になります。`{x:Static ...}` は、`static` な定数を XAML から参照するマークアップ拡張で、文字列をベタ書きしないで済みます。

リージョンにできる部品の種類で、ビューの並び方が変わります。

| 部品 | 並び方 | こんなときに |
| --- | --- | --- |
| `ContentControl` | 1 つだけ。新しく入れると置き換わる | ビューポート、プロパティ |
| `ItemsControl` | 全部が縦に並ぶ | ツール バーのような並び |
| `TabControl` | タブになる | 下のパネル（アセット、ログ） |
| `ComboBox` | ドロップダウンで選ぶ | 切り替え式の入力 |

## ビューを作る

各機能の画面は `UserControl` で作ります。`Window` のような外枠を持たず、他の画面の中に入れて使える小さな画面です。

1. `Editor` に `Modules\SceneTree` フォルダーを作り、中に `Views` と `ViewModels` を作ります。
2. `Views` を右クリックして「追加 → 新しい項目 → ユーザー コントロール (WPF)」で `SceneTreeView.xaml` を作ります。

```xml title="Modules/SceneTree/Views/SceneTreeView.xaml"
<UserControl x:Class="Editor.Modules.SceneTree.Views.SceneTreeView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:prism="http://prismlibrary.com/"
             prism:ViewModelLocator.AutoWireViewModel="True">
    <Border Background="#FF252526">
        <StackPanel Margin="8">
            <TextBlock Text="シーン ツリー" FontWeight="Bold" />
            <TextBlock Text="{Binding Message}" Margin="0,8,0,0" />
        </StackPanel>
    </Border>
</UserControl>
```

```csharp title="Modules/SceneTree/ViewModels/SceneTreeViewModel.cs"
using Prism.Mvvm;

namespace Editor.Modules.SceneTree.ViewModels;

public class SceneTreeViewModel : BindableBase
{
    public string Message => "（ここにシーンの木が出ます）";
}
```

フォルダーに合わせて名前空間が `...SceneTree.Views` / `...SceneTree.ViewModels` になるので、ViewModelLocator の規則にもちゃんと合います。

同じようにして `Property`（`PropertyView`）、`Asset`（`AssetView`）、`Log`（`LogView`）も作ります。中身は今のところタイトルだけで構いません。

## モジュールを作る

モジュールは `IModule` を実装したクラスです。やることは 2 つあります。

```csharp title="Modules/SceneTree/SceneTreeModule.cs"
using Prism.Ioc;
using Prism.Modularity;
using Prism.Regions;

using Editor.Infrastructure;
using Editor.Modules.SceneTree.Views;

namespace Editor.Modules.SceneTree;

public class SceneTreeModule : IModule
{
    // ① DI コンテナーに、このモジュールの型を登録する
    public void RegisterTypes(IContainerRegistry containerRegistry)
    {
    }

    // ② 全モジュールの登録が終わったあとに呼ばれる。ビューをリージョンに登録する
    public void OnInitialized(IContainerProvider containerProvider)
    {
        var regionManager = containerProvider.Resolve<IRegionManager>();
        regionManager.RegisterViewWithRegion(RegionNames.SceneTree, typeof(SceneTreeView));
    }
}
```

`RegisterTypes` が先に全モジュール分実行されて、そのあとに `OnInitialized` が実行されます。ほかのモジュールが登録した型を使うような処理は、`OnInitialized` に書きます。

`RegisterViewWithRegion` は、「このリージョンが作られたら、このビューを自動で差し込んでください」という登録です。`typeof(SceneTreeView)` は、型そのものを表す式です。

`PropertyModule`（`RegionNames.Property`）、`AssetModule`、`LogModule`（どちらも `RegionNames.Bottom`）も同じ形で作ります。下のパネル（`TabControl`）に 2 つ登録すると、2 つのタブになります。

### タブの見出しを付ける

`TabControl` をリージョンにすると、ビューがタブとして並びますが、タブの見出し（ヘッダー）の文字は自動では決まりません。ビューモデルの `Title` を見出しに使う、というスタイルを `TabControl` に足します。

```xml
<TabControl Grid.Row="2" prism:RegionManager.RegionName="{x:Static infra:RegionNames.Bottom}">
    <TabControl.ItemContainerStyle>
        <Style TargetType="TabItem">
            <Setter Property="Header" Value="{Binding DataContext.Title}" />
        </Style>
    </TabControl.ItemContainerStyle>
</TabControl>
```

`TabItem` の中身はビューなので、`DataContext.Title` はそのビューのビューモデルの `Title` です。`AssetViewModel` と `LogViewModel` に `public string Title => "アセット";` のようなプロパティを足しておきます。

## モジュールを登録する

`App.xaml.cs` に、モジュールの一覧を教えます。

```csharp
using Prism.Modularity;

protected override void ConfigureModuleCatalog(IModuleCatalog moduleCatalog)
{
    moduleCatalog.AddModule<SceneTreeModule>();
    moduleCatalog.AddModule<PropertyModule>();
    moduleCatalog.AddModule<AssetModule>();
    moduleCatalog.AddModule<LogModule>();
}
```

起動の順番は、「アプリの `RegisterTypes` → 各モジュールの `RegisterTypes` → 各モジュールの `OnInitialized` → シェルの表示」です。実行すると、第 6 章と同じ見た目の画面が、リージョン経由で出ます。

この教材ではモジュールを同じプロジェクトのフォルダーとして作っています。機能が大きくなったら、別の C# ライブラリ プロジェクトにして、`Editor` から参照を追加すれば、同じように登録できます。必要になるまで読み込まない遅延読み込みや、フォルダー内の DLL を探して読む方式もあります（第 19 章）。

## ナビゲーション：同じリージョンの表示を切り替える

リージョンに複数のビューを用意しておいて、名前を指定して表示を切り替えたい場面があります。たとえば右側のパネルを「プロパティ」と「設定」で切り替える場合です。これをナビゲーションと呼びます。

まず、ビューをナビゲーション用に登録します。

```csharp
public void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterForNavigation<PropertyView>();
    containerRegistry.RegisterForNavigation<SettingsView>();
}
```

切り替えるときは、`RequestNavigate` を呼びます。

```csharp
public class MainWindowViewModel : BindableBase
{
    private readonly IRegionManager _regionManager;
    public DelegateCommand<string> NavigateCommand { get; }

    public MainWindowViewModel(IRegionManager regionManager)
    {
        _regionManager = regionManager;
        NavigateCommand = new DelegateCommand<string>(
            viewName => _regionManager.RequestNavigate(RegionNames.Property, viewName));
    }
}
```

```xml
<Button Content="設定" Command="{Binding NavigateCommand}" CommandParameter="SettingsView" />
```

`RegisterForNavigation<T>()` は、ビューをクラス名の文字列（`"SettingsView"`）で呼び出せるようにする登録です。`RegisterViewWithRegion`（起動時に差し込むビューを決める）と違い、`RequestNavigate` は実行中に表示を切り替えます。

### 画面に出入りしたときの通知

ビューモデルに `INavigationAware` を実装すると、画面に出入りするときに通知が来ます。

```csharp
public class SettingsViewModel : BindableBase, INavigationAware
{
    public void OnNavigatedTo(NavigationContext navigationContext)
    {
        // この画面に切り替わったとき。渡されたパラメーターも読める
    }

    public bool IsNavigationTarget(NavigationContext navigationContext)
    {
        return true;   // すでにあるこの画面を使い回してよいか
    }

    public void OnNavigatedFrom(NavigationContext navigationContext)
    {
        // 他の画面に切り替わるとき
    }
}
```

`IsNavigationTarget` が `true` なら既存のビューを再利用、`false` なら新しく作ります。値を渡したいときは `NavigationParameters` を使います。

```csharp
var parameters = new NavigationParameters { { "ObjectId", 42 } };
_regionManager.RequestNavigate(RegionNames.Property, "PropertyView", parameters);
```

ここで知っておきたいのは、ナビゲーションで切り替えたビューは、デフォルトではリージョンに残り続けるという点です。同じ画面に何度も行き来すると、前の状態が残ったままの画面が出てくることがあります。残すかどうかを制御する方法（`KeepAlive`）や、未保存の編集があるときに移動を止める方法（`IConfirmNavigationRequest`）は、第 19 章で説明します。

## 動作確認

- 起動すると、第 6 章と同じ見た目で、左に「シーン ツリー」、右に「プロパティ」、下にタブ（アセット、ログ）が出る。
- `MainWindow.xaml` には、部品の中身が書かれていない（リージョンだけ）。
- 「出力」ウィンドウに `RegionNotFoundException` などの例外が出ていない。

??? failure "リージョンが見つからない（`RegionNotFoundException`）"
    `RegisterViewWithRegion` の名前と、XAML の `RegionName` が一致していません。`RegionNames` の定数を使っているか確かめてください。

??? failure "ビューが出ない（空白のまま）"
    モジュールを `AddModule` していない可能性があります。`OnInitialized` にブレークポイントを置いて、呼ばれているかを確認します。

??? failure "タブの見出しが空欄になる"
    `ItemContainerStyle` のバインディングが、ビューモデルの `Title` に届いていません。「出力」ウィンドウに `BindingExpression path error` が出ているはずです。

??? failure "ビューモデルがビューにつながらない"
    `UserControl` にも `prism:ViewModelLocator.AutoWireViewModel="True"` が必要です。ビューのフォルダーと名前空間の規則も確かめます。

## 関連する章

- [第 19 章 Prism を掘り下げる](19-prism-deep.md)：`KeepAlive`、`IConfirmNavigationRequest`、`CompositeCommand`、モジュールの遅延読み込み

次の章では、お互いを知らないモジュールどうしが連絡を取る方法と、ビューモデルからダイアログを開く方法を学びます。

[第 18 章 イベント集約、ダイアログ、サービス](18-events-dialogs.md) へ進みます。

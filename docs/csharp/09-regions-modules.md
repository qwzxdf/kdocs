---
title: 第 9 章 リージョン、モジュール、ナビゲーション
tags:
  - C#連携
---

# 第 9 章 リージョン、モジュール、ナビゲーション

この章では、エディタの画面を<strong>領域（リージョン）</strong>に分け、各機能（シーン ツリー、プロパティ、アセット、ログ）を<strong>モジュール</strong>として、それぞれ別々に追加できる形にします。第 6 章で作った画面の骨組みを、Prism の仕組みで作り直す章です。

## この章の考え方

第 6 章の `MainWindow.xaml` には、シーン ツリーも、プロパティも、アセットも、全部を直接書きました。機能が増えると、`MainWindow.xaml` が巨大になり、複数の人が同時に触ると衝突します。

そこで、`MainWindow` を<strong>「枠だけ」</strong>にします。枠には、名前の付いた<strong>空きスペース（リージョン）</strong>だけを置き、中身は、各機能が自分で、「このリージョンに、私の画面を出して」と、登録します。

```text
MainWindow（枠）
┌──────────────────────────────────────────────┐
│ [SceneTreeRegion] [ViewportRegion] [PropertyRegion] │
│                   [BottomRegion]                    │
└──────────────────────────────────────────────┘
        ▲                ▲                ▲
  SceneTree モジュール  Viewport モジュール  Property モジュール
  （自分の View を差し込む）
```

| 用語 | 意味 |
| --- | --- |
| <strong>リージョン（Region）</strong> | 画面の中の、名前の付いた空きスペース。中に、ビューを差し込める |
| <strong>ビュー（View）</strong> | リージョンに差し込む部品。ふつうは `UserControl` |
| <strong>リージョン マネージャー</strong> | リージョンとビューの対応を管理する（`IRegionManager`） |
| <strong>モジュール（Module）</strong> | 機能のまとまり。ビューやサービスの登録をまとめて行う（`IModule`） |
| <strong>ナビゲーション</strong> | リージョンに表示するビューを、名前で切り替える |

## この章のゴール

- `MainWindow` を、リージョンだけの枠にする。
- 4 つのモジュール（SceneTree、Property、Asset、Log）を作り、各リージョンにビューを差し込む。
- ナビゲーションで、下のパネルの表示を切り替える。

## 手順 1：リージョン名を決める

リージョンの名前は、文字列です。タイプミスを防ぐために、<strong>定数にまとめます</strong>。`Editor` に `Infrastructure` フォルダーを作り、次を書きます。

```csharp
namespace Editor.Infrastructure;

// 画面の領域の名前
public static class RegionNames
{
    public const string SceneTree = "SceneTreeRegion";
    public const string Viewport = "ViewportRegion";
    public const string Property = "PropertyRegion";
    public const string Bottom = "BottomRegion";
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `static class` | インスタンスを作れず、`static` なメンバーだけを持つクラス。C++ の名前空間にまとめた定数に近い |
| `const string` | コンパイル時に決まる文字列の定数。他の `const` から使え、属性の引数にも書ける |

## 手順 2：MainWindow を枠にする

`Views\MainWindow.xaml` の本体を、次のようにします（第 6 章の Grid の構造はそのまま、中身をリージョンに置き換えます）。

```xml
<Window x:Class="Editor.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:prism="http://prismlibrary.com/"
        xmlns:infra="clr-namespace:Editor.Infrastructure"
        prism:ViewModelLocator.AutoWireViewModel="True"
        Title="{Binding Title}" Height="720" Width="1280">
    <DockPanel>
        <Menu DockPanel.Dock="Top">
            <!-- 第 6 章のメニューと同じ（コマンドは第 21 章以降で結びつける） -->
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

            <ContentControl Grid.Column="0" prism:RegionManager.RegionName="{x:Static infra:RegionNames.SceneTree}" />
            <GridSplitter Grid.Column="1" Width="4" HorizontalAlignment="Stretch" />

            <Grid Grid.Column="2">
                <Grid.RowDefinitions>
                    <RowDefinition Height="*" MinHeight="120" />
                    <RowDefinition Height="Auto" />
                    <RowDefinition Height="200" MinHeight="60" />
                </Grid.RowDefinitions>
                <ContentControl Grid.Row="0" prism:RegionManager.RegionName="{x:Static infra:RegionNames.Viewport}" />
                <GridSplitter Grid.Row="1" Height="4" HorizontalAlignment="Stretch" />
                <TabControl Grid.Row="2" prism:RegionManager.RegionName="{x:Static infra:RegionNames.Bottom}" />
            </Grid>

            <GridSplitter Grid.Column="3" Width="4" HorizontalAlignment="Stretch" />
            <ContentControl Grid.Column="4" prism:RegionManager.RegionName="{x:Static infra:RegionNames.Property}" />
        </Grid>
    </DockPanel>
</Window>
```

`MainWindowViewModel` には、`StatusText` を足します。

```csharp
private string _statusText = "準備完了";
public string StatusText
{
    get => _statusText;
    set => SetProperty(ref _statusText, value);
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `prism:RegionManager.RegionName="…"` | 添付プロパティ。この部品を、<strong>その名前のリージョン</strong>にする。中身は、リージョンマネージャーが差し込む |
| `ContentControl` | <strong>1 つの内容</strong>を表示する部品。リージョンに差し込めるのは、1 つ（置き換わる） |
| `TabControl`（リージョンにすると） | 差し込んだビューが、<strong>タブとして並ぶ</strong>。複数のビューを同時に持てる |
| `{x:Static infra:RegionNames.SceneTree}` | `static` な定数を参照するマークアップ拡張。文字列を直接書かずに済む |
| `xmlns:infra` | 自分の名前空間を、XAML で使うための宣言 |

### リージョン アダプター

リージョンにできる部品の種類で、<strong>ビューの並び方</strong>が変わります。この対応を決めているのが <strong>リージョン アダプター</strong>です。

| 部品 | 並び方 | 使いどころ |
| --- | --- | --- |
| `ContentControl` | 1 つだけ。新しく入れると置き換わる | 中央のビューポート、右のプロパティ |
| `ItemsControl` | 全部が縦に並ぶ | ツール バーのような並び |
| `TabControl`（`Selector`） | タブになる | 下のパネル（アセット、ログ） |
| `ComboBox`（`Selector`） | ドロップダウンで選ぶ | 切り替え式の入力 |

## 手順 3：ビューを作る

各機能の画面は、`UserControl`（部品として使える小さな画面）で作ります。シーン ツリーから始めます。

1. `Editor` に、`Modules\SceneTree` フォルダーを作る。
2. その中に、`Views` と `ViewModels` のフォルダーを作る。
3. `Views` を右クリック →「追加 → 新しい項目 → ユーザー コントロール (WPF)」で、`SceneTreeView.xaml` を作る。

`Modules\SceneTree\Views\SceneTreeView.xaml`:

```xml
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

`Modules\SceneTree\ViewModels\SceneTreeViewModel.cs`:

```csharp
using Prism.Mvvm;

namespace Editor.Modules.SceneTree.ViewModels;

public class SceneTreeViewModel : BindableBase
{
    public string Message => "（ここにシーンの木が出ます）";
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `UserControl` | 部品として組み込める、小さな画面。`Window` のように外枠を持たず、他の画面の中に入れて使う |
| フォルダーと名前空間 | `Modules\SceneTree\Views` の中なので、名前空間は `Editor.Modules.SceneTree.Views`。ViewModelLocator の規則（`.Views.` → `.ViewModels.`）に合う |

同じようにして、`Property`（`PropertyView`）、`Asset`（`AssetView`）、`Log`（`LogView`）も作ります。中身は、今は、タイトルだけで構いません。

## 手順 4：モジュールを作る

モジュールは、<strong>`IModule` を実装したクラス</strong>です。

`Modules\SceneTree\SceneTreeModule.cs`:

```csharp
using Prism.Ioc;
using Prism.Modularity;
using Prism.Regions;

using Editor.Infrastructure;
using Editor.Modules.SceneTree.Views;

namespace Editor.Modules.SceneTree;

public class SceneTreeModule : IModule
{
    // ① 型の登録（DI コンテナーに）
    public void RegisterTypes(IContainerRegistry containerRegistry)
    {
        // このモジュールが提供するサービスがあれば、ここで登録する
    }

    // ② 初期化（全モジュールの登録が終わった後に呼ばれる）
    public void OnInitialized(IContainerProvider containerProvider)
    {
        var regionManager = containerProvider.Resolve<IRegionManager>();
        regionManager.RegisterViewWithRegion(RegionNames.SceneTree, typeof(SceneTreeView));
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `IModule` | モジュールのインターフェース。`RegisterTypes` と `OnInitialized` の 2 つを持つ |
| `RegisterTypes` | 自分のモジュールが使う型を、コンテナーに登録する。すべてのモジュールの `RegisterTypes` が、先に実行される |
| `OnInitialized` | 全モジュールの登録が終わった後に呼ばれる。ビューをリージョンに登録するなど、他のモジュールの型も使う処理を書く |
| `IContainerProvider` | 解決専用のコンテナー。`Resolve<T>()` を持つ |
| `IRegionManager` | リージョンを管理する。`RegisterViewWithRegion(リージョン名, 型)` で、リージョンが作られたときに、そのビューを自動で差し込む |
| `typeof(SceneTreeView)` | 型そのものを表す式。C++ の `typeid` に近い（ただし、型の情報オブジェクトを返す） |

同様に、`PropertyModule`（`RegionNames.Property`）、`AssetModule`（`RegionNames.Bottom`）、`LogModule`（`RegionNames.Bottom`）を作ります。下のパネル（`TabControl`）に 2 つのビューが登録されると、2 つのタブになります。

### タブの見出しを付ける

`TabControl` のリージョンでは、タブの見出し（ヘッダー）を、ビューモデルの `Title` から取ります。`TabControl` 側に、次のスタイルを足します。

```xml
<TabControl Grid.Row="2" prism:RegionManager.RegionName="{x:Static infra:RegionNames.Bottom}">
    <TabControl.ItemContainerStyle>
        <Style TargetType="TabItem">
            <Setter Property="Header" Value="{Binding DataContext.Title}" />
        </Style>
    </TabControl.ItemContainerStyle>
</TabControl>
```

この指定で、各ビューのビューモデルが持つ `Title` が、タブの見出しになります。`AssetViewModel` と `LogViewModel` に、`public string Title => "アセット";` のようなプロパティを足します。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `ItemContainerStyle` | リスト系・タブ系の部品が、各項目を入れる入れ物（`TabItem` など）に使うスタイル |
| `Style TargetType="TabItem"` | `TabItem` 全部に適用 |
| `{Binding DataContext.Title}` | `TabItem` の中身（ビュー）の `DataContext`（ビューモデル）の `Title` を指す。`TabItem` の `DataContext` は、差し込まれたビューそのもの |

## 手順 5：モジュールをカタログに登録する

`App.xaml.cs` に、`ConfigureModuleCatalog` を足します。

```csharp
using Prism.Modularity;

using Editor.Modules.Asset;
using Editor.Modules.Log;
using Editor.Modules.Property;
using Editor.Modules.SceneTree;

protected override void ConfigureModuleCatalog(IModuleCatalog moduleCatalog)
{
    moduleCatalog.AddModule<SceneTreeModule>();
    moduleCatalog.AddModule<PropertyModule>();
    moduleCatalog.AddModule<AssetModule>();
    moduleCatalog.AddModule<LogModule>();
}
```

実行すると、第 6 章の画面と同じ見た目が、リージョン経由で出ます。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `IModuleCatalog` | 起動時に読み込むモジュールの一覧 |
| `AddModule<T>()` | モジュールを一覧に追加する |
| 起動の順序 | `RegisterTypes`（アプリ）→ `ConfigureModuleCatalog` → 各モジュールの `RegisterTypes` → 各モジュールの `OnInitialized` → `CreateShell` の結果を表示 |

!!! note "モジュールを別プロジェクトにするには"
    この教材では、1 つのプロジェクト（`Editor`）の中のフォルダーとして、モジュールを作ります。機能が大きくなったら、モジュールを<strong>別の C# ライブラリ プロジェクト</strong>にして、`Editor` から参照を追加し、同じように `AddModule<T>()` で登録できます。Prism は、DLL を実行時に探して読み込む方式（`DirectoryModuleCatalog`）にも対応しています。

## 手順 6：ナビゲーションで切り替える

リージョンに<strong>複数のビューを登録して、1 つだけを見せ、名前で切り替える</strong>のが、ナビゲーションです。例えば、右側のパネルを、「プロパティ」と「設定」で切り替えるときに使います。

### ビューをナビゲーション用に登録する

```csharp
// モジュールの RegisterTypes
public void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterForNavigation<PropertyView>();
    containerRegistry.RegisterForNavigation<SettingsView>();
}
```

### 切り替える

```csharp
public class MainWindowViewModel : BindableBase
{
    private readonly IRegionManager _regionManager;

    public DelegateCommand<string> NavigateCommand { get; }

    public MainWindowViewModel(IRegionManager regionManager)
    {
        _regionManager = regionManager;
        NavigateCommand = new DelegateCommand<string>(Navigate);
    }

    private void Navigate(string viewName)
    {
        _regionManager.RequestNavigate(RegionNames.Property, viewName);
    }
}
```

```xml
<Button Content="設定" Command="{Binding NavigateCommand}" CommandParameter="SettingsView" />
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `RegisterForNavigation<T>()` | ビューを、<strong>クラス名の文字列</strong>（`"PropertyView"`）で呼び出せるように登録する |
| `RequestNavigate(リージョン名, ビュー名)` | そのリージョンに、そのビューを表示する |
| `RegisterViewWithRegion` との違い | `RegisterViewWithRegion` は<strong>起動時に決めた物を差し込む</strong>。`RequestNavigate` は<strong>実行中に切り替える</strong> |

### ナビゲーションの通知（INavigationAware）

ビューモデルが `INavigationAware` を実装すると、画面に出入りするときに、通知が来ます。

```csharp
public class SettingsViewModel : BindableBase, INavigationAware
{
    public void OnNavigatedTo(NavigationContext navigationContext)
    {
        // 画面に出たとき。渡されたパラメーターも読める
    }

    public bool IsNavigationTarget(NavigationContext navigationContext)
    {
        return true;   // 既に作ってあるこのビューを再利用してよいか
    }

    public void OnNavigatedFrom(NavigationContext navigationContext)
    {
        // 画面から去るとき
    }
}
```

| メソッド | 呼ばれるとき |
| --- | --- |
| `OnNavigatedTo` | このビューに切り替わったとき。`navigationContext.Parameters` で、渡された値を読む |
| `IsNavigationTarget` | 同じ種類のビューが、既にあるとき、<strong>それを再利用してよいか</strong>を返す。`true` なら再利用、`false` なら新しく作る |
| `OnNavigatedFrom` | 他のビューに切り替わるとき。未保存の内容の保存などを行う |

パラメーターを渡すときは、`NavigationParameters` を使います。

```csharp
var parameters = new NavigationParameters { { "ObjectId", 42 } };
_regionManager.RequestNavigate(RegionNames.Property, "PropertyView", parameters);
```

## 手順 7：リージョンに複数のビューが入るとき

| 登録した数 | `ContentControl` のとき | `TabControl` のとき |
| --- | --- | --- |
| 1 つ | そのビューが出る | 1 つのタブ |
| 複数 | 最後に登録した物に置き換わる、または例外 | 登録した順にタブが並ぶ |

`ContentControl` に複数を登録したいときは、`regionManager.Regions[名前].Activate(view)` で、前に出すものを切り替えます。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| 起動 | 第 6 章と同じ見た目で、左に「シーン ツリー」、右に「プロパティ」、下にタブ（アセット、ログ）が出る |
| `MainWindow.xaml` | 部品の中身が書かれていない（リージョンだけ） |
| 出力ウィンドウ | `RegionNotFoundException` などの例外が出ない |

## よくあるミス

??? failure "`RegionNotFoundException`／リージョンが見つからない"
    `RegisterViewWithRegion` の名前と、XAML の `RegionName` が一致していない。`RegionNames` の定数を使っているか確認する。または、`OnInitialized` が、シェルの表示前に走り、リージョンがまだ無いことがある。Prism は、リージョンが後から作られた場合でも、登録済みのビューを差し込むので、`RegisterViewWithRegion` を使う限りは問題ない。

??? failure "ビューが出ない（空白のまま）"
    モジュールが `AddModule` されていない。`OnInitialized` に、ブレークポイントを置いて、呼ばれているか確認する。

??? failure "タブの見出しが、空欄になる"
    `ItemContainerStyle` のバインディングが、ビューモデルの `Title` に届いていない。出力ウィンドウの `BindingExpression path error` を確認する。

??? failure "ビューモデルが、ビューに結びつかない"
    `UserControl` にも、`prism:ViewModelLocator.AutoWireViewModel="True"` が必要。ビューのフォルダーと名前空間の規則も確認する。

## この章のまとめ

- `MainWindow` は、リージョンだけの枠にする。中身は、各モジュールが差し込む。
- モジュールは、`IModule` の `RegisterTypes`（型の登録）と `OnInitialized`（ビューの登録）を持つ。
- `RegisterViewWithRegion` は<strong>起動時に決める</strong>、`RequestNavigate` は<strong>実行中に切り替える</strong>。

## 次の章へ

次の章（[第 10 章 イベント集約、ダイアログ、サービス](10-events-dialogs.md)）では、お互いを知らないモジュールどうしが連絡する仕組み（<strong>IEventAggregator</strong>）と、ビューモデルからダイアログを開く仕組みを作ります。

---
title: 第 22 章 リージョン、モジュール、ナビゲーション
tags:
  - C#連携
---

# 第 22 章 リージョン、モジュール、ナビゲーション

第 6 章の `MainWindow.xaml` には、シーン ツリーも、プロパティも、アセットも、全部を直接書きました。第 16 章まで機能を足してきた結果、このファイルは検索ボックスや一覧のテンプレートまで抱えて、太っています。複数の人が同時に触ればぶつかりますし、どの機能のコードがどこにあるのかも分かりにくくなります。

!!! info "このページを読む前に"
    - [第 21 章 DI コンテナーの種類と DryIoc](21-di-containers.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

そこでこの章では、`MainWindow` を「枠だけ」にして、中身は機能ごとに別々の場所から差し込む形に作り直します。使うのは Prism のリージョンとモジュールです。

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Infrastructure/RegionNames.cs`（新規） | リージョンの名前の定数 |
    | `MainWindow.xaml`（変更） | 中身を全部消して、リージョンだけの枠にする |
    | `Modules/SceneTree/`（新規） | シーン ツリーのモジュール（モジュール、ビュー、ビューモデル） |
    | `Modules/Property/`（新規） | プロパティのモジュール。設定の画面もここ |
    | `Modules/Asset/`・`Modules/Log/`（新規） | 第 15〜16 章で作ったタブを、モジュールに移す |
    | `ViewModels/AssetBrowserViewModel.cs`（名前変更） | `Modules/Asset/AssetViewModel.cs` に移す |
    | `App.xaml.cs`（変更） | モジュールの一覧を教える |

    この章の終わりでは、プロパティ パネルは、シーン ツリーの選択ではなく、仮のオブジェクトを表示しています。2 つのモジュールをつなぐのは、次の章です。

## 考え方：枠に名前を付けて、中身はあとから差し込む

`MainWindow` には、名前の付いた空きスペース（リージョン）だけを置きます。中身のビューは、各機能が自分で「このリージョンに私の画面を出してください」と登録します。

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
| モジュール | 機能のまとまり。ビューやサービスの登録をまとめて行う |

`MainWindow` は、どんなビューが入るのかを知りません。リージョンの名前だけで中身とつながるので、機能を足したり外したりしても `MainWindow` は変わりません。

## リージョンの名前を決める

リージョンの名前は文字列ですが、タイプミスを避けるために定数にまとめます。

```csharp title="Infrastructure/RegionNames.cs（新規）"
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

```xml title="MainWindow.xaml（変更：全体）"
<Window x:Class="Editor.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:prism="http://prismlibrary.com/"
        xmlns:infra="clr-namespace:Editor.Infrastructure"
        prism:ViewModelLocator.AutoWireViewModel="True"
        Title="MiniEngine Editor" Height="720" Width="1280"
        Background="#FF1E1E1E">
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

`Window.Resources` にあった `BoolToVisibility` と `ValidatedTextBox` は、使うビューの側に移すので、ここには残しません。ステータス バーの「選択中の名前」の行も、いったん消します。選択は、これからシーン ツリーのモジュールの持ち物になるからです。次の章で戻します。

`MainWindowViewModel` は、ステータス バーの文字だけを持つ小さなクラスになります。

```csharp title="MainWindowViewModel.cs（変更：全体）"
using Prism.Mvvm;

namespace Editor;

public class MainWindowViewModel : BindableBase
{
    private string _statusText = "準備完了";

    public string StatusText
    {
        get => _statusText;
        set => SetProperty(ref _statusText, value);
    }
}
```

`TabControl` と `ContentControl` に、`prism:RegionManager.RegionName` を付けると、それがリージョンになります。`prism:RegionManager.RegionName` は添付プロパティで、これを付けた部品が「その名前のリージョン」になります。`{x:Static ...}` は、`static` な定数を XAML から参照するマークアップ拡張で、文字列をベタ書きしないで済みます。

リージョンにできる部品の種類で、ビューの並び方が変わります。

| 部品 | 並び方 | こんなときに |
| --- | --- | --- |
| `ContentControl` | 1 つだけ。新しく入れると置き換わる | ビューポート、プロパティ |
| `ItemsControl` | 全部が縦に並ぶ | ツール バーのような並び |
| `TabControl` | ビューごとにタブができる | 下のパネル（アセット、ログ） |
| `ComboBox` | ドロップダウンで選ぶ | 切り替え式の入力 |

## ビューを作る

各機能の画面は `UserControl` で作ります。`Window` のような外枠を持たず、他の画面の中に入れて使える小さな画面です。ここでは、画面とビューモデルを機能ごとのフォルダーに並べます。

1. `Editor` に `Modules\SceneTree` フォルダーを作ります。
2. フォルダーを右クリックして「追加 → 新しい項目 → ユーザー コントロール (WPF)」で `SceneTreeView.xaml` を作ります。
3. 同じフォルダーに、ビューモデルの `SceneTreeViewModel.cs` を作ります。

画面とビューモデルを同じフォルダー、同じ名前空間（`Editor.Modules.SceneTree`）に置いても、ViewModelLocator は見つけられます。`SceneTreeView` のように名前が `View` で終わる画面には、`Model` だけを足して `SceneTreeViewModel` を探すからです（第 20 章）。

### シーン ツリー

`MainWindow.xaml` にあった左のパネルを、そのまま移します。

```xml title="Modules/SceneTree/SceneTreeView.xaml（新規）"
<UserControl x:Class="Editor.Modules.SceneTree.SceneTreeView"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:prism="http://prismlibrary.com/"
             prism:ViewModelLocator.AutoWireViewModel="True">
    <DockPanel Background="#FF252526">
        <TextBox DockPanel.Dock="Top" Margin="8"
                 Text="{Binding FilterText, UpdateSourceTrigger=PropertyChanged, Delay=300}" />
        <Button DockPanel.Dock="Bottom" Content="オブジェクトを追加" Margin="8"
                Command="{Binding AddCommand}" />
        <ListBox ItemsSource="{Binding Objects}"
                 SelectedItem="{Binding Selected}"
                 Background="Transparent" BorderThickness="0" Foreground="White">
            <ListBox.ItemTemplate>
                <!-- 第 14 章の ItemTemplate（名前、位置、削除ボタン）をそのまま -->
            </ListBox.ItemTemplate>
        </ListBox>
    </DockPanel>
</UserControl>
```

`prism:ViewModelLocator.AutoWireViewModel="True"` を、`UserControl` にも付けます。付け忘れると、ビューモデルが結ばれず、画面が空になります。

`MainWindowViewModel` にあった、オブジェクトの一覧と選択、絞り込み、追加、削除は、そのまま `SceneTreeViewModel` に移ります。

```csharp title="Modules/SceneTree/SceneTreeViewModel.cs（新規）"
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Windows.Data;
using Editor.ViewModels;
using Prism.Commands;
using Prism.Mvvm;

namespace Editor.Modules.SceneTree;

public class SceneTreeViewModel : BindableBase
{
    private SceneObjectViewModel? _selected;
    private string _filterText = "";
    private readonly ICollectionView _objectsView;

    public SceneTreeViewModel()
    {
        Objects = new ObservableCollection<SceneObjectViewModel>
        {
            new("Camera", 0, 2, -5),
            new("Cube", 1, 0, 2),
            new("Light", 3, 5, 0),
        };
        Selected = Objects[1];

        _objectsView = CollectionViewSource.GetDefaultView(Objects);
        _objectsView.Filter = o => o is SceneObjectViewModel s
            && s.Name.Contains(_filterText, StringComparison.OrdinalIgnoreCase);

        AddCommand = new DelegateCommand(Add);
        DeleteCommand = new DelegateCommand<SceneObjectViewModel>(Delete);
    }

    public ObservableCollection<SceneObjectViewModel> Objects { get; }

    public SceneObjectViewModel? Selected
    {
        get => _selected;
        set => SetProperty(ref _selected, value);
    }

    public string FilterText
    {
        get => _filterText;
        set
        {
            if (SetProperty(ref _filterText, value))
                _objectsView.Refresh();
        }
    }

    public DelegateCommand AddCommand { get; }
    public DelegateCommand<SceneObjectViewModel> DeleteCommand { get; }

    private void Add()
    {
        var obj = new SceneObjectViewModel($"Object {Objects.Count}");
        Objects.Add(obj);
        Selected = obj;
    }

    private void Delete(SceneObjectViewModel obj)
    {
        Objects.Remove(obj);
        if (Selected == obj) Selected = null;
    }
}
```

`HasSelection` は、プロパティ パネルの側で使うので、ここにはありません。

### プロパティ

右のパネルは、`MainWindow.xaml` にあった入力欄、スライダー、リセット ボタンを移します。第 14 章で `Window.Resources` に置いた `BoolToVisibility` と `ValidatedTextBox` は、このビューの `UserControl.Resources` に移します。

```xml title="Modules/Property/PropertyView.xaml（新規）"
<UserControl x:Class="Editor.Modules.Property.PropertyView" ...
             prism:ViewModelLocator.AutoWireViewModel="True">
    <UserControl.Resources>
        <BooleanToVisibilityConverter x:Key="BoolToVisibility" />
        <!-- ValidatedTextBox のスタイル（第 14 章）もここへ -->
    </UserControl.Resources>
    <Border Background="#FF252526" Padding="8">
        <StackPanel Visibility="{Binding HasTarget, Converter={StaticResource BoolToVisibility}}">
            <TextBlock Text="プロパティ" Foreground="White" FontWeight="Bold" />
            <!-- 第 13〜14 章の入力欄。Selected.Name を Target.Name に読み替える -->
        </StackPanel>
    </Border>
</UserControl>
```

```csharp title="Modules/Property/PropertyViewModel.cs（新規）"
using Editor.ViewModels;
using Prism.Mvvm;

namespace Editor.Modules.Property;

public class PropertyViewModel : BindableBase
{
    private SceneObjectViewModel? _target;

    public PropertyViewModel()
    {
        // 次の章で、シーン ツリーの選択につなぐ。それまでの仮のオブジェクト
        Target = new SceneObjectViewModel("(仮) Cube", 1, 0, 2);
    }

    public SceneObjectViewModel? Target
    {
        get => _target;
        set
        {
            if (SetProperty(ref _target, value))
                RaisePropertyChanged(nameof(HasTarget));
        }
    }

    public bool HasTarget => _target is not null;
}
```

画面の側は、`Selected.Name` と書いていたバインディングを、`Target.Name` に読み替えます。ほかの `Selected.` も同じです。

### アセットとログ

下のパネルの 2 つのタブは、すでに独立したビューモデルを持っています。`TabItem` の中身を、そのまま `UserControl` に移すだけです。`DataContext="{Binding AssetBrowser}"` のように、ビューモデルを切り替えていた行は消します。ViewModelLocator が、画面ごとのビューモデルを結んでくれるからです。

- `Modules/Asset/AssetView.xaml`：アセットのタブの中身（コンボボックス、一覧、進行バー）。
- `Modules/Log/LogView.xaml`：ログのタブの中身（`DataGrid`）。

名前の規則に合わせて、`AssetBrowserViewModel` は `Modules/Asset/AssetViewModel.cs` に移して、`AssetViewModel` に改名します（`AssetView` に `Model` を足した名前になります）。`LogViewModel` は、`LogView` に合わせて `Modules/Log/` に移します。

## モジュールを作る

モジュールは `IModule` を実装したクラスです。やることは 2 つあります。

```csharp title="Modules/SceneTree/SceneTreeModule.cs（新規）"
using Editor.Infrastructure;
using Prism.Ioc;
using Prism.Modularity;
using Prism.Navigation.Regions;

namespace Editor.Modules.SceneTree;

public class SceneTreeModule : IModule
{
    // ① DI コンテナーにこのモジュールの型を登録する
    public void RegisterTypes(IContainerRegistry containerRegistry)
    {
    }

    // ② このモジュールの RegisterTypes の直後に呼ばれる。ビューをリージョンに登録する
    public void OnInitialized(IContainerProvider containerProvider)
    {
        var regionManager = containerProvider.Resolve<IRegionManager>();
        regionManager.RegisterViewWithRegion(RegionNames.SceneTree, typeof(SceneTreeView));
    }
}
```

モジュールごとに、`RegisterTypes`、`OnInitialized` の順で呼ばれます。モジュール A の `OnInitialized` が終わってから、モジュール B の `RegisterTypes` が始まります。つまり、`OnInitialized` の時点で使えるのは、自分と、自分より前に初期化されたモジュールが登録した型までです。あとのモジュールの型は、まだ登録されていません（Prism 9.0.537 で確認）。初期化の順番は、`ConfigureModuleCatalog` で `AddModule` した順です。モジュール同士のやり取りは、型を直接知り合うのではなく、第 23 章のイベント集約を使うのが安全です。

<strong>名前空間に注意</strong>してください。リージョンとナビゲーション関連の型（`IRegionManager`、`INavigationAware`、`NavigationContext` など）は、Prism 8 までは `Prism.Regions` でしたが、Prism 9 では `Prism.Navigation.Regions` です。古い記事の `using Prism.Regions;` をそのまま写すと、「名前空間 'Regions' が存在しません」というエラーになります。

`RegisterViewWithRegion` は、「このリージョンが作られたら、このビューを自動で差し込んでください」という登録です。`typeof(SceneTreeView)` は、型そのものを表す式です。

ほかの 3 つのモジュールも、同じ形で作ります。

| モジュール | ビュー | リージョン | `RegisterTypes` で登録するもの |
| --- | --- | --- | --- |
| `PropertyModule` | `PropertyView` | `RegionNames.Property` | （次の節のナビゲーションで足す） |
| `AssetModule` | `AssetView` | `RegionNames.Bottom` | `IAssetScanner` → `AssetScanner` |
| `LogModule` | `LogView` | `RegionNames.Bottom` | なし |

`IAssetScanner` を使うのは、アセットのモジュールだけなので、そのモジュールで登録します。`App.RegisterTypes` に書いていた行は、移します。

```csharp title="Modules/Asset/AssetModule.cs（新規：RegisterTypes だけ）"
public void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterSingleton<IAssetScanner, AssetScanner>();
}
```

`LogViewModel` は逆です。アセット側の `AssetViewModel` も、ログ側の `LogView` も使うので、<strong>`App.RegisterTypes` に残します</strong>。モジュールで登録すると、そのモジュールの初期化より前に `AssetViewModel` が作られたとき、`LogViewModel` が未登録のまま作られます。具体的なクラスは、未登録でも解決できてしまうため、エラーにならず、毎回別の実体が作られて、ログが別々の一覧に入ります（第 19 章）。複数のモジュールが共有する物は `App` に登録する、と覚えておきます。

```csharp title="App.xaml.cs（変更）"
protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterSingleton<LogViewModel>();    // 複数のモジュールで共有する
}
```

### タブの見出しを付ける

`TabControl` をリージョンにすると、ビューごとにタブができます。ただし、タブの見出し（ヘッダー）の文字は、自動では決まらず、空のタブが並びます。そこで、ビューモデルの `Title` を見出しに使う、というスタイルを `TabControl` に足します。

まず、`AssetViewModel` と `LogViewModel` に、`Title` を足します。

```csharp
public string Title => "アセット";      // LogViewModel は "ログ"
```

```xml title="MainWindow.xaml（変更：TabControl）"
<TabControl Grid.Row="2" prism:RegionManager.RegionName="{x:Static infra:RegionNames.Bottom}">
    <TabControl.ItemContainerStyle>
        <Style TargetType="TabItem">
            <Setter Property="Header"
                    Value="{Binding Content.DataContext.Title, RelativeSource={RelativeSource Self}}" />
        </Style>
    </TabControl.ItemContainerStyle>
</TabControl>
```

`TabItem` の `Content` が、差し込まれたビューです。そのビューの `DataContext` が、ViewModelLocator が結んだビューモデルなので、`Content.DataContext.Title` で見出しを読めます。`TabItem` 自身の `DataContext` は、親から引き継いだものなので、`{Binding DataContext.Title}` と書くと、ビューモデルの `Title` には届かない場合があります。`RelativeSource={RelativeSource Self}` で `TabItem` 自身から、ビューをたどるほうが確実です。

## モジュールを登録する

`App.xaml.cs` に、モジュールの一覧を教えます。

```csharp title="App.xaml.cs（変更）"
using Prism.Modularity;

protected override void ConfigureModuleCatalog(IModuleCatalog moduleCatalog)
{
    moduleCatalog.AddModule<SceneTreeModule>();
    moduleCatalog.AddModule<PropertyModule>();
    moduleCatalog.AddModule<AssetModule>();
    moduleCatalog.AddModule<LogModule>();
}
```

起動の順番は、モジュールが 2 つ（A、B）のとき、実際に動かして確かめると、次のとおりです（Prism 9.0.537）。

```text title="実験の出力：モジュール A、B で確かめた起動の順"
App.RegisterTypes
App.ConfigureModuleCatalog
App.CreateShell
  ModA.RegisterTypes
  ModA.OnInitialized
  ModB.RegisterTypes
  ModB.OnInitialized
App.OnInitialized
```

1. アプリの `RegisterTypes`。
2. `ConfigureModuleCatalog`。ここで教えたモジュールの一覧が決まるだけで、まだ中身は動かない。
3. `CreateShell`。`MainWindow` が作られる。
4. モジュールを、一覧の順に 1 つずつ初期化する。1 つ分が `RegisterTypes` と `OnInitialized` のセット。
5. `OnInitialized`。基底クラスの `OnInitialized` が、シェルを `Show()` する。

画面に出るのは最後です。実行すると、第 16 章までと同じ見た目の画面が、リージョン経由で出ます。

この教材ではモジュールを同じプロジェクトのフォルダーとして作っています。機能が大きくなったら、別の C# ライブラリ プロジェクトにして、`Editor` から参照を追加すれば、同じように登録できます。必要になるまで読み込まない遅延読み込みや、フォルダー内の DLL を探して読む方式もあります（第 24 章）。

## ナビゲーション：同じリージョンの表示を切り替える

リージョンに複数のビューを用意しておいて、名前を指定して表示を切り替えたい場面があります。Editor では、右のパネルを「プロパティ」と「設定」で切り替えます。これをナビゲーションと呼びます。

まず、「設定」の画面を小さく作ります。エディターの設定は、あとの章で中身を足すので、今は見出しだけにします。

```xml title="Modules/Property/SettingsView.xaml（新規）"
<UserControl x:Class="Editor.Modules.Property.SettingsView" ...
             prism:ViewModelLocator.AutoWireViewModel="True">
    <Border Background="#FF252526" Padding="8">
        <TextBlock Text="エディターの設定" Foreground="White" FontWeight="Bold" />
    </Border>
</UserControl>
```

`SettingsViewModel` は、空のクラスで構いません（`BindableBase` を継承しておきます）。次に、ビューをナビゲーション用に登録します。

```csharp title="Modules/Property/PropertyModule.cs（変更）"
public void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterForNavigation<PropertyView>();
    containerRegistry.RegisterForNavigation<SettingsView>();
}
```

切り替えるときは、`RequestNavigate` を呼びます。メニューの「表示」から呼べるようにします。

```csharp title="MainWindowViewModel.cs（変更）"
using Editor.Infrastructure;
using Prism.Commands;
using Prism.Navigation.Regions;

private readonly IRegionManager _regionManager;
public DelegateCommand<string> NavigateCommand { get; }

public MainWindowViewModel(IRegionManager regionManager)
{
    _regionManager = regionManager;
    NavigateCommand = new DelegateCommand<string>(
        viewName => _regionManager.RequestNavigate(RegionNames.Property, viewName));
}
```

```xml title="MainWindow.xaml（変更：「表示」メニュー）"
<MenuItem Header="表示(_V)">
    <MenuItem Header="プロパティ(_P)" Command="{Binding NavigateCommand}" CommandParameter="PropertyView" />
    <MenuItem Header="設定(_S)" Command="{Binding NavigateCommand}" CommandParameter="SettingsView" />
</MenuItem>
```

`RegisterForNavigation<T>()` は、ビューをクラス名の文字列（`"SettingsView"`）で呼び出せるようにする登録です。`RegisterViewWithRegion`（起動時に差し込むビューを決める）と違い、`RequestNavigate` は実行中に表示を切り替えます。メニューから「設定」を選ぶと、右のパネルが切り替わります。

### 深掘り：画面に出入りしたときの通知

ビューモデルに `INavigationAware` を実装すると、画面に出入りするときに通知が来ます。

```csharp title="実験：INavigationAware の形（Editor には入れない）"
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

`IsNavigationTarget` が `true` なら既存のビューを再利用、`false` なら新しく作ります。

呼ばれる順番は、次のとおりです。2 つのビュー（V1、V2）で `RequestNavigate("V1")` → `"V2"` → `"V1"` と続けて実行した結果です（Prism 9.0.537）。

```text title="実験の出力：V1、V2 で確かめた呼ばれる順"
RequestNavigate V1
    [V1 VM ctor]
    V1.OnNavigatedTo
RequestNavigate V2
    V1.ConfirmNavigationRequest
    V1.OnNavigatedFrom
    [V2 VM ctor]
    V2.OnNavigatedTo
RequestNavigate V1
    V2.ConfirmNavigationRequest
    V2.OnNavigatedFrom
    V1.IsNavigationTarget
    V1.OnNavigatedTo
```

1. 今出ているビューの `ConfirmNavigationRequest`（実装していれば。第 24 章）。ここで止められる。
2. 今出ているビューの `OnNavigatedFrom`。
3. 移動先に、すでに作ってあるビューがあれば、その `IsNavigationTarget`。1 回目の V1 や V2 のように、まだ無いときは呼ばれず、ビューとビューモデルが新しく作られる（ビューモデルのコンストラクター）。
4. 移動先の `OnNavigatedTo`。

1 回目の V1 には「今出ているビュー」が無いので、1・2 は飛ばされます。3 回目の V1 は、2 回目までに作られていたので、`IsNavigationTarget` が呼ばれて、コンストラクターは呼ばれません。値を渡したいときは `NavigationParameters` を使います。

```csharp
var parameters = new NavigationParameters { { "ObjectId", 42 } };
_regionManager.RequestNavigate(RegionNames.Property, "PropertyView", parameters);
```

ここで知っておきたいのは、ナビゲーションで切り替えたビューは、デフォルトではリージョンに残り続けるという点です。同じ画面に何度も行き来すると、前の状態が残ったままの画面が出てくることがあります。残すかどうかを制御する方法（`KeepAlive`）や、未保存の編集があるときに移動を止める方法（`IConfirmNavigationRequest`）は、第 24 章で説明します。

## 動かして確かめる

- 起動すると、第 16 章までと同じ見た目で、左にシーン ツリー、右にプロパティ、下にタブ（アセット、ログ）が出る。
- シーン ツリーで、選択、追加、削除、検索ができる。
- 右のプロパティには「(仮) Cube」が出る。シーン ツリーで別の行を選んでも、プロパティは変わらない（次の章で直します）。
- 下のタブの見出しが「アセット」「ログ」と出る。アセットの読み込みでログが増える。
- 「表示」メニューで「設定」を選ぶと、右のパネルが「エディターの設定」に切り替わり、「プロパティ」に戻せる。
- `MainWindow.xaml` には、部品の中身が書かれていない（リージョンだけ）。
- 「出力」ウィンドウに `RegionNotFoundException` などの例外が出ていない。

??? failure "リージョンが見つからない（`RegionNotFoundException`）"
    `RegisterViewWithRegion` の名前と、XAML の `RegionName` が一致していません。`RegionNames` の定数を使っているか確かめてください。

??? failure "ビューが出ない（空白のまま）"
    モジュールを `AddModule` していない可能性があります。`OnInitialized` にブレークポイントを置いて、呼ばれているかを確認します。

??? failure "タブの見出しが空欄になる、または別の文字になる"
    `ItemContainerStyle` のバインディングがビューモデルの `Title` に届いていません。上の `Content.DataContext.Title` の書き方になっているか、「出力」ウィンドウに `BindingExpression path error` が出ていないかを確かめます。

??? failure "ビューモデルがビューにつながらない"
    `UserControl` にも `prism:ViewModelLocator.AutoWireViewModel="True"` が必要です。ビューの名前空間と、ビューモデルの名前空間が同じか（または `Views` と `ViewModels` に分かれているか）、名前の末尾が規則どおりかも確かめます。

??? failure "ログの一覧が、アセットの読み込みで増えない"
    `LogViewModel` を、モジュールの `RegisterTypes` に登録していませんか。`App.RegisterTypes` に登録して、共有の 1 つにしてください。

## ここまでの Editor

```text
Editor/
├─ App.xaml / App.xaml.cs            LogViewModel を登録。モジュールの一覧
├─ Infrastructure/
│   └─ RegionNames.cs
├─ Models/ ・ Mvvm/ ・ Services/      （変更なし。IAssetScanner は AssetModule が登録）
├─ Modules/
│   ├─ SceneTree/                    SceneTreeModule / View / ViewModel
│   ├─ Property/                     PropertyModule / PropertyView / PropertyViewModel / SettingsView
│   ├─ Asset/                        AssetModule / AssetView / AssetViewModel
│   └─ Log/                          LogModule / LogView / LogViewModel
├─ ViewModels/
│   └─ SceneObjectViewModel.cs       （複数のモジュールが使うので、ここに残す）
├─ MainWindowViewModel.cs            ステータス バーとナビゲーションだけ
└─ MainWindow.xaml                   リージョンだけの枠
```

## 関連する章

- [第 24 章 Prism を掘り下げる](24-prism-deep.md)：`KeepAlive`、`IConfirmNavigationRequest`、`CompositeCommand`、モジュールの遅延読み込み

次の章では、お互いを知らないモジュールどうしが連絡を取る方法と、ビューモデルからダイアログを開く方法を学びます。シーン ツリーで選んだ物を、プロパティ パネルに伝えるのも、そこです。

[第 23 章 イベント集約、ダイアログ、サービス](23-events-dialogs.md) へ進みます。

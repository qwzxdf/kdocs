---
title: 第 16 章 Prism の導入と起動の流れ
tags:
  - C#連携
---

# 第 16 章 Prism の導入と起動の流れ

第 12 章から第 15 章で、Editor にはビューモデルが 4 つ、自作の部品が 4 つできました。`ViewModelBase`、`ValidatableViewModelBase`、`RelayCommand`、`AsyncCommand` です。動いてはいますが、気になる所も出てきました。`MainWindow.xaml.cs` で `DataContext = new MainWindowViewModel()` と書いているし、`MainWindowViewModel` の中では `new AssetBrowserViewModel(Log)` と、使う部品を手で組み立てています。画面が増えるたびに、この手作業が増えていきます。

この章では、Editor に Prism を入れます。やることは 3 つです。NuGet で Prism を入れること、アプリの起動を `PrismApplication` に作り替えること、そして自作した定型文を Prism の部品に置き換えることです。

!!! info "このページを読む前に"
    - [第 15 章 非同期処理と UI スレッド](15-async-ui.md)（前の章。この章は、そこまでの Editor を Prism に載せ替える）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `App.xaml`・`App.xaml.cs`（変更） | `PrismApplication` に作り替え、型を登録する |
    | `Views/MainWindow.xaml`・`.xaml.cs`（移動） | `Views` フォルダーに移し、ViewModelLocator で結ぶ |
    | `ViewModels/*.cs`（変更） | `ViewModelBase` を `BindableBase` に、`RelayCommand` を `DelegateCommand` に置き換える |
    | `Mvvm/ViewModelBase.cs`・`Mvvm/RelayCommand.cs`（削除） | Prism の部品に置き換えたので不要になる |
    | `Mvvm/AsyncCommand.cs`・`Mvvm/ValidatableViewModelBase.cs`（変更なし） | Prism にない物なので、そのまま使う |

## Prism は何をしてくれるのか

エディタのように画面がたくさんあるアプリでは、次のような困りごとが増えていきます。

- 画面ごとに `DataContext = new XxxViewModel()` を書いて回るのが面倒になる。
- ビューモデルが他のクラス（エンジンの窓口など）を必要とするとき、誰がそれを作って渡すのか決まっていない。
- 右側のパネルに別の画面を出したいなど、画面の一部を後から差し替えたい。
- シーン ツリーで選んだ物をプロパティ パネルに伝えたいが、お互いを知りたくない。
- 機能ごとにプロジェクトを分けて、後から足せるようにしたい。

Prism はこれらに対する部品をそろえたフレームワークです。ただし全部が同じ重さではありません。Prism を使う中心はおそらく DI コンテナーで、他の機能の多くは、必要になったときに使えば足ります。

| Prism の機能 | 何に使うか | 扱う場所 |
| --- | --- | --- |
| DI コンテナー | 必要なクラスを自動で作って渡す | この章、第 17〜21 章 |
| ViewModelLocator | 画面とビューモデルを名前の規則で自動でつなぐ | この章 |
| BindableBase、DelegateCommand | 通知とコマンドの定型文を減らす | この章 |
| リージョン | 画面の枠にあとから部品を差し込む | 第 22 章 |
| モジュール | 機能のまとまりを起動時に登録する | 第 22 章 |
| IEventAggregator | お互いを知らない部品の間で連絡する | 第 23 章 |
| ダイアログ サービス | ビューモデルからダイアログを開く | 第 23 章 |

Prism のバージョンは、上げると名前空間や API が変わる所があります（とくにダイアログ周り）。Web で見つけた古い記事のコードを写すときは、どのバージョン向けかを確かめてください。この教材は Prism 9 を使います。

また、MVVM の補助だけが目的なら、CommunityToolkit.Mvvm のような軽いライブラリも選べます。違いは第 25 章で比べました。

## NuGet で入れる

1. `Editor` を右クリックして「NuGet パッケージの管理」を開きます。
2. 「参照」で `Prism.DryIoc` を探して、最新の安定版（9.x）を入れます。

`Prism.DryIoc` を入れると、`Prism.Wpf` や `Prism.Core` も一緒に入ります。DryIoc は DI コンテナーの名前で、Prism は他のコンテナー（Unity など）にも対応していますが、いまは DryIoc を使います。

NuGet は、C++ の vcpkg のようなライブラリの配布の仕組みです。入れると `Editor.csproj` に、こんな行が増えます。

```xml
<ItemGroup>
  <PackageReference Include="Prism.DryIoc" Version="9.0.537" />
</ItemGroup>
```

## App を PrismApplication にする

`App.xaml` の `Application` を `prism:PrismApplication` に変えて、`StartupUri` を消します。

```xml title="App.xaml（変更）"
<prism:PrismApplication x:Class="Editor.App"
                        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                        xmlns:prism="http://prismlibrary.com/">
    <prism:PrismApplication.Resources>
        <!-- 今までのリソース（第 6 章、第 11 章の色やスタイル）は、ここに移す -->
    </prism:PrismApplication.Resources>
</prism:PrismApplication>
```

`StartupUri` を消すのは、最初のウィンドウを Prism に作らせるためです（ビューモデルや DI を使えるようにするため）。残しておくとウィンドウが 2 つ開いてしまいます。

```csharp title="App.xaml.cs（変更）"
using System.Windows;
using Editor.Views;
using Prism.DryIoc;
using Prism.Ioc;

namespace Editor;

public partial class App : PrismApplication
{
    // 最初に開く画面（シェル）を作る
    protected override Window CreateShell()
    {
        return Container.Resolve<MainWindow>();
    }

    // DI コンテナーにクラスを登録する
    protected override void RegisterTypes(IContainerRegistry containerRegistry)
    {
    }
}
```

`PrismApplication` は、起動の手順（コンテナーを作る → 型を登録する → 最初の画面を作って表示する）を代わりにやってくれる基底クラスです。私たちが書くのは、次の 2 つだけです。

- `CreateShell()` は、最初の画面を作る関数です。この「一番外側のウィンドウ」を Prism 用語でシェルと呼びます。ここでは `MainWindow` です。
- `RegisterTypes()` は、DI コンテナーに型を登録する場所です。今は空ですが、このあと使います。

`Container.Resolve<MainWindow>()` の `Container` が DI コンテナーです。「`MainWindow` を作って」と頼むと、必要なものを自動で作って渡してくれます。

## MainWindow を Views に移す

ViewModelLocator は、画面と同じ名前の「ViewModel」を、名前の規則で探します。Editor は、第 12 章でビューモデルを `ViewModels` フォルダーに入れました。画面も `Views` フォルダーに入れると、名前空間が `Editor.Views` と `Editor.ViewModels` に分かれて、規則（`.Views.` を `.ViewModels.` に置き換える）がそのまま使えます。

1. `Views` フォルダーを作り、`MainWindow.xaml` を、ドラッグして中へ移します。`MainWindow.xaml.cs` も一緒に動きます。
2. `MainWindow.xaml` の `x:Class` を `Editor.Views.MainWindow` に、`MainWindow.xaml.cs` の `namespace` を `Editor.Views` に直します。

```xml title="Views/MainWindow.xaml（変更：先頭の数行）"
<Window x:Class="Editor.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:prism="http://prismlibrary.com/"
        prism:ViewModelLocator.AutoWireViewModel="True"
        ...
```

```csharp title="Views/MainWindow.xaml.cs（変更）"
namespace Editor.Views;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
        // DataContext の設定は、もう要らない
    }
}
```

`DataContext = new MainWindowViewModel();` の行は消しました。`AutoWireViewModel="True"` が付いた画面は、ViewModelLocator が `Editor.ViewModels.MainWindowViewModel` を探して、`DataContext` に設定してくれます。

画面の `x:Class` と `.xaml.cs` の `namespace` が食い違うと、ビルドが通りません。ファイルをフォルダーに移したときは、`namespace` が自動では変わらないので、とくに気を付けてください。第 13 章で足した `xmlns:vm="clr-namespace:Editor.ViewModels"` の行は、そのまま使えます。

## 定型文を Prism の部品に置き換える

### BindableBase と SetProperty

第 12 章で書いた `ViewModelBase` は、`INotifyPropertyChanged` を実装して、`SetProperty` を持つ基底クラスでした。Prism にある `BindableBase` は、まったく同じ役目の基底クラスです。`SetProperty(ref _x, value)` の使い方も、「変わったかどうかを `bool` で返す」ところも同じなので、継承元を変えるだけで済みます。

```csharp title="ViewModels/SceneObjectViewModel.cs（変更：先頭）"
using Prism.Mvvm;
using Editor.Mvvm;

public class SceneObjectViewModel : ValidatableViewModelBase
```

`ValidatableViewModelBase` の継承元も変えます。

```csharp title="Mvvm/ValidatableViewModelBase.cs（変更）"
using Prism.Mvvm;

public abstract class ValidatableViewModelBase : BindableBase, INotifyDataErrorInfo
```

ほかのビューモデルは `: ViewModelBase` を `: BindableBase` に書き換えて、`using Prism.Mvvm;` を足します。違いが 1 つだけあります。自分で書いた `OnPropertyChanged(string)` は、Prism では `RaisePropertyChanged(string)` という名前です。

```csharp title="ViewModels/MainWindowViewModel.cs（変更）"
public SceneObjectViewModel? Selected
{
    get => _selected;
    set
    {
        if (SetProperty(ref _selected, value))
            RaisePropertyChanged(nameof(HasSelection));
    }
}
```

`Mvvm/ViewModelBase.cs` は、もう使わないので削除します。

`ref` は、引数を参照渡しにするキーワードです。`SetProperty` は呼ぶ側のフィールドそのものを書き換える必要があるので、`ref _x` と渡します。C++ の `T&` に近い使い方で、呼ぶ側にも `ref` と書きます。

### DelegateCommand

第 12 章で自作した `RelayCommand` の、本物にあたるのが Prism の `DelegateCommand` です。大きな違いは、`RaiseCanExecuteChanged()` を手で呼ぶ代わりに、`ObservesProperty` で「このプロパティが変わったら、`CanExecute` を聞き直して」と宣言できることです。

`SceneObjectViewModel` の `ResetCommand` で比べます。

```csharp title="ViewModels/SceneObjectViewModel.cs（変更）"
using Prism.Commands;

// コンストラクターの中
ResetCommand = new DelegateCommand(Reset, () => _x != 0 || _y != 0 || _z != 0)
    .ObservesProperty(() => X)
    .ObservesProperty(() => Y)
    .ObservesProperty(() => Z);

public DelegateCommand ResetCommand { get; }

public float X { get => _x; set => SetProperty(ref _x, value); }
public float Y { get => _y; set => SetProperty(ref _y, value); }
public float Z { get => _z; set => SetProperty(ref _z, value); }
```

`X`、`Y`、`Z` の `set` から、`ResetCommand.RaiseCanExecuteChanged()` の呼び出しが消えました。呼び忘れて、ボタンの状態が更新されない、という種類のミスがなくなります。

`() => X` は、プロパティを「指す式」で、Prism はそこからプロパティ名を取り出しています。似た機能として、`bool` のプロパティをそのまま「押せるかどうか」にする `.ObservesCanExecute(() => IsReady)` もあります。

引数を受け取るコマンドは `DelegateCommand<T>` で、`RelayCommand<T>` の代わりになります。

```csharp title="ViewModels/MainWindowViewModel.cs（変更）"
public DelegateCommand AddCommand { get; }
public DelegateCommand<SceneObjectViewModel> DeleteCommand { get; }

// コンストラクターの中
AddCommand = new DelegateCommand(Add);
DeleteCommand = new DelegateCommand<SceneObjectViewModel>(Delete);
```

`AssetBrowserViewModel` の `CancelCommand` も同じです。`IsBusy` の `set` の中の `RaiseCanExecuteChanged()` は、要らなくなります。

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更）"
public DelegateCommand CancelCommand { get; }

// コンストラクターの中
CancelCommand = new DelegateCommand(() => _cts?.Cancel(), () => IsBusy)
    .ObservesProperty(() => IsBusy);

public bool IsBusy { get => _isBusy; private set => SetProperty(ref _isBusy, value); }
```

`Mvvm/RelayCommand.cs` も削除します。`AsyncCommand` は、Prism に同じ物がないので、そのまま使います（CommunityToolkit.Mvvm なら `AsyncRelayCommand` があります。第 25 章）。

## DI で、手作業の組み立てをなくす

`MainWindowViewModel` の中で、`Log` と `AssetBrowser` を手で作っていました。

```csharp title="今の書き方（変更前）"
Log = new LogViewModel();
AssetBrowser = new AssetBrowserViewModel(Log);       // Log を渡す係が、ここにいる
```

`AssetBrowserViewModel` が `AssetScanner` も必要とすれば、`MainWindowViewModel` がそれも知っていて、作って渡さなければなりません。DI コンテナーは、これを自動でやってくれます。

DI（Dependency Injection、依存性注入）は、「必要な部品を自分で作らず、外から渡してもらう」という設計の考え方です。誰が渡すのか、を担当するのが DI コンテナーです。コンテナーは「`LogViewModel` が欲しいと言われたら、これを作る」という登録を持っていて、クラスが必要になったとき、コンストラクターの引数を見て、必要なものを（芋づる式に）作って渡します。

| 用語 | 意味 |
| --- | --- |
| 登録（Register） | 「この型が欲しいと言われたら、これを作る」と教えること |
| 解決（Resolve） | コンテナーにオブジェクトを作ってもらうこと |
| 注入（Inject） | 作ったものをコンストラクターの引数で渡すこと |
| 生存期間 | 作ったものを使い回すか、毎回作るか |

まず、`App.xaml.cs` で 3 つの型を登録します。

```csharp title="App.xaml.cs（変更）"
using Editor.Services;
using Editor.ViewModels;

protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterSingleton<AssetScanner>();
    containerRegistry.RegisterSingleton<LogViewModel>();
    containerRegistry.RegisterSingleton<AssetBrowserViewModel>();
}
```

`RegisterSingleton` は、アプリの間ずっと 1 つだけ作って、みんなで共有する登録です。ログやアセット一覧のように、状態を共有するものは `RegisterSingleton` にします。状態を持たない小さな部品は `Register`（解決のたびに新しく作る）で足ります。

次に、受け取る側のコンストラクターに、欲しいものを書きます。

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更）"
public AssetBrowserViewModel(LogViewModel log, AssetScanner scanner)
{
    _log = log;
    _scanner = scanner;
    // 以下は前のとおり
}
```

```csharp title="ViewModels/MainWindowViewModel.cs（変更）"
public MainWindowViewModel(LogViewModel log, AssetBrowserViewModel assetBrowser)
{
    Log = log;
    AssetBrowser = assetBrowser;
    // 以下は前のとおり
}
```

`private readonly AssetScanner _scanner = new();` の行は消します。`new AssetBrowserViewModel(Log)` と書いていた所もなくなりました。

`MainWindowViewModel` を `new` しているコードは、どこにもありません。ViewModelLocator がコンテナーに「ビューモデルを作って」と頼み、コンテナーがコンストラクターの引数 `LogViewModel` と `AssetBrowserViewModel` を見て作って渡しているのです。`AssetBrowserViewModel` に必要な `LogViewModel` と `AssetScanner` も、コンテナーが同じように渡します。

ここでは、DI がどういう形かだけを見ました。登録だけで作られるのか、`Singleton` と `Transient` は何が違うのか、インターフェースを挟む意味はなにか、などは、続く第 17〜21 章で順に掘り下げます。

## ViewModelLocator のしくみ（ここまでのおさらい）

画面を開くたびに「この画面のビューモデルはこれ」と書くのは面倒です。Prism の ViewModelLocator は、名前の規則でビューモデルを見つけて、`DataContext` に設定してくれます。

`AutoWireViewModel="True"` が付いた画面は、名前の規則に従ってビューモデルを探します。規則は「画面の名前に `ViewModel` を足したクラス」で、名前空間に `.Views.` があれば `.ViewModels.` に置き換えて探します。`MainWindow`（`Editor.Views`）には `Editor.ViewModels.MainWindowViewModel` を探します。末尾が `View` の画面（`SceneTreeView`）には、`Model` だけを足して `SceneTreeViewModel` を探します（詳しくは第 20 章）。規則に合わないときは、明示的に結び付けることもできます。

```csharp
ViewModelLocationProvider.Register<MainWindow, MainWindowViewModel>();
```

## 動かして確かめる

実行して、次の点を見てください。

- ウィンドウが 1 つだけ開き、第 15 章までと同じ画面と動きになっている（見た目は何も変わらないのが正解です）。
- シーン ツリーの選択、位置のリセット、アセットの読み込みとキャンセルが、今までどおり動く。
- 「出力」ウィンドウに `System.Windows.Data Error` が出ていない。

??? failure "起動時に `ContainerResolutionException` が出る"
    ビューモデルのコンストラクターが欲しがっている型が登録されていません。メッセージの奥のほう（内側の例外）に足りない型の名前が書いてあります。具体的なクラスなら登録しなくても解決できる場合がありますが、インターフェースは必ず登録が必要です。

??? failure "ウィンドウが 2 つ開く"
    `App.xaml` に `StartupUri` が残っています。消してください。

??? failure "画面が空のまま、バインディングが効かない"
    名前の規則を確かめます。`MainWindow` が `Editor.Views`、`MainWindowViewModel` が `Editor.ViewModels` にあるか。名前の末尾が `ViewModel` になっているか。`AutoWireViewModel="True"` が書かれているか、の 3 点です。

??? failure "`PrismApplication` が見つからない（`CS0246`）"
    `using Prism.DryIoc;` が足りません。`Ctrl + .` で足せます。

??? failure "`App.xaml` と `App.xaml.cs` の基底クラスが合わないとビルドできない"
    XAML は `prism:PrismApplication`、C# は `: PrismApplication` です。片方が `Application` のままだと、ビルドが失敗します。

??? failure "`OnPropertyChanged` が見つからない（`CS1503`）"
    Prism の `BindableBase` では、名前を渡して通知する関数は `RaisePropertyChanged(nameof(...))` です。

## ここまでの Editor

```text
Editor/
├─ App.xaml / App.xaml.cs            PrismApplication。型の登録
├─ Models/                           （変更なし）
├─ Mvvm/
│   ├─ ValidatableViewModelBase.cs   BindableBase を継承
│   └─ AsyncCommand.cs
│   （ViewModelBase.cs と RelayCommand.cs は、Prism に置き換えて削除）
├─ Services/
│   └─ AssetScanner.cs
├─ ViewModels/
│   ├─ SceneObjectViewModel.cs       DelegateCommand、ObservesProperty
│   ├─ AssetBrowserViewModel.cs      コンストラクターで受け取る
│   ├─ LogViewModel.cs
│   └─ MainWindowViewModel.cs        コンストラクターで受け取る
└─ Views/
    ├─ MainWindow.xaml               AutoWireViewModel
    └─ MainWindow.xaml.cs
```

## 関連する章

- [第 17 章 DI とは何か](17-di-basics.md)〜[第 21 章 DI コンテナーの種類と DryIoc](21-di-containers.md)：DI の掘り下げ
- [第 25 章 MVVM ライブラリを比べる](25-mvvm-libraries.md)：`BindableBase` と CommunityToolkit.Mvvm の書き比べ
- [第 24 章 Prism を掘り下げる](24-prism-deep.md)：ナビゲーションの確認、KeepAlive、CompositeCommand、モジュールの遅延読み込み

次の章からは、ここで出てきた DI の仕組みを、「なぜ必要か」から順に掘り下げます。その後の第 22 章では、画面を「リージョン」という領域に分けて、機能ごとのモジュールが自分の画面をそこへ差し込む形に作り直します。

[第 17 章 DI とは何か](17-di-basics.md) へ進みます。第 22 章の画面づくりに進みたいときは、DI の章（第 17〜21 章）を飛ばして、[第 22 章 リージョン、モジュール、ナビゲーション](22-regions-modules.md) へ進んでも構いません。

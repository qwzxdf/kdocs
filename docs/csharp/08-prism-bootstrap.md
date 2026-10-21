---
title: 第 8 章 Prism の導入と起動の流れ
tags:
  - C#連携
---

# 第 8 章 Prism の導入と起動の流れ

この章では `Editor` に <strong>Prism</strong> を導入します。Prism は WPF のアプリを<strong>「小さな部品に分けて、育てやすくする」ためのフレームワーク</strong>です。この章の作業は 3 つです。

1. NuGet で Prism を入れる。
2. アプリの起動を `PrismApplication` に作り替える。
3. 第 7 章で手書きした `INotifyPropertyChanged` と `RelayCommand` を Prism の `BindableBase` と `DelegateCommand` に置き換える。

## この章の考え方

第 7 章までで WPF だけで MVVM を組めることが分かりました。ただし、エディタのように大きなアプリでは次の問題が出てきます。

| 問題 | 具体例 |
| --- | --- |
| ビューモデルを作る場所がばらばら | 画面ごとに `DataContext = new XxxViewModel()` を書いて回る |
| ビューモデルが他のクラスを必要とする | シーン ツリーのビューモデルが、エンジンの窓口クラスを必要とする。誰がどう渡すのか |
| 画面の領域を後から差し替えたい | 右側のパネルにプロパティ パネルを出す、別のパネルを出す |
| 画面どうしの連絡 | シーン ツリーで選んだらプロパティ パネルが変わる。でもお互いを知りたくない |
| 機能ごとに分けて開発したい | シーン ツリー機能、アセット機能を別プロジェクトにして、後から足したい |

Prism はこれらに対して、次の部品を用意しています。

| Prism の機能 | 解決する問題 | 扱う章 |
| --- | --- | --- |
| <strong>ViewModelLocator</strong> | 画面とビューモデルを名前の規則で自動で結びつける | この章 |
| <strong>BindableBase / DelegateCommand</strong> | 通知とコマンドの定型文を減らす | この章 |
| <strong>DI コンテナー</strong> | 必要なクラスを自動で作って渡す | この章、第 10 章 |
| <strong>リージョン</strong> | 画面の領域に部品（ビュー）を差し込む | 第 9 章 |
| <strong>モジュール</strong> | 機能ごとのまとまり。起動時に登録する | 第 9 章 |
| <strong>IEventAggregator</strong> | お互いを知らない部品の間の、メッセージの連絡 | 第 10 章 |
| <strong>ダイアログ サービス</strong> | ビューモデルから、ダイアログを開く | 第 10 章 |

!!! note "Prism の版について"
    この教材は <strong>Prism 9</strong>（DryIoc 版）を前提にしています。Prism は版によって名前空間や API が変わる所があります（例えば、ダイアログ関係は Prism 8 と 9 で名前空間が違います）。web 上の古い記事のコードを写すときは、版が合っているか確認してください。

## この章のゴール

- Prism を入れ `PrismApplication` で起動する。
- `ViewModelLocator` でビューとビューモデルを自動で結びつける。
- `BindableBase` と `DelegateCommand` を使う。
- DI コンテナーにクラスを登録して、取り出せる。

## 手順 1：NuGet で Prism を入れる

1. `Editor` プロジェクトを右クリック →「NuGet パッケージの管理」。
2. 「参照」タブで `Prism.DryIoc` を検索し、<strong>最新の安定版（9.x）</strong>をインストールする。

`Prism.DryIoc` を入れると `Prism.Wpf` と `Prism.Core` などが、まとめて入ります。

| 新しく出てきたもの | 説明 |
| --- | --- |
| NuGet | .NET のライブラリ配布の仕組み。パッケージ（ライブラリ + 情報）をインターネットから入れる。C++ の vcpkg に近い |
| パッケージ | NuGet で配られる、ライブラリの単位。名前と版を持つ |
| `Prism.Core` | Prism の中核（`BindableBase`、`DelegateCommand` など）。UI に依存しない |
| `Prism.Wpf` | WPF 向けの機能（`PrismApplication`、リージョン、ダイアログなど） |
| `Prism.DryIoc` | DI コンテナーに <strong>DryIoc</strong> を使う版。他に `Prism.Unity` などがあるが今の主流は DryIoc |
| `<PackageReference>` | `.csproj` に追加される行。パッケージ名と版が書かれる |

`Editor.csproj` に次のような行が増えていれば成功です。

```xml
<ItemGroup>
  <PackageReference Include="Prism.DryIoc" Version="9.0.537" />
</ItemGroup>
```

## 手順 2：フォルダーの構成を決める

Prism の ViewModelLocator は、<strong>フォルダーと名前の規則</strong>で、動きます。次の構成にします。

```text
Editor\
  App.xaml / App.xaml.cs
  Views\
    MainWindow.xaml / MainWindow.xaml.cs
  ViewModels\
    MainWindowViewModel.cs
  Models\   （あとで使う）
```

1. `Editor` に `Views` と `ViewModels` のフォルダーを作る。
2. `MainWindow.xaml` を `Views` フォルダーに<strong>ドラッグして移す</strong>（`.xaml.cs` もついてくる）。
3. 第 7 章で作った `PlayerViewModel` などの実験用のファイルは、不要なので削除する。`RelayCommand.cs` も削除する。
4. `Views\MainWindow.xaml` を開き <strong>`x:Class` を `Editor.Views.MainWindow` に</strong>直す。`MainWindow.xaml.cs` の `namespace` も `Editor.Views` に直す。

!!! warning "名前空間は、フォルダーに合わせる"
    ファイルをフォルダーに移しても、`namespace` は自動で変わらないことがあります。`x:Class`（XAML）と `namespace`（C#）が、食い違うとビルドが失敗します。

## 手順 3：App を PrismApplication にする

### App.xaml

`StartupUri` を<strong>削除</strong>し `Application` を `prism:PrismApplication` に変えます。

```xml
<prism:PrismApplication x:Class="Editor.App"
                        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                        xmlns:prism="http://prismlibrary.com/">
    <prism:PrismApplication.Resources>
        <!-- 第 6 章のリソースは、ここに移す -->
    </prism:PrismApplication.Resources>
</prism:PrismApplication>
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `xmlns:prism="http://prismlibrary.com/"` | Prism の部品を `prism:` という接頭辞で書けるようにする |
| `prism:PrismApplication` | `Application` の代わりに使う。起動の手順（DI コンテナーの作成、シェルの作成）を Prism が行う |
| `StartupUri` を消す理由 | 起動するウィンドウは、Prism が作る（ビューモデルや DI を使うために）。`StartupUri` を残すと二重に起動する |

### App.xaml.cs

```csharp
using System.Windows;
using Prism.DryIoc;
using Prism.Ioc;

using Editor.Views;

namespace Editor;

public partial class App : PrismApplication
{
    // 最初に開く画面（シェル）を作る
    protected override Window CreateShell()
    {
        return Container.Resolve<MainWindow>();
    }

    // DI コンテナーに、クラスを登録する
    protected override void RegisterTypes(IContainerRegistry containerRegistry)
    {
    }
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `PrismApplication` | 起動を管理する基底クラス。`OnStartup` の中でコンテナー作成 → 型登録 → シェル作成 → 表示、を順に行う |
| シェル（Shell） | アプリの<strong>一番外側のウィンドウ</strong>。ここでは `MainWindow` |
| `CreateShell()` | シェルを作る関数。`Container.Resolve<T>()` で DI コンテナーに作ってもらう |
| `Container` | DI コンテナー（`IContainerProvider`）。`Resolve` でオブジェクトを取り出す |
| `RegisterTypes(IContainerRegistry)` | コンテナーに型を登録する場所。登録したクラスを他のクラスが使えるようになる |
| `IContainerRegistry` | 登録用のインターフェース。`Register`、`RegisterSingleton`、`RegisterForNavigation` など |
| `protected override` | 基底クラスの関数を派生クラスで上書きする（第 5 章の `override`） |

## 手順 4：DI コンテナーとは何か

<strong>DI（Dependency Injection、依存性注入）</strong>はプログラムの設計の考え方で、<strong>「必要な部品を自分で作らず外から渡してもらう」</strong>ことです。

DI がないコードを考えます。

```csharp
public class SceneTreeViewModel
{
    private readonly EngineService _engine = new EngineService();   // 自分で作る
}
```

これは次の問題を抱えます。

- `EngineService` を作るのに必要な引数が増えるたびに作る側が変わる。
- テストのとき偽物（ダミー）の `EngineService` に差し替えられない。
- 複数のクラスが同じ `EngineService` を<strong>共有</strong>したいとき誰かが作って、配って回る必要がある。

DI では必要なものを<strong>コンストラクターの引数</strong>で宣言します。

```csharp
public class SceneTreeViewModel
{
    private readonly IEngineService _engine;

    public SceneTreeViewModel(IEngineService engine)    // 外から渡してもらう
    {
        _engine = engine;
    }
}
```

「誰が渡すのか」を担当するのが、<strong>DI コンテナー</strong>です。コンテナーは「`IEngineService` が必要になったら、`EngineService` を作って渡す」という登録を持っています。`SceneTreeViewModel` が必要になったときコンテナーはコンストラクターの引数を調べ必要なものを（再帰的に）作って渡します。

| 用語 | 意味 |
| --- | --- |
| 依存 | あるクラスが動くために必要とする、他のクラス |
| 注入（Inject） | 依存を外から渡すこと。コンストラクターの引数で渡すのが標準 |
| コンテナー | 型の登録を持ち依存を解決して、オブジェクトを作る仕組み |
| 登録（Register） | 「この型が必要になったら、これを作る」と教えること |
| 解決（Resolve） | コンテナーにオブジェクトを作ってもらうこと |
| 生存期間 | 作ったオブジェクトを使い回すか毎回作るか |

### 登録の方法

`RegisterTypes` の中で次のように登録します。

```csharp
protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    // シングルトン：アプリの間、1 つだけ作り、みんなで共有する
    containerRegistry.RegisterSingleton<IEngineService, EngineService>();

    // 一時的：解決のたびに新しく作る
    containerRegistry.Register<ISomething, Something>();

    // 具体的な型だけを登録する（インターフェースなし）
    containerRegistry.RegisterSingleton<AppSettings>();
}
```

| メソッド | 生存期間 | 使いどころ |
| --- | --- | --- |
| `RegisterSingleton<TFrom, TTo>()` | アプリの間 1 つ | エンジンの窓口、設定、ログなど共有するもの |
| `Register<TFrom, TTo>()` | 毎回新しく作る | 状態を持たない小さな部品 |
| `RegisterInstance(instance)` | 作ってある物を登録 | すでに作ったオブジェクトを渡す |
| `RegisterForNavigation<TView>()` | ビューのナビゲーション登録 | 第 9 章 |
| `RegisterDialog<TView, TViewModel>()` | ダイアログの登録 | 第 10 章 |

## 手順 5：ViewModelLocator

ビューを開くとき「どのビューモデルを `DataContext` にするか」を毎回書くのは面倒です。Prism の <strong>ViewModelLocator</strong> は、<strong>名前の規則</strong>でビューモデルを自動で見つけて設定します。

`Views\MainWindow.xaml` に 2 行足します。

```xml
<Window x:Class="Editor.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:prism="http://prismlibrary.com/"
        prism:ViewModelLocator.AutoWireViewModel="True"
        Title="{Binding Title}" Height="720" Width="1280">
    <Grid />
</Window>
```

そして、`ViewModels\MainWindowViewModel.cs` を書きます。

```csharp
using Prism.Mvvm;

namespace Editor.ViewModels;

public class MainWindowViewModel : BindableBase
{
    private string _title = "MiniEngine Editor";
    public string Title
    {
        get => _title;
        set => SetProperty(ref _title, value);
    }
}
```

実行するとウィンドウのタイトルが、「MiniEngine Editor」になります。`DataContext` を書いていないのに `{Binding Title}` が動いています。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `prism:ViewModelLocator.AutoWireViewModel="True"` | 添付プロパティ。`True` にするとこのビューの `DataContext` に <strong>規則で見つけたビューモデル</strong>を DI コンテナーで作って設定する |
| 命名規則 | `〜.Views.Xxx` のビューに対して、`〜.ViewModels.XxxViewModel` を探す。末尾が `View` のビュー（`SceneTreeView`）は `SceneTreeViewModel`（`ViewModel` を足す。`View` は重ならない） |
| `BindableBase` | Prism の基底クラス。`INotifyPropertyChanged` を実装済み |
| `SetProperty(ref field, value)` | 値が変わっていれば、フィールドを更新して `PropertyChanged` を発生させ `true` を返す。第 7 章の定型文 5 行が、1 行になる |
| `ref` | 引数を<strong>参照渡し</strong>にする。呼ばれた関数が呼ぶ側の変数そのものを書き換えられる。C++ の `T&` に近い。呼ぶ側にも `ref` を書く |

!!! tip "SetProperty の中身"
    `SetProperty` は第 7 章の `set` と同じことをしています。「今の値と同じなら何もしない。違えばフィールドを更新して通知する」。さらに、`[CallerMemberName]` でプロパティ名も自動で入ります。

### 規則に合わない場合

規則に頼らず明示的に結びつけることもできます。`App.xaml.cs` やビューの初期化で次のように登録します。

```csharp
ViewModelLocationProvider.Register<MainWindow, MainWindowViewModel>();
```

規則の設定自体を変えたい場合は `ViewModelLocationProvider.SetDefaultViewTypeToViewModelTypeResolver` を使います。この教材では既定の規則をそのまま使います。

## 手順 6：DelegateCommand

第 7 章の `RelayCommand` に相当するのが、Prism の <strong>`DelegateCommand`</strong> です。

```csharp
using Prism.Commands;
using Prism.Mvvm;

namespace Editor.ViewModels;

public class MainWindowViewModel : BindableBase
{
    private int _counter;
    public int Counter
    {
        get => _counter;
        set => SetProperty(ref _counter, value);
    }

    public DelegateCommand IncrementCommand { get; }

    public MainWindowViewModel()
    {
        IncrementCommand = new DelegateCommand(Increment, CanIncrement)
            .ObservesProperty(() => Counter);
    }

    private void Increment() => Counter++;
    private bool CanIncrement() => Counter < 10;
}
```

```xml
<StackPanel Margin="16">
    <TextBlock Text="{Binding Counter}" FontSize="32" />
    <Button Content="+1" Command="{Binding IncrementCommand}" Width="80" />
</StackPanel>
```

押すたびに数字が増え 10 になるとボタンが無効になります。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DelegateCommand` | `Execute` と `CanExecute` をデリゲートで受け取るコマンド。`RelayCommand` と同じ役割 |
| `DelegateCommand<T>` | 引数つきのコマンド。`CommandParameter` で値を渡せる |
| `.ObservesProperty(() => Counter)` | `Counter` が変わったら、自動で `CanExecute` を再確認させる。第 7 章の `RaiseCanExecuteChanged()` の手書きが要らなくなる |
| `.ObservesCanExecute(() => IsReady)` | `bool` のプロパティをそのまま `CanExecute` の結果として使う |
| `RaiseCanExecuteChanged()` | 手動で再確認させたいときに呼ぶ |
| `() => Counter`（式） | プロパティを<strong>指す式</strong>。Prism が式の中身からプロパティ名を取り出す |
| `FontSize` | 文字の大きさ |

### DelegateCommand<T> と CommandParameter

```csharp
public DelegateCommand<string> OpenCommand { get; }
OpenCommand = new DelegateCommand<string>(path => Open(path));
```

```xml
<Button Content="開く" Command="{Binding OpenCommand}" CommandParameter="scene1.json" />
```

## 手順 7：DI でクラスを受け取る

ビューモデルの<strong>コンストラクターの引数</strong>に必要なクラスを書くとコンテナーが渡してくれます。簡単な例として「メッセージを返すサービス」を作ります。

```csharp
namespace Editor.Services;

public interface IGreeter
{
    string Greet(string name);
}

public class Greeter : IGreeter
{
    public string Greet(string name) => $"こんにちは、{name} さん";
}
```

`App.xaml.cs` の `RegisterTypes` で登録します。

```csharp
containerRegistry.RegisterSingleton<IGreeter, Greeter>();
```

ビューモデルのコンストラクターで受け取ります。

```csharp
public class MainWindowViewModel : BindableBase
{
    private readonly IGreeter _greeter;

    public MainWindowViewModel(IGreeter greeter)
    {
        _greeter = greeter;
        Title = _greeter.Greet("Editor");
    }
    // …
}
```

`MainWindowViewModel` を `new` で作っているコードはどこにもありません。ViewModelLocator が、コンテナーに「`MainWindowViewModel` を作って」と頼みコンテナーが、コンストラクターの引数 `IGreeter` を見て、`Greeter` を作って渡しています。

| 新しく出てきたもの | 説明 |
| --- | --- |
| インターフェースを介して依存する | `Greeter` ではなく `IGreeter` を受け取る。実装を後から差し替えられる（テスト用のダミーなど） |
| コンストラクター注入 | 依存をコンストラクターの引数で受け取る。最もよく使う形 |
| `readonly` フィールド | 受け取った依存を保持する。後で差し替えない |

この仕組みは後の章でエンジンの窓口（`IEngineService`）を全部のビューモデルに配るために使います。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| 起動 | ウィンドウが開きタイトルに「こんにちは、Editor さん」が出る |
| `+1` ボタン | 数字が増え 10 でボタンが無効になる |
| 出力ウィンドウ | バインディング エラー（`System.Windows.Data Error`）が出ない |

## よくあるミス

??? failure "起動時に `ContainerResolutionException`（解決できない型）"
    ビューモデルのコンストラクターが要求する型が、登録されていない。メッセージの最後（内側の例外）に足りない型の名前が書かれている。`RegisterTypes` に登録する。具体的なクラスなら登録しなくても解決できる場合もあるが、インターフェースは必ず登録が要る。

??? failure "ウィンドウが 2 つ開く"
    `App.xaml` に `StartupUri` が残っている。削除する。

??? failure "タイトルが、バインドされない／ViewModel が見つからない"
    名前の規則を確認する。`Views` フォルダーの `MainWindow` に対して、`ViewModels` フォルダーの `MainWindowViewModel`。名前空間が `〜.Views` / `〜.ViewModels` になっているか。`AutoWireViewModel="True"` が書かれているか。

??? failure "`CS0246: 型または名前空間 'PrismApplication' が見つかりません`"
    `using Prism.DryIoc;` が無い。`Ctrl + .` で候補から足す。

??? failure "`App.xaml` の `x:Class` と `App.xaml.cs` の基底クラスが食い違う"
    XAML は `prism:PrismApplication`、C# は `: PrismApplication`。どちらかが `Application` のままだとビルドが失敗する。

## この章のまとめ

- Prism は `PrismApplication` から起動し、DI コンテナーを持つ。
- ViewModelLocator が、規則（`Views` / `ViewModels`、`〜ViewModel`）でビューとビューモデルをつなぐ。
- `BindableBase` と `SetProperty`、`DelegateCommand` と `ObservesProperty` で定型文が減る。
- DI コンテナーはコンストラクターの引数を見て、依存を渡す。

## 次の章へ

次の章（[第 9 章 リージョン、モジュール、ナビゲーション](09-regions-modules.md)）では画面を<strong>領域（リージョン）</strong>に分け機能を<strong>モジュール</strong>として追加できる形にします。エディタの骨組みがここで決まります。

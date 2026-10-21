---
title: 第 16 章 Prism の導入と起動の流れ
tags:
  - C#連携
---

# 第 16 章 Prism の導入と起動の流れ

この章では `Editor` に Prism を入れます。やることは 3 つです。NuGet で Prism を入れること、アプリの起動を `PrismApplication` に作り替えること、そして第 12 章で手書きした通知とコマンドの定型文を、Prism の `BindableBase` と `DelegateCommand` に置き換えることです。

## Prism は何をしてくれるのか

第 12 章までで、WPF だけでも MVVM は組めることが分かりました。では、なぜ Prism を入れるのでしょうか。エディタのように画面がたくさんあるアプリでは、次のような困りごとが出てくるからです。

- 画面ごとに `DataContext = new XxxViewModel()` を書いて回るのが面倒になる。
- ビューモデルが他のクラス（エンジンの窓口など）を必要とするとき、誰がそれを作って渡すのか決まっていない。
- 右側のパネルに別の画面を出したいなど、画面の一部を後から差し替えたい。
- シーン ツリーで選んだ物をプロパティ パネルに伝えたいが、お互いを知りたくない。
- 機能ごとにプロジェクトを分けて、後から足せるようにしたい。

Prism はこれらに対する部品をそろえたフレームワークです。ただし全部が同じ重さではありません。Prism を使う中心はおそらく DI コンテナーで、他の機能の多くはその上に乗っています。

| Prism の機能 | 何に使うか | 扱う場所 |
| --- | --- | --- |
| DI コンテナー | 必要なクラスを自動で作って渡す | この章、第 18 章 |
| ViewModelLocator | 画面とビューモデルを名前の規則で自動でつなぐ | この章 |
| BindableBase、DelegateCommand | 通知とコマンドの定型文を減らす | この章 |
| リージョン | 画面の枠に、あとから部品を差し込む | 第 17 章 |
| モジュール | 機能のまとまりを、起動時に登録する | 第 17 章 |
| IEventAggregator | お互いを知らない部品の間で連絡する | 第 18 章 |
| ダイアログ サービス | ビューモデルからダイアログを開く | 第 18 章 |

Prism のバージョンは、上げると名前空間や API が変わる所があります（とくにダイアログ周り）。Web で見つけた古い記事のコードを写すときは、どのバージョン向けかを確かめてください。この教材は Prism 9（DryIoc 版）で書いています。

また、MVVM の補助だけが目的なら、CommunityToolkit.Mvvm のような軽いライブラリも選べます。違いは第 20 章で比べました。

## NuGet で入れる

1. `Editor` を右クリックして「NuGet パッケージの管理」を開きます。
2. 「参照」で `Prism.DryIoc` を探して、最新の安定版（9.x）を入れます。

`Prism.DryIoc` を入れると、`Prism.Wpf` や `Prism.Core` も一緒に入ります。DryIoc は DI コンテナーの名前で、Prism は他のコンテナー（Unity など）にも対応していますが、いまの主流は DryIoc です。

NuGet は、C++ の vcpkg のようなライブラリの配布の仕組みです。入れると `Editor.csproj` に、こんな行が増えます。

```xml
<ItemGroup>
  <PackageReference Include="Prism.DryIoc" Version="9.0.537" />
</ItemGroup>
```

## フォルダーを整える

あとで出てくる ViewModelLocator は、フォルダーと名前の規則でビューモデルを探します。先にフォルダーを整えておきます。

```text
Editor\
  App.xaml / App.xaml.cs
  Views\       MainWindow.xaml / .cs
  ViewModels\  MainWindowViewModel.cs
  Models\      （あとで使う）
```

1. `Views` と `ViewModels` のフォルダーを作ります。
2. `MainWindow.xaml` を `Views` にドラッグして移します（`.xaml.cs` も一緒に動きます）。
3. 第 12 章で作った実験用のファイル（`PlayerViewModel`、`RelayCommand` など）は削除します。
4. `Views\MainWindow.xaml` の `x:Class` を `Editor.Views.MainWindow` に直し、`MainWindow.xaml.cs` の `namespace` も `Editor.Views` に直します。

ファイルをフォルダーに移しても、`namespace` は自動では変わりません。`x:Class` と `namespace` が食い違うとビルドが通らないので、ここは忘れずに。

## App を PrismApplication にする

`App.xaml` の `Application` を `prism:PrismApplication` に変えて、`StartupUri` を消します。

```xml title="App.xaml"
<prism:PrismApplication x:Class="Editor.App"
                        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                        xmlns:prism="http://prismlibrary.com/">
    <prism:PrismApplication.Resources>
        <!-- 第 6 章のリソースはここに移す -->
    </prism:PrismApplication.Resources>
</prism:PrismApplication>
```

`StartupUri` を消すのは、最初のウィンドウを Prism に作らせるためです（ビューモデルや DI を使えるようにするため）。残しておくとウィンドウが 2 つ開いてしまいます。

```csharp title="App.xaml.cs"
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

`PrismApplication` は、起動の手順（コンテナーを作る → 型を登録する → 最初の画面を作って表示する）を代わりにやってくれる基底クラスです。私たちが書くのは、その途中の 2 つの穴だけです。

- `CreateShell()` は、最初の画面を作る関数です。この「一番外側のウィンドウ」を、Prism 用語でシェルと呼びます。ここでは `MainWindow` です。
- `RegisterTypes()` は、DI コンテナーに型を登録する場所です。今は空ですが、このあと使います。

`Container.Resolve<MainWindow>()` の `Container` が DI コンテナーです。「`MainWindow` を作って」と頼むと、必要なものを自動で作って渡してくれます。DI の話は、次の節でじっくり説明します。

## DI コンテナーとは何か

DI（Dependency Injection、依存性注入）は、「必要な部品を自分で作らず、外から渡してもらう」という設計の考え方です。

DI を使わない書き方から見てみましょう。

```csharp
public class SceneTreeViewModel
{
    private readonly EngineService _engine = new EngineService();   // 自分で作る
}
```

これには困る点がいくつかあります。

- `EngineService` を作るのに引数が必要になったら、作っているすべての場所を直さないといけない。
- テストのとき、偽物の `EngineService` に差し替えられない。
- いくつものクラスが同じ `EngineService` を共有したいとき、誰かが作って配って回らないといけない。

DI では、必要なものをコンストラクターの引数に書いて、外から渡してもらいます。

```csharp
public class SceneTreeViewModel
{
    private readonly IEngineService _engine;

    public SceneTreeViewModel(IEngineService engine)   // 外から渡してもらう
    {
        _engine = engine;
    }
}
```

誰が渡すのか、を担当するのが DI コンテナーです。コンテナーは「`IEngineService` が欲しいと言われたら `EngineService` を作る」という登録を持っています。`SceneTreeViewModel` が必要になったとき、コンテナーはコンストラクターの引数を見て、必要なものを（芋づる式に）作って渡します。

| 用語 | 意味 |
| --- | --- |
| 登録（Register） | 「この型が欲しいと言われたら、これを作る」と教えること |
| 解決（Resolve） | コンテナーにオブジェクトを作ってもらうこと |
| 注入（Inject） | 作ったものを、コンストラクターの引数で渡すこと |
| 生存期間 | 作ったものを使い回すか、毎回作るか |

### 登録の書き方

```csharp
protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    // アプリの間ずっと 1 つだけ。みんなで共有する
    containerRegistry.RegisterSingleton<IEngineService, EngineService>();

    // 解決のたびに新しく作る
    containerRegistry.Register<ISomething, Something>();

    // インターフェースなしで、クラスだけを登録する
    containerRegistry.RegisterSingleton<AppSettings>();
}
```

エンジンの窓口やログのように、状態を共有するものは `RegisterSingleton` にします。状態を持たない小さな部品は `Register` で十分です。

DI コンテナーを使う利点は、「共有する物」と「その持ち主」が 1 か所（`RegisterTypes`）で決まることです。DI なしで同じことをしようとすると、独自のシングルトン クラスを作る、グローバル変数にする、画面から画面へ引数で配って回る、といった方法になりますが、どれもテストしにくく、あとから差し替えにくくなります。

## ViewModelLocator

画面を開くたびに「この画面のビューモデルはこれ」と書くのは面倒です。Prism の ViewModelLocator は、名前の規則でビューモデルを見つけて、`DataContext` に設定してくれます。

`Views\MainWindow.xaml` に 2 行足します。

```xml title="Views/MainWindow.xaml"
<Window x:Class="Editor.Views.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:prism="http://prismlibrary.com/"
        prism:ViewModelLocator.AutoWireViewModel="True"
        Title="{Binding Title}" Height="720" Width="1280">
    <Grid />
</Window>
```

```csharp title="ViewModels/MainWindowViewModel.cs"
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

実行すると、ウィンドウのタイトルが「MiniEngine Editor」になります。`DataContext` を書いていないのに、`{Binding Title}` が動いています。

`AutoWireViewModel="True"` が付いた画面は、名前の規則に従ってビューモデルを探します。規則は「`...Views.Xxx` の画面には、`...ViewModels.XxxViewModel`」です。末尾が `View` の画面（`SceneTreeView`）は `SceneTreeViewModel` を探します。規則に合わないときは、明示的に結び付けることもできます。

```csharp
ViewModelLocationProvider.Register<MainWindow, MainWindowViewModel>();
```

ViewModelLocator が便利なのは、ビューモデルを DI コンテナーで作ってくれる点です。つまり、ビューモデルのコンストラクターに欲しいものを書くだけで、コンテナーが渡してくれます。この後すぐ試します。

## BindableBase と SetProperty

上のコードの `BindableBase` は Prism の基底クラスで、`INotifyPropertyChanged` を実装済みです。`SetProperty(ref _title, value)` が、第 12 章の `set` に書いた 5 行を 1 行にしてくれます。やっていることは同じです。

1. 今の値と同じなら何もしない。
2. 違えば、フィールドを新しい値に更新する。
3. `PropertyChanged` を起こす（プロパティ名は `[CallerMemberName]` で自動）。

`ref` は、引数を参照渡しにするキーワードです。`SetProperty` は呼ぶ側のフィールドそのものを書き換える必要があるので、`ref _title` と渡します。C++ の `T&` に近い使い方で、呼ぶ側にも `ref` と書きます。

`SetProperty` は、値が変わったときに `true` を返します。変わったときだけ、ほかの処理もしたい場合に使えます。

```csharp
set
{
    if (SetProperty(ref _title, value))
    {
        // 変わったときだけここを通る
    }
}
```

## DelegateCommand

第 12 章で自作した `RelayCommand` の、本物にあたるのが Prism の `DelegateCommand` です。

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

押すたびに数字が増え、10 になるとボタンが自動で無効になります。

`.ObservesProperty(() => Counter)` は、「`Counter` が変わったら、`CanExecute` を聞き直して」という指定です。第 12 章で手書きした `RaiseCanExecuteChanged()` が要らなくなりました。`() => Counter` は、プロパティを「指す式」で、Prism はそこからプロパティ名を取り出しています。

似た機能として、`bool` のプロパティをそのまま「押せるかどうか」にする `.ObservesCanExecute(() => IsReady)` もあります。

引数を受け取るコマンドは `DelegateCommand<T>` で、XAML の `CommandParameter` から値を渡します。

```csharp
public DelegateCommand<string> OpenCommand { get; }
OpenCommand = new DelegateCommand<string>(path => Open(path));
```

```xml
<Button Content="開く" Command="{Binding OpenCommand}" CommandParameter="scene1.json" />
```

## DI でクラスを受け取る

最後に、ビューモデルが DI で別のクラスを受け取る例をひとつ作って、流れを確かめます。簡単なサービスを用意します。

```csharp title="Services/Greeter.cs"
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

ビューモデルのコンストラクターに、欲しいものを書きます。

```csharp
public class MainWindowViewModel : BindableBase
{
    private readonly IGreeter _greeter;

    public MainWindowViewModel(IGreeter greeter)
    {
        _greeter = greeter;
        Title = _greeter.Greet("Editor");
    }
    // ...
}
```

`MainWindowViewModel` を `new` しているコードは、どこにもありません。ViewModelLocator がコンテナーに「ビューモデルを作って」と頼み、コンテナーがコンストラクターの引数 `IGreeter` を見て `Greeter` を作って渡しているのです。この仕組みを使って、後の章でエンジンの窓口を全ビューモデルに配ります。

`Greeter` ではなく `IGreeter` を受け取っているのにも意味があります。インターフェースを受け取っていれば、テストのときに偽物の実装へ差し替えられますし、実装を入れ替えても、受け取る側は何も直さずに済みます。

## 動かして確かめる

実行して、次の点を見てください。

- ウィンドウが 1 つだけ開き、タイトルに「こんにちは、Editor さん」と出る。
- `+1` ボタンで数字が増え、10 で押せなくなる。
- 「出力」ウィンドウに `System.Windows.Data Error` が出ていない。

??? failure "起動時に `ContainerResolutionException` が出る"
    ビューモデルのコンストラクターが欲しがっている型が、登録されていません。メッセージの奥のほう（内側の例外）に、足りない型の名前が書いてあります。具体的なクラスなら登録しなくても解決できる場合がありますが、インターフェースは必ず登録が必要です。

??? failure "ウィンドウが 2 つ開く"
    `App.xaml` に `StartupUri` が残っています。消してください。

??? failure "タイトルがバインドされない"
    名前の規則を確かめます。`Views` の `MainWindow` に対して、`ViewModels` の `MainWindowViewModel` があるか。名前空間が `...Views` と `...ViewModels` になっているか。`AutoWireViewModel="True"` が書かれているか、の 3 点です。

??? failure "`PrismApplication` が見つからない（`CS0246`）"
    `using Prism.DryIoc;` が足りません。`Ctrl + .` で足せます。

??? failure "`App.xaml` と `App.xaml.cs` の基底クラスが合わないとビルドできない"
    XAML は `prism:PrismApplication`、C# は `: PrismApplication` です。片方が `Application` のままだと、ビルドが失敗します。

## 関連する章

- [第 20 章 MVVM ライブラリを比べる](20-mvvm-libraries.md)：`BindableBase` と CommunityToolkit.Mvvm の書き比べ
- [第 19 章 Prism を掘り下げる](19-prism-deep.md)：ナビゲーションの確認、KeepAlive、CompositeCommand、モジュールの遅延読み込み

次の章では、画面を「リージョン」という領域に分けて、機能ごとのモジュールが自分の画面をそこへ差し込む形に作り直します。

[第 17 章 リージョン、モジュール、ナビゲーション](17-regions-modules.md) へ進みます。

---
title: 第 18 章 Prism の起動で何が起きるか：Container と RegisterTypes
tags:
  - C#連携
---

# 第 18 章 Prism の起動で何が起きるか：Container と RegisterTypes

第 16 章の `App.xaml.cs` には、不思議な点がいくつかありました。`RegisterTypes` を、自分では一度も呼んでいません。`Container` という名前を使っていますが、どこにも宣言がありません。そもそも、`Main` 関数も見当たりません。

この章では、アプリが起動してから、ウィンドウが出るまでを、実際に動く順番で追いかけます。そのうえで、`Container` を誰が持っているのか、なぜ他のクラスから触ってはいけないのかを説明します。

!!! info "このページを読む前に"
    - [第 17 章 DI とは何か](17-di-basics.md)（登録、解決、コンストラクター インジェクションの言葉を使う）
    - [第 16 章 Prism の導入と起動の流れ](16-prism-bootstrap.md)（`App` を `PrismApplication` に作り替えた）

!!! abstract "この章での Editor"
    この章では、Editor に残るファイルは足しません。第 16 章の `App.xaml.cs` に、起動の順番を確かめるための実験コードを一時的に重ねて、あとで消します。

## `Main` が見当たらないのは、なぜか

C++ の `main` に当たる C# の `Main` は、WPF では自分で書きません。`App.xaml` のビルド アクションが `ApplicationDefinition` になっていて、ビルドのときに、`Main` が自動で生成されるからです。

生成されたコードは、`obj\Debug\net8.0-windows\App.g.cs`（フォルダー名は、ターゲットによって変わります）にあります。開くと、`App` を作って `Run()` を呼ぶ `Main` が見つかります（細かい中身は `App.xaml` の内容によって少し変わります）。

```csharp
// App.g.cs（自動生成。編集しない）
public static void Main()
{
    Editor.App app = new Editor.App();
    app.Run();
}
```

`Run()` が、WPF のメッセージ ループを回し始めます。その中で、アプリの開始を知らせる `OnStartup` が呼ばれます。ここから先は、`PrismApplication` の出番です。

## 起動の順番を、実際に確かめる

`RegisterTypes` はいつ呼ばれるのでしょうか。推測せず、確かめます。`App` のメソッドを上書きして、呼ばれた順に出力してみます。WPF のアプリには、文字を出す画面（コンソール）がないので、`Debug.WriteLine` を使います。出力は、Visual Studio の「出力」ウィンドウに出ます。

```csharp title="実験：起動の順番を確かめる（App.xaml.cs に一時的に足す。Editor には残さない）"
using System.Diagnostics;

public partial class App : PrismApplication
{
    protected override void ConfigureViewModelLocator()
    {
        Debug.WriteLine("1 ConfigureViewModelLocator");
        base.ConfigureViewModelLocator();
    }

    protected override void RegisterTypes(IContainerRegistry containerRegistry)
    {
        Debug.WriteLine("2 RegisterTypes");
        containerRegistry.RegisterSingleton<AssetScanner>();
        containerRegistry.RegisterSingleton<LogViewModel>();
        containerRegistry.RegisterSingleton<AssetBrowserViewModel>();
    }

    protected override Window CreateShell()
    {
        Debug.WriteLine("3 CreateShell");
        return Container.Resolve<MainWindow>();
    }

    protected override void InitializeShell(Window shell)
    {
        Debug.WriteLine("4 InitializeShell");
        base.InitializeShell(shell);
    }

    protected override void OnInitialized()
    {
        Debug.WriteLine("5 OnInitialized");
        base.OnInitialized();
    }
}
```

```text title="実行結果（Prism 9.0.537）"
1 ConfigureViewModelLocator
2 RegisterTypes
3 CreateShell
4 InitializeShell
5 OnInitialized
```

自分では何も呼んでいないのに、`PrismApplication` が、この順に呼んでくれています。<strong>制御がフレームワークの側にある</strong>、という第 17 章で出てきた IoC の一例です。

大事なのは、`RegisterTypes`（2）が `CreateShell`（3）より前に呼ばれていることです。そのため、`CreateShell` の中の `Container.Resolve<MainWindow>()` の時点では、登録がすべて終わっています。もし順序が逆なら、`MainWindow` が必要とする型が、まだ登録されていないことになります。

### その内側で、何が行われているか

Prism 9.0.537 の `PrismApplicationBase` のソースを読むと、順序は次のとおりです。`OnStartup` が呼ばれると、まず `ConfigureViewModelLocator()`、次に `Initialize()`、最後に `OnInitialized()` が呼ばれます。真ん中の `Initialize()` の中身は、次の順番です。

1. コンテナーを作る（`CreateContainerExtension`）。DryIoc 版では、DryIoc を包んだ `DryIocContainerExtension` が作られる
2. Prism 自身が必要とする型を登録する（`RegisterRequiredTypes`）
3. 自分の型を登録する（`RegisterTypes`）
4. モジュール、リージョンまわりの設定をする
5. シェルを作る（`CreateShell`）
6. シェルに ViewModel を結びつけ、リージョン マネージャーを設定する
7. シェルを初期化する（`InitializeShell`。`MainWindow` にシェルが設定される）
8. モジュールを初期化する（`InitializeModules`）

そのあとで `OnInitialized()` が呼ばれ、`MainWindow` が `Show()` されます。画面に出るのは、最後の最後です。

!!! warning "順序は Prism のバージョンで変わる"
    ここに書いた順序は、Prism 9.0.537 のソースで確かめたものです。古いバージョンや、将来のバージョンでは、呼ばれる順序や、メソッドの名前が違うことがあります。動きを前提にしたコードを書くときは、使っているバージョンの `PrismApplicationBase` を、F12 で開いて確かめてください。

`RegisterTypes` は、基底クラスで `abstract` です。上書きしないと、コンパイル エラーになります。登録するものが無くても、空の関数は必ず書きます。

## `Container` は、どこで宣言されているのか

`App.xaml.cs` に `Container` の宣言は無いのに、使えています。F12（定義へ移動）で `Container` に飛ぶと、基底クラスの `PrismApplicationBase` で宣言されているのが分かります。

```csharp
// PrismApplicationBase の中
public IContainerProvider Container => _containerExtension;
```

`App` は `PrismApplication` を継承しているので、そのまま使えます。型は `IContainerProvider` で、「解決（`Resolve`）する」ことだけができるインターフェースです。

実体は、さきほど確かめた `DryIocContainerExtension` です。実行して `Container.GetType().Name` を表示すると、そう出ます。これは DryIoc の `IContainer` を包んだ薄いラッパーで、Prism の共通の窓口（`IContainerProvider`、`IContainerRegistry`）と、DryIoc を結んでいます。

持ち主の関係は、次の順です。

1. `App`（WPF のプロセスの間ずっと生きている）
2. `Container`（`DryIocContainerExtension`）
3. その内側の DryIoc の `IContainer`
4. Singleton の実体

`App` が生きている間は、コンテナーも生きています。アプリが終わるとコンテナーが `Dispose` され、`IDisposable` を実装した Singleton も、そのときに破棄されます。

C++ で言えば、`main` の中でコンテナー オブジェクトをローカル変数として持ち、そこから部品を組み立てて渡している状態に近いです。`App` が、`main` の役割をしています。

## 他のクラスから `App.Container` を触ってはいけない

`Container` は、`App` から見えるだけでなく、静的な入口をたどれば、どのクラスからも取り出せてしまいます。

```csharp title="実験：悪い例（Editor には入れない）"
public class AssetBrowserViewModel : BindableBase
{
    private async Task LoadAsync()
    {
        var scanner = ((App)Application.Current).Container.Resolve<AssetScanner>();   // 取りに行く
        var files = await scanner.ScanAsync(AppContext.BaseDirectory);
        // ...
    }
}
```

動きますが、問題があります。`AssetBrowserViewModel` が `AssetScanner` に依存していることが、コンストラクターの引数に現れません。クラスの外から見て、何に頼っているのかが分からなくなります。テストのとき、コンテナーごと用意しないと動かないので、偽物の差し替えも面倒です。必要なものを外から取りに行くこの書き方は、<strong>Service Locator</strong> と呼ばれるアンチパターンです。

良い書き方は、第 17 章で見たとおり、コンストラクターで受け取ることです。

```csharp title="第 16 章の形（良い例）"
public class AssetBrowserViewModel : BindableBase
{
    private readonly AssetScanner _scanner;

    public AssetBrowserViewModel(LogViewModel log, AssetScanner scanner)
    {
        _scanner = scanner;
        // ...
    }
}
```

実行時に、どの型を作るかを選ぶファクトリーのように、どうしてもコンテナー自体が要るときは、`IContainerProvider` をコンストラクターで受け取れます。コンテナーが、自分自身を注入してくれます。

```csharp title="実験：ファクトリー（Editor には入れない）"
public class PanelFactory
{
    private readonly IContainerProvider _container;

    public PanelFactory(IContainerProvider container) => _container = container;

    public T Create<T>() => _container.Resolve<T>();
}
```

ただし、使いすぎると、これも結局 Service Locator になります。ファクトリーのような、限られた場所だけに使ってください。

## まとめ

- `Main` は、`App.xaml` のビルドで自動生成される。`Run()` の中で `OnStartup` が呼ばれる。
- `PrismApplication` が、`ConfigureViewModelLocator` → コンテナーを作る → `RegisterTypes` → `CreateShell` → `InitializeShell` → `OnInitialized` の順に呼ぶ（9.0.537 で確認）。
- `RegisterTypes` は `CreateShell` より前なので、シェルの解決の時点で、登録は終わっている。
- `Container` は `PrismApplicationBase` の `IContainerProvider`。実体は `DryIocContainerExtension`。
- 他のクラスから `App.Container` を取りに行かない。必要な物は、コンストラクターで受け取る。

## 関連する章

- [第 17 章 DI とは何か](17-di-basics.md)
- [第 19 章 登録とライフタイム](19-registration-lifetime.md)：登録しただけで、オブジェクトは作られるのか

[第 19 章 登録とライフタイム](19-registration-lifetime.md) へ進みます。

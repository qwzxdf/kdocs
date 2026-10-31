---
title: 第 22 章 DI コンテナーの種類と DryIoc
tags:
  - C#連携
---

# 第 22 章 DI コンテナーの種類と DryIoc

Prism は DryIoc を使っていますが、DI コンテナーはほかにもたくさんあります。Web で調べると Autofac や Microsoft.Extensions.DependencyInjection が出てきて、書き方が少しずつ違うので混乱しやすいところです。

この章ではコンテナーの種類を整理し、Prism が書き方をそろえている仕組みを説明します。そして、Prism を介さずに DryIoc だけを使う最小の例で、コンテナーの動きを手元で確かめます。

!!! info "このページを読む前に"
    - [第 20 章 登録とライフタイム](20-registration-lifetime.md)（`Register`、`RegisterSingleton`、`Resolve` の意味）
    - [第 18 章 DI とは何か](18-di-basics.md)

!!! abstract "この章での Editor"
    この章でも Editor にファイルは足しません。Prism を介さない DryIoc だけの動きは、別の小さなコンソール アプリで確かめます。

## DI コンテナーにはどんな種類があるのか

.NET には定番のコンテナーがいくつかあります。

- <strong>Microsoft.Extensions.DependencyInjection</strong>：.NET 標準のコンテナー。ASP.NET Core が使っている。機能は控えめでまず迷ったらこれ。
- <strong>DryIoc</strong>：軽量で高速。Prism.DryIoc が使っている。
- <strong>Autofac</strong>：機能が豊富な老舗の定番。
- <strong>Unity</strong>：Prism が昔から対応していたコンテナー。ゲーム エンジンの Unity とは別物なので、検索では注意する。
- <strong>SimpleInjector</strong>：設定ミスを起動時に見つけやすい作りになっている。
- そのほか Ninject、Castle Windsor、Lamar など。

どれも基本の発想は同じです。型を登録し解決のときにコンストラクターの引数を見て、再帰的に組み立てます。違うのは登録の書き方、ライフタイムの種類、細かい機能（スコープ、デコレーター、遅延解決など）です。

## Prism は書き方をそろえてくれる

Prism はコンテナーごとにパッケージが分かれています（`Prism.DryIoc`、`Prism.Unity` など）。どれを選んでもアプリのコードでは `IContainerRegistry`（登録する窓口）と `IContainerProvider`（解決する窓口）という、共通の窓口を使います。`RegisterTypes` が `containerRegistry` を受け取っているのは、そのためです。

```csharp title="第 20 章の形"
protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterSingleton<IAssetScanner, AssetScanner>();   // どのコンテナーでも同じ書き方
}
```

おかげでコンテナーを入れ替えても、アプリのコードはほとんど変わりません。そのかわり Prism の共通の窓口には出てこない、コンテナー固有の機能があります。

DryIoc 固有の機能（たとえば、特定の範囲だけで使い回す `Reuse.Scoped`）が必要になったら `GetContainer()` で、内側の DryIoc の `IContainer` を取り出せます。

```csharp title="実験（Editor には入れない）"
using DryIoc;
using Prism.DryIoc;

protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    IContainer dryIoc = containerRegistry.GetContainer();   // DryIoc 本来の窓口
    dryIoc.Register<IAssetScanner, AssetScanner>(Reuse.Scoped);
}
```

ただし、これを使うと Prism の共通の窓口に頼る利点（コンテナーの入れ替えやすさ）を手放すことになります。どうしても必要なときだけにします。

## C++ にも DI コンテナーはあるのか

あります。Boost.DI、Hypodermic、Fruit などです。ただし C++ ではコンテナーを使わず `main` の側で、コンストラクターの引数として手作業で渡して、組み立てることも多いです（第 18 章の Pure DI）。テンプレートの機能でコンパイル時に組み立てを検証するライブラリもあり C# とは少し違う方向に発展しています。

## DryIoc だけで使う最小の例

Prism を介さず DryIoc だけを使うとコンテナーの動きが分かりやすくなります。Editor とは別にコンソール アプリを作り NuGet で `DryIoc.dll` を入れます。

```csharp title="実験：コンソール アプリ（Editor には入れない）"
using DryIoc;

public interface ILogger
{
    void Write(string message);
}

public class ConsoleLogger : ILogger
{
    public void Write(string message) => Console.WriteLine(message);
}

public class ProjectService
{
    private readonly ILogger _logger;

    public ProjectService(ILogger logger)
    {
        _logger = logger;
    }

    public void Open(string path) => _logger.Write($"open: {path}");
}

public class Program
{
    public static void Main()
    {
        var container = new Container();

        container.Register<ILogger, ConsoleLogger>(Reuse.Singleton);
        container.Register<ProjectService>(Reuse.Singleton);

        var service = container.Resolve<ProjectService>();
        service.Open("test.prest");
    }
}
```

```text title="実行結果（DryIoc 5.4.3）"
open: test.prest
```

`ProjectService` を解決するとコンテナーはコンストラクターの `ILogger` を見て、登録済みの `ConsoleLogger` を自動で渡します。第 18 章で説明した組み立てが、そのまま動いています。

登録の書き方はよく使うものが 4 つあります。

```csharp title="実験（Editor には入れない）"
container.Register<IFoo, Foo>(Reuse.Transient);          // 解決のたびに新規作成（省略時の既定）
container.Register<IFoo, Foo>(Reuse.Singleton);          // 1 つだけ作って使い回す
container.RegisterInstance<IFoo>(new Foo());             // 自分で作った物を登録する
container.RegisterDelegate<IFoo>(r => new Foo(r.Resolve<ILogger>()));   // 作り方を自分で書く
```

`Reuse.Transient` が省略時の既定、`Reuse.Singleton` は 1 つだけ作る設定です。`RegisterInstance` は自分で作った物を渡す方法で、`RegisterDelegate` は作り方を関数で与える方法です。引数の一部を設定値などから自分で与えたいときに使います。

Prism の窓口では `Reuse` は出てきません。`RegisterSingleton` と `Register` の 2 つにまとめられているからです。

## まとめ

- DI コンテナーは DryIoc、Autofac、Microsoft.Extensions.DependencyInjection など、多数ある。基本の発想は同じ。
- Prism は `IContainerRegistry` と `IContainerProvider` で、書き方をそろえる。
- DryIoc 固有の機能が要るときは、`GetContainer()` で内側の `IContainer` を取り出せる。
- DryIoc 単体では `Register<I, T>(Reuse.Singleton)` と `Resolve<T>()` で、同じ動きを確かめられる。
- C++ でも手作業で組み立てる（Pure DI）か DI ライブラリを使う。

## 関連する章

- [第 21 章 ViewModelLocator のしくみ](21-viewmodel-locator.md)
- [第 23 章 リージョン、モジュール、ナビゲーション](23-regions-modules.md)

次の章からはまた画面づくりに戻ります。[第 23 章 リージョン、モジュール、ナビゲーション](23-regions-modules.md) へ進みます。

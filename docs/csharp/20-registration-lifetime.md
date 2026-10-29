---
title: 第 20 章 登録とライフタイム：登録しただけで、作られるのか
tags:
  - C#連携
---

# 第 20 章 登録とライフタイム：登録しただけで、作られるのか

第 17 章で `RegisterTypes` に書いた `RegisterSingleton<LogViewModel>()` で、`LogViewModel` は、その場で作られるのでしょうか。「Singleton」と書くと、アプリにひとつだけの実体になりますが、その実体は、どこにあるのでしょう。登録していない型を欲しがったら、何が起きるのでしょう。

この章では、登録と解決の違い、実体が作られるタイミング、インターフェースを挟むかどうかの判断を扱います。

!!! info "このページを読む前に"
    - [第 19 章 Prism の起動で何が起きるか](19-prism-startup.md)（`RegisterTypes` が `CreateShell` より前に呼ばれる）
    - [第 18 章 DI とは何か](18-di-basics.md)（登録、解決、注入）

!!! abstract "この章での Editor"
    前半は、仕組みを確かめる実験です。Editor の中だとウィンドウなどが絡んで分かりにくいので、別の小さなコンソール アプリ（NuGet で `Prism.DryIoc` を入れる）で行い、Editor には入れません。後半の「インターフェースを挟む」では、Editor の `AssetScanner` に実際に手を入れます。

## 登録は「レシピを書く」だけ

`RegisterTypes` の時点では、実体は作られません。確かめます。作られたときに出力するクラスを用意します。

```csharp title="実験：コンソール アプリ（Editor には入れない）"
public class ConsoleLogger : ILogger
{
    public ConsoleLogger() { Console.WriteLine("  [new ConsoleLogger]"); }
    public void Write(string message) => Console.WriteLine(message);
}
```

```csharp title="実験（Editor には入れない）"
var container = new DryIocContainerExtension();   // Prism.DryIoc のコンテナー
container.RegisterSingleton<ILogger, ConsoleLogger>();
Console.WriteLine("登録した");
var a = container.Resolve<ILogger>();
var b = container.Resolve<ILogger>();
Console.WriteLine("同じ実体: " + ReferenceEquals(a, b));
```

```text title="実行結果（Prism.DryIoc 9.0.537）"
登録した
  [new ConsoleLogger]
同じ実体: True
```

「登録した」の時点では、`new ConsoleLogger` は走っていません。`Resolve` を呼んだ最初の 1 回で作られ、2 回目の `Resolve` は、同じ実体を返しています。

つまり、`RegisterSingleton<ILogger, ConsoleLogger>()` が、コンテナーに入れる情報は、「`ILogger` が要求されたら、`ConsoleLogger` を 1 つだけ作って使い回す」という、レシピだけです。実体は、最初に必要とされたときに、作られます（遅延生成）。

## Singleton と Transient

実体を使い回すかどうかを、ライフタイムと呼びます。Prism の窓口には、2 種類あります。

<strong>`RegisterSingleton`</strong> は、コンテナーが 1 つだけ作って、全員に同じものを渡します。エンジンの窓口やログのように、状態を共有する物に使います。

<strong>`Register`</strong> は、解決のたびに、新しいインスタンスを作ります（Transient）。状態を持たない小さな部品や、利用者ごとに別の状態を持たせたい物に使います。

```csharp title="実験（Editor には入れない）"
container.Register<Plain>();
var p1 = container.Resolve<Plain>();
var p2 = container.Resolve<Plain>();
Console.WriteLine("同じ実体: " + ReferenceEquals(p1, p2));   // False
```

Singleton の実体が入っている場所は、`App` ではなく、コンテナーの内部です。C# のクラスは参照型なので、渡されるのは実体への参照です。C++ の `IFoo&` や `std::shared_ptr<IFoo>` を、みんなが持っている状態に近いと考えてください。

アプリが終了すると、コンテナーが破棄されるときに、`IDisposable` を実装した Singleton の `Dispose` も呼ばれます。ファイルやスレッドを持つ Singleton は、ここで後始末できます。

## 起動時に、作っておきたいとき

遅延生成は便利ですが、「起動時に必ず作っておきたい」ものもあります。たとえば、最初のログ ファイルを開く処理です。方法は 2 つあります。

ひとつは、自分で `Resolve` を呼ぶ方法です。

```csharp title="実験（Editor には入れない）"
protected override void OnInitialized()
{
    Container.Resolve<ILogger>();   // ここで作られる
    base.OnInitialized();
}
```

もうひとつは、自分で作った物を、そのまま登録する方法です。

```csharp title="実験（Editor には入れない）"
containerRegistry.RegisterInstance<ILogger>(new ConsoleLogger());
```

こちらは、登録の時点で `new` が走ります。コンストラクターに引数が要るときも、自分で渡せます。ただし、DI コンテナーに作らせる利点（引数を自動で組み立てる）は、使えません。

## 登録していない型を欲しがったら

登録を忘れると、何が起きるのでしょうか。確かめます。

```csharp title="実験（Editor には入れない）"
var container = new DryIocContainerExtension();   // 何も登録していない
var plain = container.Resolve<Plain>();            // 具体的なクラス
container.Resolve<ILogger>();                      // インターフェース
```

```text title="実行結果（Prism.DryIoc 9.0.537）"
  [new Plain]
```

そのあと、`ILogger` の `Resolve` で、`ContainerResolutionException` が出ます。

<strong>具体的なクラス（`Plain`）は、登録しなくても解決できます。</strong> Prism.DryIoc は、未登録の具体クラスを、その場で作る設定で動いているためです。ただし、毎回新しく作られる（Transient 扱い）ので、共有したい物は、登録が要ります。

<strong>インターフェース（`ILogger`）は、必ず登録が要ります。</strong> インターフェースだけでは、どのクラスを作ればよいか、コンテナーが決められないからです。

??? failure "起動時に `ContainerResolutionException` が出る"
    例外のメッセージは長いですが、読む場所は決まっています。内側の例外（`InnerException`）か、メッセージの中ほどに、「`ILogger` を解決できない」のように、足りない型の名前が書かれています。その型を `RegisterTypes` に登録してください。型の名前のつづりと、`using` の足りなさも、よく見ます。

## なぜインターフェースを挟むのか

ここまで、`ILogger` と `ConsoleLogger` のように、インターフェースと実装を分けてきました。必須ではありません。`RegisterSingleton<ProjectService>()` のように、具体的なクラスのまま登録して、そのまま受け取ることもできます。

インターフェースを挟むと、次のような場面で効きます。

- <strong>差し替え。</strong> テスト用の偽物や、メモリ上だけで動く実装を渡せる。
- <strong>依存の向きを縛る。</strong> ビューモデルは「何ができるか」だけを知り、「どう実装されているか」を知らずに済む。
- <strong>プロジェクトの分離。</strong> インターフェースだけを共通のプロジェクトに置き、実装を別のプロジェクトに置ける。

逆に、差し替える予定も、テストで偽物にする予定もないなら、インターフェースは要りません。実装が 1 つしかないクラスに、全部 `I` を付けるのは、やりすぎだと言われがちです。目安は次のとおりです。

- ファイル I/O、時刻、ネットワークなど、テストで偽物に替えたくなる物は、インターフェースを挟む。
- 純粋な計算や、単純なデータの入れ物は、具体的なクラスのままでよい。
- 迷うなら、最初は具体的なクラスで書き、必要になった時点で、インターフェースを取り出す。

インターフェースの取り出しは、IDE の機能でできます。Visual Studio では、クラス名にカーソルを置いて `Ctrl + .` を押し、「インターフェースの抽出」を選びます。自動でやってくれるのは、インターフェースの生成と、クラスへの実装の宣言までです。使う側の引数の型を `IFoo` に書き換える作業と、`RegisterTypes` の登録の変更は、自分で行います。

C++ で言えば、仮想関数を持つ抽象基底クラスを置くか、テンプレートや具体的な型で直接持つかの選択と同じです。差し替えたい場所にだけ、抽象を置きます。

### Editor で、IAssetScanner を取り出す

`AssetScanner` は、ディスクを読みます。読む場所が変わると結果が変わるので、画面の確認やテストのとき、決まった結果を返す偽物に差し替えたくなる部品です。上の目安で言えば、インターフェースを挟む側です。

`AssetScanner` から、インターフェースを取り出します。クラス名にカーソルを置いて `Ctrl + .` を押し、「インターフェースの抽出」を選ぶと、できます。

```csharp title="Services/IAssetScanner.cs（新規）"
using Editor.Models;

namespace Editor.Services;

public interface IAssetScanner
{
    Task<IReadOnlyList<FileEntry>> ScanAsync(
        string root, IProgress<double>? progress = null,
        Action<string>? log = null, CancellationToken token = default);
}
```

```csharp title="Services/AssetScanner.cs（変更：宣言だけ）"
public class AssetScanner : IAssetScanner
```

使う側の引数の型と、登録は、自分で書き換えます。

```csharp title="Modules/Asset/AssetViewModel.cs（変更）"
private readonly IAssetScanner _scanner;

public AssetViewModel(LogViewModel log, IAssetScanner scanner)
```

```csharp title="App.xaml.cs（変更）"
containerRegistry.RegisterSingleton<IAssetScanner, AssetScanner>();   // 前は RegisterSingleton<AssetScanner>()
```

実行して、第 17 章までと同じに動けば成功です。見た目は何も変わりません。変わったのは、`AssetViewModel` が「本物のディスクを読むクラス」ではなく、「`ScanAsync` できる物」だけを知っている点です。

その効果を確かめるために、偽物を作ってみます。Editor には入れない実験です。

```csharp title="実験：決まった結果を返す偽物（Editor には入れない）"
public class FakeAssetScanner : IAssetScanner
{
    public Task<IReadOnlyList<FileEntry>> ScanAsync(
        string root, IProgress<double>? progress = null,
        Action<string>? log = null, CancellationToken token = default)
    {
        IReadOnlyList<FileEntry> files = new[] { new FileEntry("fake.png", "texture", 1_024) };
        return Task.FromResult(files);
    }
}
```

`RegisterTypes` の登録を `RegisterSingleton<IAssetScanner, FakeAssetScanner>()` に替えるだけで、読み込みボタンを押すと、ディスクを見ずに `fake.png` の 1 件が出ます。`AssetViewModel` は、1 行も直していません。確かめたら、元の登録に戻してください。

## まとめ

- 登録は「レシピを書く」だけ。実体は、最初に `Resolve` されたときに作られる（遅延生成）。
- `RegisterSingleton` は 1 つを使い回す。`Register` は毎回新しく作る。
- 起動時に作りたいなら、自分で `Resolve` するか、`RegisterInstance` で渡す。
- 具体的なクラスは未登録でも解決できる（Prism.DryIoc の設定）が、インターフェースは登録が必須。
- インターフェースは、差し替えたい物にだけ挟む。

## 関連する章

- [第 19 章 Prism の起動で何が起きるか](19-prism-startup.md)
- [第 21 章 ViewModelLocator のしくみ](21-viewmodel-locator.md)：ビューモデルが、コンテナー経由で作られる経路

[第 21 章 ViewModelLocator のしくみ](21-viewmodel-locator.md) へ進みます。

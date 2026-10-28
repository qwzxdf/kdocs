---
title: 第 17 章 DI とは何か：IoC・DI・DI コンテナー
tags:
  - C#連携
---

# 第 17 章 DI とは何か：IoC・DI・DI コンテナー

第 16 章で、ビューモデルのコンストラクターに `IGreeter` と書くだけで、`Greeter` が渡されました。便利でしたが、「誰が、いつ、どうやって渡したのか」は、はっきりしないまま進めました。ここから 5 つの章をかけて、この仕組みを順に読み解きます。

この章では、まず言葉を整理します。IoC、DI、DI コンテナーは、よく一緒に出てきて、区別がつきにくい言葉です。それぞれが何を指すのか、なぜそんなものが要るのかを、C++ の書き方と比べながら見ていきます。

!!! info "このページを読む前に"
    - [第 16 章 Prism の導入と起動の流れ](16-prism-bootstrap.md)（`RegisterTypes` と ViewModelLocator を一度動かしてある）
    - [第 5 章 C++ を知っている人のための C# 入門](05-csharp-basics.md)（インターフェースとコンストラクターの書き方）

## 自分で new すると、何が困るのか

シーン ツリーのビューモデルが、エンジンの窓口（`EngineService`）を使う場面を考えます。DI を知らないと、次のように書きたくなります。

```csharp
public class SceneTreeViewModel
{
    private readonly EngineService _engine = new EngineService();   // 自分で作る
}
```

動きます。ただし、エディタが育つにつれて、次のような困りごとが出ます。

`EngineService` が、ログ出力の `Logger` を必要とするようになったとします。`new EngineService(new Logger())` と書き直しますが、`EngineService` を作っている場所が 10 か所あれば、10 か所とも直さなければなりません。さらに `Logger` がファイルのパスを必要とするようになれば、また全部の場所に波及します。

テストのときは、本物のエンジンではなく、偽物の `EngineService` を使いたくなります。しかし、`SceneTreeViewModel` の中で `new` しているので、外から差し替える手段がありません。

複数のビューモデルが、同じ `EngineService` を共有したいときも困ります。それぞれが `new` すると、別々のインスタンスができてしまいます。

C++ で言えば、クラスのメンバーに `EngineService engine_;` を値で持たせて、コンストラクターの中で作っているのと同じ状態です。作り方を変えたとき、そのクラスを書き換えるしかありません。

## 必要なものを、外から渡してもらう

解決の方向は単純で、<strong>必要なものを自分で作らず、コンストラクターの引数で受け取る</strong>ことです。

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

これを<strong>コンストラクター インジェクション</strong>と呼びます。クラスは「何が必要か」を引数で宣言するだけで、「どれを、どう作るか」を知らなくて済みます。

得られるものは 3 つあります。

- 引数の一覧を見れば、そのクラスが何に頼っているかが、一目で分かります。
- 本物の代わりに、偽物（テスト用の実装）を渡せます。
- 「作る係」と「使う係」が分かれるので、`EngineService` の作り方が変わっても、`SceneTreeViewModel` は書き換えずに済みます。

C++ では、コンストラクターで `IEngineService&` や `std::unique_ptr<IEngineService>` を受け取る形と、同じ発想です。C# の参照型は、変数が実体そのものではなく、実体を指す参照なので、`IEngineService&` を受け取っている感覚に近いと考えると、つかみやすくなります。

## IoC、DI、DI コンテナーは何が違うのか

ここまでの話に、3 つの言葉を当てはめます。

<strong>IoC</strong>（Inversion of Control、制御の反転）は、設計の原則です。普通のプログラムは、自分のクラスが自分で依存を `new` して、生成も呼び出しも、自分で制御しています。IoC は、この制御の主導権を、外側（フレームワークなど）に渡す、という考え方です。クラスは「何が必要か」を宣言するだけで、「どれを、いつ、どう作るか」は外が決めます。

<strong>DI</strong>（Dependency Injection、依存性注入）は、IoC を実現する具体的な手法のひとつです。依存するオブジェクトを、コンストラクターの引数などから渡します。上で書いたコンストラクター インジェクションが、その代表です。

<strong>DI コンテナー</strong>は、DI を自動でやってくれる道具です。DryIoc や Autofac などがあります。「この型が欲しいと言われたら、これを作る」という登録を持っていて、引数を見て、必要なものを順に作って渡します。

つまり、IoC が考え方、DI が手法、DI コンテナーが道具です。

IoC は、DI 以外の形でも現れます。WPF で、自分は `Main` の中のメッセージ ループを書かず、`OnStartup` や `CreateShell` といった関数を用意しておくだけで、フレームワークが適切なタイミングで呼んでくれるのも、IoC の一種です。制御がフレームワークの側にあるからです。この様子は「Don't call us, we'll call you（こちらから呼ばないで。こちらから呼びます）」という標語で呼ばれます。

## コンテナーが無いと、どう組み立てるのか

DI コンテナーが無くても、DI はできます。自分で、順に組み立てて渡せばよいのです。

```csharp
var logger = new ConsoleLogger();
var engine = new EngineService(logger);
var viewModel = new SceneTreeViewModel(engine);
```

アプリの一番外側（C++ の `main`、C# の起動処理）で、全部を組み立てて渡します。これを、コンテナーを使わない DI という意味で、Pure DI と呼ぶことがあります。小さなアプリなら、これで十分です。C++ では、コンテナー ライブラリを使わず、`main` で手作業で組み立てる流儀が、よく選ばれます。

困るのは、規模が大きくなったときです。エディタには、ビューモデルが何十個もあり、それぞれが違う組み合わせの部品を必要とします。この組み立てを手で書くと、長くて、直しにくくなります。引数が 1 つ増えるたびに、組み立てのコードを探して直すことになります。

DI コンテナーは、この「組み立て」を、型の登録と、コンストラクターの引数の型だけから、自動でやってくれる道具です。

## 登録したあと、何が起きるのか

第 16 章の例を、もう一度見ます。

```csharp
// App.xaml.cs の RegisterTypes
containerRegistry.RegisterSingleton<IGreeter, Greeter>();
```

```csharp
public MainWindowViewModel(IGreeter greeter) { ... }
```

`MainWindowViewModel` をコンテナーに作ってもらうと、次の順で組み立てられます。

1. コンテナーが、`MainWindowViewModel` のコンストラクターの引数を調べる
2. `IGreeter` が要ることが分かる
3. 登録を見て、`IGreeter` には `Greeter` を使うと分かる
4. `Greeter` を作る（`Greeter` のコンストラクターに引数があれば、同じ手順を繰り返す）
5. 作った `Greeter` を引数にして、`MainWindowViewModel` を作る

引数の先に、さらに別の依存があっても、コンテナーは再帰的に、全部をたどって組み立てます。

## 動かない例：自分で new すると、注入されない

注入が働くのは、<strong>コンテナーが作ったオブジェクト</strong>に対してだけです。自分で `new` した瞬間に、コンテナーの出番はありません。

```csharp
var vm = new MainWindowViewModel();   // コンパイル エラー
```

`MainWindowViewModel` のコンストラクターは `IGreeter` を要求しているので、引数なしの `new` は、そもそも書けません（`CS7036` などのエラー）。書くなら、自分で引数を渡すことになります。

```csharp
var vm = new MainWindowViewModel(new Greeter());   // 動くが、DI を使っていない
```

これは動きますが、注入ではなく、手で組み立てているだけです。`Greeter` の作り方が変わるたびに、ここも直すことになり、DI の利点が消えます。

「注入されない」バグの典型的な原因は、次の 2 つです。

- ビューモデルを、コンテナーを通さずに `new` している。コンテナー経由で作ってもらう方法は、第 18 章で見ます。
- 注入してほしい型を、`RegisterTypes` に登録していない。これは第 19 章で扱います。

!!! tip "どこまで DI にするのか"
    DI にするのは、差し替えたい物、共有したい物、他のクラスに依存する物です。`Vector3` のような値の入れ物や、単純な計算だけのクラスまで、すべて注入にする必要はありません。「テストで偽物に替えたくなるか」「複数の場所で共有するか」を、目安にします。

## まとめ

- 自分で `new` すると、作り方の変更が波及し、差し替えもできない。
- 必要な物はコンストラクターの引数で受け取る（コンストラクター インジェクション）。
- IoC は考え方、DI は手法、DI コンテナーは道具。
- コンテナーは、登録と引数の型から、必要な物を再帰的に作って渡す。
- 注入が効くのは、コンテナーが作ったオブジェクトだけ。

## 関連する章

- [第 16 章 Prism の導入と起動の流れ](16-prism-bootstrap.md)：最初の DI の例
- [第 18 章 Prism の起動で何が起きるか](18-prism-startup.md)：`RegisterTypes` は誰がいつ呼ぶのか、`Container` は誰が持つのか

[第 18 章 Prism の起動で何が起きるか](18-prism-startup.md) へ進みます。

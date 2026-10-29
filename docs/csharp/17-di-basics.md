---
title: 第 17 章 DI とは何か：IoC・DI・DI コンテナー
tags:
  - C#連携
---

# 第 17 章 DI とは何か：IoC・DI・DI コンテナー

第 16 章で、`AssetBrowserViewModel` のコンストラクターに `LogViewModel` と `AssetScanner` と書くだけで、コンテナーが両方を作って渡してくれました。便利でしたが、「誰が、いつ、どうやって渡したのか」は、はっきりしないまま進めました。ここから 5 つの章をかけて、この仕組みを順に読み解きます。

この章では、まず言葉を整理します。IoC、DI、DI コンテナーは、よく一緒に出てきて、区別がつきにくい言葉です。それぞれが何を指すのか、なぜそんなものが要るのかを、Editor の実物と、C++ の書き方と比べながら見ていきます。

!!! info "このページを読む前に"
    - [第 16 章 非同期処理と UI スレッド](16-async-ui.md)（「作る係と使う係を分ける」の節で、`RegisterTypes` に登録して、コンストラクターで受け取るところまで動かしてある）
    - [第 12 章 Prism の導入と起動の流れ](12-prism-bootstrap.md)（`App` と ViewModelLocator）
    - [第 5 章 C++ を知っている人のための C# 入門](05-csharp-basics.md)（インターフェースとコンストラクターの書き方）

!!! abstract "この章での Editor"
    この章では、Editor にファイルを足しません。第 16 章で `RegisterTypes` に書いた 3 行と、2 つのコンストラクターを読み直して、その裏にある考え方を調べます。

## 自分で new すると、何が困るのか

第 16 章の途中までの `AssetBrowserViewModel` は、使う部品を、自分の中で作っていました。

```csharp title="第 16 章の途中までの書き方"
public class AssetBrowserViewModel : BindableBase
{
    private readonly AssetScanner _scanner = new();     // 自分で作る
    private readonly LogViewModel _log;

    public AssetBrowserViewModel(LogViewModel log) => _log = log;
}
```

動きます。ただし、エディタが育つにつれて、次のような困りごとが出ます。

`AssetScanner` が、除外するフォルダーの一覧を必要とするようになったとします。`new AssetScanner(excludes)` と書き直しますが、`AssetScanner` を作っている場所をすべて探して直さなければなりません。作っている場所が `AssetBrowserViewModel` のほかにもあると、直し漏れが起きます。

テストのときは、本物のディスクを読む `AssetScanner` ではなく、決まった結果を返す偽物を使いたくなります。しかし、`AssetBrowserViewModel` の中で `new` しているので、外から差し替える入口がありません。

複数のビューモデルが、同じ `LogViewModel` を共有したいときも困ります。それぞれが `new` すると、別々のインスタンスができて、ログが別々の一覧に入ってしまいます。`MainWindowViewModel` が `Log` を作って `AssetBrowserViewModel` に渡していたのは、その共有のためでした。

C++ で言えば、クラスのメンバーに `AssetScanner scanner_;` を値で持たせて、コンストラクターの中で作っているのと同じ状態です。作り方を変えたとき、使っている側を全部直すことになります。

## 必要なものを、外から渡してもらう

解決の方向は単純で、<strong>必要なものを自分で作らず、コンストラクターの引数で受け取る</strong>ことです。第 16 章で書き換えた形が、まさにそれです。

```csharp title="ViewModels/AssetBrowserViewModel.cs（第 16 章の形）"
public class AssetBrowserViewModel : BindableBase
{
    private readonly AssetScanner _scanner;
    private readonly LogViewModel _log;

    public AssetBrowserViewModel(LogViewModel log, AssetScanner scanner)   // 外から渡してもらう
    {
        _log = log;
        _scanner = scanner;
    }
}
```

これを<strong>コンストラクター インジェクション</strong>と呼びます。クラスは「何が必要か」を引数で宣言するだけで、「どれを、どう作るか」は知りません。

得られるものは 3 つあります。

- 引数の一覧を見れば、そのクラスが何に頼っているかが、一目で分かります。`AssetBrowserViewModel` は、ログとスキャナーに頼っています。
- 本物の代わりに、偽物（テスト用の実装）を渡せます。
- 「作る係」と「使う係」が分かれるので、`AssetScanner` の作り方が変わっても、`AssetBrowserViewModel` は書き換えずに済みます。

C++ では、コンストラクターで `IAssetScanner&` や `std::unique_ptr<IAssetScanner>` を受け取る形と、同じ発想です。C# の参照型は、変数が実体そのものではなく、実体を指す参照なので、`IAssetScanner&` を受け取っている感覚に近いと考えると、つかみやすくなります。

## IoC、DI、DI コンテナーは何が違うのか

ここまでの話に、3 つの言葉を当てはめます。

<strong>IoC</strong>（Inversion of Control、制御の反転）は、設計の原則です。普通のプログラムは、自分のクラスが自分で依存を `new` して、生成も呼び出しも、自分で制御しています。IoC は、この制御の主導権を、外側（フレームワークなど）に渡す、という考え方です。クラスは「何が必要か」を宣言するだけで、「どれを、いつ、どう作るか」は外が決めます。

<strong>DI</strong>（Dependency Injection、依存性注入）は、IoC を実現する具体的な手法のひとつです。依存するオブジェクトを、コンストラクターの引数などから渡します。上で書いたコンストラクター インジェクションが、その代表です。

<strong>DI コンテナー</strong>は、DI を自動でやってくれる道具です。DryIoc や Autofac などがあります。「この型が欲しいと言われたら、これを作る」という登録を持っていて、引数を見て、必要なものを順に作って渡します。

つまり、IoC が考え方、DI が手法、DI コンテナーが道具です。

IoC は、DI 以外の形でも現れます。WPF で、自分は `Main` の中のメッセージ ループを書かず、`OnStartup` や `CreateShell` といった関数を用意しておくだけで、フレームワークが適切なタイミングで呼んでくれるのも、IoC の一種です。制御がフレームワークの側にあるからです。この様子は「Don't call us, we'll call you（こちらから呼ばないで。こちらから呼びます）」という標語で呼ばれます。

## コンテナーが無いと、どう組み立てるのか

DI コンテナーが無くても、DI はできます。自分で、順に組み立てて渡せばよいのです。Editor の画面を、手で組み立てると、こうなります。

```csharp title="実験：コンテナーなしで Editor を組み立てる（Editor には入れない）"
var log = new LogViewModel();
var scanner = new AssetScanner();
var assetBrowser = new AssetBrowserViewModel(log, scanner);
var main = new MainWindowViewModel(log, assetBrowser);
```

アプリの一番外側（C++ の `main`、C# の起動処理）で、全部を組み立てて渡します。これを、コンテナーを使わない DI という意味で、Pure DI と呼ぶことがあります。小さなアプリなら、これで十分です。C++ では、コンテナー ライブラリを使わず、`main` で手作業で組み立てる流儀が、よく選ばれます。

困るのは、規模が大きくなったときです。エディタには、ビューモデルがこれから何十個も増え、それぞれが違う組み合わせの部品を必要とします。上の 4 行は、今の 2 つの画面だけで 4 行ですが、パネルが増えるたびに、組み立てのコードを探して直すことになります。引数が 1 つ増えるたびにも、同じです。

DI コンテナーは、この「組み立て」を、型の登録と、コンストラクターの引数の型だけから、自動でやってくれる道具です。

## 登録したあと、何が起きるのか

第 16 章で書いた登録を、もう一度見ます。

```csharp
// App.xaml.cs の RegisterTypes
containerRegistry.RegisterSingleton<AssetScanner>();
containerRegistry.RegisterSingleton<LogViewModel>();
containerRegistry.RegisterSingleton<AssetBrowserViewModel>();
```

```csharp
public MainWindowViewModel(LogViewModel log, AssetBrowserViewModel assetBrowser) { ... }
```

`MainWindowViewModel` をコンテナーに作ってもらうと、次の順で組み立てられます。

1. コンテナーが、`MainWindowViewModel` のコンストラクターの引数を調べる
2. `LogViewModel` と `AssetBrowserViewModel` が要ることが分かる
3. `AssetBrowserViewModel` のコンストラクターを調べると、`LogViewModel` と `AssetScanner` が要ることが分かる
4. `AssetScanner` を作る。`LogViewModel` を作る（登録が Singleton なので、1 つだけ）
5. それらを引数にして `AssetBrowserViewModel` を作る
6. `LogViewModel` と `AssetBrowserViewModel` を引数にして、`MainWindowViewModel` を作る

引数の先に、さらに別の依存があっても、コンテナーは再帰的に、全部をたどって組み立てます。さっきの手作業の 4 行を、コンテナーが代わりにやっています。

## 動かない例：自分で new すると、注入されない

注入が働くのは、<strong>コンテナーが作ったオブジェクト</strong>に対してだけです。自分で `new` した瞬間に、コンテナーの出番はありません。

```csharp
var vm = new MainWindowViewModel();   // コンパイル エラー
```

`MainWindowViewModel` のコンストラクターは `LogViewModel` と `AssetBrowserViewModel` を要求しているので、引数なしの `new` は、そもそも書けません（`CS7036` などのエラー）。書くなら、自分で引数を渡すことになります。

```csharp
var vm = new MainWindowViewModel(new LogViewModel(), ...);   // 動くが、DI を使っていない
```

これは動きますが、注入ではなく、手で組み立てているだけです。`LogViewModel` の作り方が変わるたびに、ここも直すことになり、DI の利点が消えます。しかもここで作った `LogViewModel` は、ほかの場所の `LogViewModel` とは別の実体になるので、ログが分かれて入ります。

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

- [第 16 章 非同期処理と UI スレッド](16-async-ui.md)：最初の DI の例（登録とコンストラクターでの受け取り）
- [第 12 章 Prism の導入と起動の流れ](12-prism-bootstrap.md)：`Container.Resolve` が最初に出てきた所
- [第 18 章 Prism の起動で何が起きるか](18-prism-startup.md)：`RegisterTypes` は誰がいつ呼ぶのか、`Container` は誰が持つのか

[第 18 章 Prism の起動で何が起きるか](18-prism-startup.md) へ進みます。

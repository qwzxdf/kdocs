---
title: 第 20 章 ViewModelLocator のしくみ：画面とビューモデルは、どうつながるのか
tags:
  - C#連携
---

# 第 20 章 ViewModelLocator のしくみ：画面とビューモデルは、どうつながるのか

第 16 章では、XAML に `prism:ViewModelLocator.AutoWireViewModel="True"` と 1 行書くだけで、`DataContext` を書かなくても、バインディングが動きました。このとき、ビューモデルは、いつ、誰が、どこで作っているのでしょうか。名前が合わなかったら、どうなるのでしょうか。

この章では、画面（View）とビューモデルが結びつくまでの流れを、順に追いかけます。

!!! info "このページを読む前に"
    - [第 19 章 登録とライフタイム](19-registration-lifetime.md)（コンテナーに作らせる、という言い方を使う）
    - [第 18 章 Prism の起動で何が起きるか](18-prism-startup.md)（`ConfigureViewModelLocator` が最初に呼ばれる）

!!! abstract "この章での Editor"
    この章では、Editor に残るファイルは足しません。第 16 章で `Views` に移した `MainWindow` で何が起きているかを、コンストラクターに出力を足して確かめます（確かめたら消します）。

## `AutoWireViewModel="True"` の裏で起きていること

`MainWindow` を、コンテナーに作ってもらったときの流れを、実際の出力で確かめます。`MainWindow.xaml` には `AutoWireViewModel="True"` を書き、`MainWindowViewModel` のコンストラクターは `LogViewModel` と `AssetBrowserViewModel` を要求しています。各クラスのコンストラクターの先頭と、`MainWindow` のコンストラクターの前後に、`Debug.WriteLine` を一時的に足して、「出力」ウィンドウを見ます。

```csharp title="実験：コンストラクターに出力を足す（Editor には残さない）"
// LogViewModel、AssetScanner、AssetBrowserViewModel、MainWindowViewModel のコンストラクターの先頭
Debug.WriteLine("  [new LogViewModel]");      // 名前は、それぞれのクラス名にする

// MainWindow のコンストラクター
public MainWindow()
{
    Debug.WriteLine("  [MainWindow ctor 開始]");
    InitializeComponent();
    Debug.WriteLine($"  [MainWindow ctor 終了] DataContext = {DataContext?.GetType().Name}");
}
```

```text title="「出力」ウィンドウの表示（Prism 9.0.537）"
  [MainWindow ctor 開始]
  [new LogViewModel]
  [new AssetScanner]
  [new AssetBrowserViewModel]
  [new MainWindowViewModel]
  [MainWindow ctor 終了] DataContext = MainWindowViewModel
```

番号を付けて読み解くと、こうなります。

1. `MainWindow` のコンストラクターが始まる。
2. コンストラクターの中で `InitializeComponent()` が呼ばれ、XAML が読み込まれる。
3. XAML の `AutoWireViewModel="True"` が設定された瞬間に、ViewModelLocator が動く。
4. ViewModelLocator が、名前の規則で、`MainWindowViewModel` という型を探す。
5. その型を、コンテナーに作ってもらう（`ConfigureViewModelLocator` で、そう設定してある）。
6. コンテナーが、コンストラクターの引数を左から順に、`LogViewModel`、`AssetBrowserViewModel`（その引数の `AssetScanner` も）を作って渡し、`MainWindowViewModel` を作る。
7. できた `MainWindowViewModel` が、`DataContext` に設定される。
8. コンストラクターが終わる。このとき、`DataContext` は、すでに入っている。

重要なのは、ビューモデルを作る係が、ViewModelLocator ではなくコンテナーだということです。ViewModelLocator は「どの型か」を探すだけで、実際の組み立てはコンテナーに任せています。だから、ビューモデルのコンストラクターで、欲しい物を書くだけで、注入されます。

## ビューモデルの探し方：名前の規則

ViewModelLocator が型を探す規則は、Prism のソースで確かめられます（`ViewModelLocationProvider` の既定の規則）。

- 画面の完全な名前（名前空間つき）を取る。
- その中の `.Views.` を `.ViewModels.` に置き換える。`.Views.` がなければ何も変わらないので、画面と同じ名前空間で探すことになる。
- 画面の名前の末尾が `View` なら `Model` を、そうでなければ `ViewModel` を足す。
- 画面と同じアセンブリ（同じプロジェクト）の中から探す。

具体的には、次のように決まります。

- `Editor.Views.MainWindow` には `Editor.ViewModels.MainWindowViewModel`（`View` で終わらないので、`ViewModel` を足す。`Views` と `ViewModels` のフォルダーに分けて置く、第 16 章の形）
- `Editor.Modules.SceneTree.SceneTreeView` には `Editor.Modules.SceneTree.SceneTreeViewModel`（`View` で終わるので、`Model` を足す。機能ごとのフォルダーに、画面とビューモデルを並べる形。第 22 章で使います）
- `Editor.MainWindow` には `Editor.MainWindowViewModel`（`.Views.` がないので、置き換えは起きない）

Editor は、第 16 章で上の 1 つ目の形にしました。第 22 章からは、2 つ目の形でも画面を作ります。どちらの形でも、規則は同じです。

## 動かないとき

ビューモデルが結びつかない原因は、ほとんど次の 3 つのどれかです。

- XAML に `AutoWireViewModel="True"` が書かれていない。
- 名前の規則から外れている。画面とビューモデルの名前空間が違う、ビューモデルが別のプロジェクトにある、名前の末尾が違う、など。
- ビューモデルの引数の型が、登録されていない（第 19 章）。

最初の 2 つは、バインディングが空振りして、画面に何も出ません。出力ウィンドウに `System.Windows.Data Error: 40 : BindingExpression path error` が出ているときは、`DataContext` が `null` のままのことが多いです。

### 規則から外れる場合は、明示的に結ぶ

名前や配置が規則に合わないときは、画面とビューモデルの組み合わせを、明示的に登録できます。たとえば、第 16 章で `MainWindow` を `Views` に移し忘れて、`Editor.MainWindow` のままにしたとします。規則は `Editor.MainWindowViewModel` を探しますが、ビューモデルは `Editor.ViewModels` にあるので、見つかりません。移し忘れを直すか、次のように結びます。

```csharp
protected override void ConfigureViewModelLocator()
{
    base.ConfigureViewModelLocator();
    ViewModelLocationProvider.Register<MainWindow, MainWindowViewModel>();
}
```

`Register` で登録した組み合わせは、名前の規則よりも優先されます。規則どおりの配置なら要りません。名前や名前空間が規則から外れているときや、名前の規則による探索（リフレクション）を避けたいときに使います。

`base.ConfigureViewModelLocator()` を呼ぶのを忘れないでください。基底クラスのこの関数が、「ビューモデルをコンテナーに作らせる」設定をしています。呼ばないと、ビューモデルが、コンテナーを経由せずに作られます。

## 動かない例：コンテナーが出来る前に画面を作る

画面を `new` で作っても、AutoWire は動きます。ただし、<strong>コンテナーが出来たあと</strong>に限ります。

```csharp title="実験（Editor には入れない）"
var b = new MainWindow();   // CreateShell の中など、起動の途中で自分で new
```

```text title="「出力」ウィンドウの表示（Prism 9.0.537）"
  [MainWindow ctor 開始]
  [new MainWindowViewModel]
  [MainWindow ctor 終了] DataContext = MainWindowViewModel
```

画面を自分で `new` しても、XAML の `AutoWireViewModel="True"` が働いて、ビューモデルは、コンテナー経由で作られます（`LogViewModel` などは、最初の画面を作るときにすでに作られているので、ここでは `new` が出ません）。画面を作るのが `Container.Resolve<MainWindow>()` か `new MainWindow()` かは、AutoWire の動きには関係がないのです。

動かなくなるのは、画面を作る時点で、コンテナーがまだ無い場合です。たとえば、`App` のコンストラクターの中で `new MainWindow()` と書いた場合です。

```csharp title="実験（Editor には入れない）"
public App()
{
    new MainWindow();   // コンテナーを作る前
}
```

```text title="「出力」ウィンドウの表示（Prism 9.0.537）"
  [MainWindow ctor 開始]
  例外: XamlParseException / MissingMethodException
```

起動の順序（第 18 章）では、`ConfigureViewModelLocator` が呼ばれるのは `OnStartup` の中で、`App` のコンストラクターより後です。この時点では、「ビューモデルをコンテナーに作らせる」設定がまだ入っておらず、既定の作り方（引数なしのコンストラクターで `new`）が使われます。`MainWindowViewModel` は引数付きのコンストラクターしか持たないので、`MissingMethodException` になり、XAML の読み込みが `XamlParseException` で失敗します。

??? failure "`XamlParseException` の内側に `MissingMethodException` が見える"
    画面を、起動の途中より前（`App` のコンストラクターなど）で作っていないか、確かめます。または、ビューモデルに引数なしのコンストラクターがなく、かつコンテナーを経由していない状況です。画面は、`CreateShell` 以降で作ってください。

反対に、ビューモデルを `new MainWindowViewModel()` と自分で作ると、コンストラクターの引数が要るので、そもそもコンパイルが通りません。自分で引数を渡すと動きますが、それは注入ではなく、手作業の組み立てです。

## まとめ

- AutoWire は、XAML の読み込み中に動き、ビューモデルを探して、`DataContext` に設定する。
- ビューモデルの型は、名前の規則（画面と同じ名前空間、末尾 `View` なら `Model`、そうでなければ `ViewModel`。`.Views.` があれば `.ViewModels.` に置き換える）で探す。
- 実際に作るのはコンテナーなので、ビューモデルのコンストラクターで注入が効く。
- 規則から外れるときは、`ViewModelLocationProvider.Register<TView, TViewModel>()` で明示する。
- 画面を作る時点で、コンテナーが無いと、`XamlParseException` になる。

## 関連する章

- [第 19 章 登録とライフタイム](19-registration-lifetime.md)
- [第 21 章 DI コンテナーの種類と DryIoc](21-di-containers.md)

[第 21 章 DI コンテナーの種類と DryIoc](21-di-containers.md) へ進みます。

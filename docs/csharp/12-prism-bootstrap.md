---
title: 第 12 章 Prism の導入と起動の流れ
tags:
  - C#連携
---

# 第 12 章 Prism の導入と起動の流れ

第 11 章までで、Editor の見た目はできました。ただ、シーン ツリーにもプロパティ パネルにも、まだ何も表示されていません。次の章からは、画面の裏に「データ」を持たせて、オブジェクトを選んだら名前と位置が出る、というところまで作っていきます。

そのとき、画面ごとに「この画面が表示するデータをまとめたクラス」を用意することになります。クラスを作るたびに、画面にそれを結びつける行を書いて回る。値が変わったことを画面に知らせる定型文を、毎回書く。ボタンを押したときの処理を、画面の外に持たせる部品を、自分で用意する。どれも WPF では定番の作業で、定番だからこそ、同じ形のコードが何度も並びます。

この定型作業を引き受けてくれるのが **Prism** です。WPF のアプリを育てるための部品集で、この教材では最後まで使います。そこで、データを扱う章に入る前に、先に入れてしまいます。この章でやるのは、Prism を入れることと、アプリの起動を Prism に任せる形に作り替えることだけです。画面の見た目は変わりません。

!!! info "このページを読む前に"
    - [第 11 章 スタイル、リソース、テンプレート、トリガー](11-style-template.md)（前の章。ここまでの内容が前提になる）
    - [第 6 章 WPF プロジェクトと XAML](06-wpf-xaml.md)（この章は、そこで作った `App.xaml` と `MainWindow.xaml` を書き換える）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Editor.csproj`（変更） | NuGet で Prism を入れる |
    | `App.xaml`・`App.xaml.cs`（変更） | `PrismApplication` に作り替える |
    | `MainWindowViewModel.cs`（新規） | ウィンドウの題名を持つだけの、最初のビューモデル |
    | `MainWindow.xaml`（変更） | ビューモデルを自動で結びつけ、題名をそこから読む |

## Prism は何をしてくれるのか

先に、Prism が持っている道具を見渡しておきます。全部を今覚える必要はありません。「こういう困りごとに効く部品が、そろっているらしい」と知っておけば十分で、各部品は、必要になる章で一つずつ説明します。

画面の裏のクラス（このあと、**ビューモデル**と呼びます）の書き方を楽にする道具が、まず 2 つあります。値が変わったことを画面に知らせる `BindableBase` と、ボタンの処理を持たせる `DelegateCommand` です。どちらも第 13 章で、必要になった所で出てきます。

画面とビューモデルを結びつける **ViewModelLocator** は、この章で使います。名前の規則で組み合わせを見つけてくれるので、画面を増やすたびに結びつけるコードを書かなくて済みます。

クラスが必要とする別のクラスを、自動で作って渡してくれる **DI コンテナー**もあります。これは、手で組み立てる苦労を一度味わってから導入したほうが分かりやすいので、第 17 章まで取っておきます。この章では、存在だけ触れます。

画面の一部を差し替えられる枠（リージョン）、機能を後から足せる単位（モジュール）、部品どうしが顔を合わせずに連絡できる仕組み（イベント集約）、ダイアログを開く道具は、第 22 章と第 23 章で扱います。

Prism は、ライブラリというよりフレームワークです。違いは、<strong>誰が主導権を持つか</strong>にあります。ライブラリは、こちらが好きなときに呼ぶ道具です。フレームワークは、向こうがアプリの流れを握っていて、こちらが書いたコードを、決まったタイミングで呼び出してきます。C++ で言えば、`std::sort` はライブラリ（自分で呼ぶ）、ゲーム エンジンの `Update()` はフレームワーク型（エンジンが呼ぶ）です。この章で起動の部分を Prism に任せるのは、主導権を渡す、ということです。

## NuGet で入れる

C# のライブラリは、**NuGet**（ニューゲット）という配布の仕組みから入れます。C++ の vcpkg に近いもので、パッケージの名前を指定すると、ダウンロードして、プロジェクトの参照に加えてくれます。

1. Solution Explorer で `Editor` を右クリックして、「NuGet パッケージの管理」を開きます。
2. 「参照」のタブで `Prism.DryIoc` を探して、安定版の 9.x を入れます。この教材は 9.0.537 で確かめています。

入れると、`Editor.csproj` に次の 1 行が増えます。`csproj` は、C# のプロジェクトの設定ファイル（C++ の `.vcxproj` にあたるもの）です。

```xml title="Editor.csproj（変更）"
<ItemGroup>
  <PackageReference Include="Prism.DryIoc" Version="9.0.537" />
</ItemGroup>
```

`Prism.DryIoc` を選ぶのは、Prism の本体（`Prism.Wpf`、`Prism.Core`）と、DI コンテナーの **DryIoc** が、まとめて入るからです。DI コンテナーには何種類かあって、Prism は他のもの（Unity など）にも対応していますが、この教材では DryIoc を使います。違いと理由は、第 21 章で説明します。

Prism は、版を上げると名前空間や API が変わる所があります（とくにダイアログ周り）。Web で見つけた記事のコードを写すときは、どの版向けかを確かめてください。

## App を PrismApplication にする

第 6 章で作った `App.xaml` には、`StartupUri="MainWindow.xaml"` という行がありました。起動したら、この画面を開きなさい、という指定です。この方法では、WPF が `MainWindow` を自分で `new` して表示します。私たちが作る手順の途中に入り込む余地はありません。

この先、ウィンドウを作るときには、ビューモデルを結びつけたり、必要なものを渡したりする作業が入ります。そこで、最初のウィンドウを開く役を、`StartupUri` から Prism に替えます。

まず `App.xaml` です。`Application` を `prism:PrismApplication` に変えて、`StartupUri` を消します。

```xml title="App.xaml（変更）"
<prism:PrismApplication x:Class="Editor.App"
                        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                        xmlns:prism="http://prismlibrary.com/">
    <prism:PrismApplication.Resources>
        <ResourceDictionary>
            <ResourceDictionary.MergedDictionaries>
                <ResourceDictionary Source="Themes/Dark.xaml" />
            </ResourceDictionary.MergedDictionaries>
        </ResourceDictionary>
    </prism:PrismApplication.Resources>
</prism:PrismApplication>
```

`xmlns:prism="http://prismlibrary.com/"` は、`prism:` という接頭辞を、Prism の部品に結びつける宣言です。URL の形をしていますが、Web にはアクセスしません。「この名前の部品の集まり」という印として使っているだけです。

`Application.Resources` を `PrismApplication.Resources` に書き換えているのは、タグの名前が基底クラスの名前と同じになるためです。中身（第 11 章で作った `Themes/Dark.xaml` の読み込み）は、そのまま移します。`StartupUri` を消し忘れると、Prism が開く分と合わせてウィンドウが 2 つ出てしまいます。

次に `App.xaml.cs` です。

```csharp title="App.xaml.cs（変更）"
using System.Windows;
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

    // DI コンテナーに、クラスを登録する場所（今は空）
    protected override void RegisterTypes(IContainerRegistry containerRegistry)
    {
    }
}
```

`PrismApplication` は、起動の手順（コンテナーを作る、型を登録する、最初の画面を作って表示する）を代わりに進める基底クラスです。私たちが書くのは、その手順の途中で呼ばれる 2 つの関数だけです。

`CreateShell()` は、最初に開く画面を作って返す関数です。アプリの一番外側のウィンドウを、Prism では**シェル**（殻）と呼びます。Editor では `MainWindow` がシェルです。`Container.Resolve<MainWindow>()` は、「`MainWindow` を作って」とコンテナーに頼んでいる書き方です。いまは `new MainWindow()` と変わらない動きですが、`MainWindow` が他のクラスを必要とするようになると、この書き方が効いてきます。仕組みは第 17 章で説明します。

`RegisterTypes()` は、コンテナーに「このクラスが欲しいと言われたら、これを作ってね」と教えておく場所です。いまは空のままで構いません。この関数を私たちが一度も呼んでいないのに動く理由は、第 18 章で、起動の順番を追いながら説明します。

`override` は、基底クラスの関数を、自分の中身で置き換える印です（C++ の `override` と同じ意味です）。`PrismApplication` では、この 2 つが抽象関数なので、書かないとビルドが通りません。

## 最初のビューモデルを作って結ぶ

起動は作り替わりましたが、これだけでは、何も変わっていないように見えます。Prism がちゃんと働いていることを確かめるために、最初のビューモデルを 1 つだけ作って、画面に結びつけてみます。

用語を 2 つ、ここで整理します。**ビュー**は、XAML で書いた画面のことです。**ビューモデル**は、その画面が表示するデータと、画面から受ける操作を持つ C# のクラスです。画面の見た目と、データや処理を別々のクラスに分けておくと、片方を直してももう片方に響きにくくなります。この分け方を MVVM と呼びます。考え方は第 13 章でじっくり説明するので、今は「画面の裏に、データを持つクラスが付く」と思ってください。

最初のビューモデルは、ウィンドウの題名を持つだけのクラスです。

```csharp title="MainWindowViewModel.cs（新規）"
namespace Editor;

public class MainWindowViewModel
{
    // ウィンドウの題名。ここから読まれていることを見分けるため、少し変えてある
    public string Title => "MiniEngine Editor（ビューモデルから）";
}
```

`=>` を使った書き方は、読み取り専用のプロパティです（第 5 章）。ファイルは、`MainWindow.xaml` と同じ `Editor` の直下に置きます。画面の枠になる `MainWindow` だけは、ここに置きます。シーン ツリーのように機能ごとのまとまりになる画面は、第 22 章で、フォルダーを分けて作ります。

次に、`MainWindow.xaml` の先頭を書き換えます。

```xml title="MainWindow.xaml（変更：先頭の数行）"
<Window x:Class="Editor.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        xmlns:prism="http://prismlibrary.com/"
        prism:ViewModelLocator.AutoWireViewModel="True"
        Title="{Binding Title}" Height="720" Width="1280">
    ...
```

`prism:ViewModelLocator.AutoWireViewModel="True"` が、画面とビューモデルを自動で結びつける指定です。この指定がある画面は、Prism の **ViewModelLocator** が、名前の規則でビューモデルを探してくれます。規則は単純で、画面の名前に `ViewModel` を足したクラスを、同じ名前空間から探します。`Editor.MainWindow` には `Editor.MainWindowViewModel` です。見つかったビューモデルは、画面の `DataContext` に入れられます。

`DataContext` は、「この画面は、データをここから読みます」と指しておく場所です。`Title="{Binding Title}"` は、その `DataContext` の `Title` を読んで、ウィンドウの題名にする、という宣言です。`{Binding ...}`（バインディング）の詳しい話は、次の章の主題です。ここでは、題名が XAML の文字ではなく、ビューモデルから来ていることを見るために使います。

規則の細かい部分、たとえば機能ごとのフォルダーに置いたときや、規則から外れたときの扱いは、第 20 章でまとめます。

## 動かして確かめる

`F5` で実行します。次の点を見てください。

- ウィンドウが **1 つだけ**開く。
- タイトル バーが「MiniEngine Editor（ビューモデルから）」になっている。
- 中の見た目は、第 11 章までと同じ。

題名が変わっていれば、Prism が `MainWindow` を作り、ViewModelLocator が `MainWindowViewModel` を見つけて、`DataContext` に入れ、バインディングがそれを読んだ、という流れが全部つながっています。確かめたら、`Title` の文字から「（ビューモデルから）」を消しても構いません。

??? failure "ウィンドウが 2 つ開く"
    `App.xaml` に `StartupUri` が残っています。消してください。残っていると、WPF が自分で開く分と、Prism が開く分が重なります。

??? failure "`PrismApplication` が見つからない（`CS0246`）"
    `App.xaml.cs` の `using Prism.DryIoc;` が足りません。`Ctrl + .` で足せます。NuGet の導入に失敗しているときも、同じエラーになります。`Editor.csproj` に `PackageReference` の行があるかを確認してください。

??? failure "`App.xaml` と `App.xaml.cs` の基底クラスが合わない"
    XAML は `prism:PrismApplication`、C# は `: PrismApplication` です。片方が `Application` のままだと、ビルドが失敗します。

??? failure "タイトル バーが「MainWindow」のまま、または空になる"
    ビューモデルが結びついていません。`AutoWireViewModel="True"` が書かれているか、ビューモデルのクラス名が `MainWindowViewModel`（`MainWindow` に `ViewModel` を足したもの）で、`MainWindow` と同じ名前空間（`Editor`）にあるかを確かめてください。結びつかなかったときのバインディングは、エラーにならず、黙って何も表示されないだけです。「出力」ウィンドウに `System.Windows.Data Error: 40` が出ていれば、ほぼこの原因です。

## ここまでの Editor

```text
Editor/
├─ App.xaml / App.xaml.cs        PrismApplication。CreateShell と RegisterTypes
├─ MainWindow.xaml(.cs)          AutoWireViewModel。題名はビューモデルから読む
├─ MainWindowViewModel.cs        題名を持つだけ
└─ Themes/Dark.xaml
```

## この章のまとめ

- Prism は、画面の裏のクラスの定型作業や、アプリの構造づくりを引き受ける部品集。この教材では最初から入れて使う。
- 入れるのは NuGet から。`Prism.DryIoc` で、本体と DI コンテナーが入る。
- `App` を `PrismApplication` にして、`StartupUri` を消す。最初の画面は `CreateShell()` で作り、型の登録は `RegisterTypes()` に書く。
- `AutoWireViewModel="True"` と名前の規則（`MainWindow` → `MainWindowViewModel`）で、画面とビューモデルが自動で結びつく。

## 関連する章

- [第 13 章 データバインディングと MVVM](13-binding-mvvm.md)：ビューモデルにデータを持たせて、画面とつなぐ。`BindableBase` と `DelegateCommand` も、ここで使い始める
- [第 17 章 DI とは何か](17-di-basics.md)：`Container.Resolve` と `RegisterTypes` の意味
- [第 18 章 Prism の起動で何が起きるか](18-prism-startup.md)：`RegisterTypes` を誰が呼んでいるのか
- [第 20 章 ViewModelLocator のしくみ](20-viewmodel-locator.md)：名前の規則と、規則から外れたとき

次は、ビューモデルに実際のデータを持たせて、画面とつなぎます。[第 13 章 データバインディングと MVVM](13-binding-mvvm.md) へ進みます。

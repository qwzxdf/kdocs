---
title: 第 8 章 コントロールとコンテンツ モデル
tags:
  - C#連携
---

# 第 8 章 コントロールとコンテンツ モデル

本編では `Button` や `TextBox` を説明なしに使ってきました。この章では、WPF に最初から入っているコントロールを用途別に整理し、「ボタンの中に何でも入れられる」という WPF 独特の考え方（コンテンツ モデル）と、画面の部品が作る木の構造を説明します。

!!! info "このページを読む前に"
    - [第 7 章 Visual Studio で XAML を書くコツ](07-vs-tips.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章での Editor"
    この章では、Editor にファイルを足しません。第 6 章で作った `MainWindow`（`TabControl` や `Border`）が、どのコントロールの仲間かを読み解きます。コードは、仕組みを見るための例です。

## よく使うコントロール

全部を覚える必要はありません。「やりたいこと」から探せるように、用途別に並べました。

| やりたいこと | コントロール | 一言 |
| --- | --- | --- |
| 文字を見せるだけ | `TextBlock` | 編集できない。一番軽い。文字の表示は基本これ |
| 文字を見せる（ラベル） | `Label` | `TextBlock` に近いが、アクセスキー（`_F`）を結び付けたい入力欄の見出しに向く |
| 1 行の文字入力 | `TextBox` | 複数行にするなら `AcceptsReturn="True"` |
| パスワード入力 | `PasswordBox` | `Password` はバインディングできない（安全のため） |
| 押す | `Button` | `Command` と `Content` |
| オン・オフ | `CheckBox`、`ToggleButton` | `IsChecked` は `bool?`（`null` が「どちらでもない」） |
| 択一 | `RadioButton`、`ComboBox` | `RadioButton` は同じ親の中で 1 つだけ選べる |
| 一覧から選ぶ | `ListBox`、`ListView`、`ComboBox` | 詳細は第 16 章 |
| 表 | `DataGrid` | 第 16 章 |
| 木 | `TreeView` | 第 41 章 |
| つまみで数を決める | `Slider` | `Minimum`、`Maximum`、`Value` |
| 進み具合 | `ProgressBar` | 終わりが分からないときは `IsIndeterminate="True"` |
| タブ | `TabControl` | |
| 折りたたみ | `Expander` | プロパティ パネルの見出しごとの折りたたみに便利 |
| 枠で囲む | `GroupBox`、`Border` | `GroupBox` は見出し付き |
| メニュー | `Menu`、`ContextMenu`、`ToolBar`、`StatusBar` | |
| 画像 | `Image` | `Source` に画像を指定する |
| 説明の吹き出し | `ToolTip` | 部品の `ToolTip="..."` でも設定できる |

C# のコードで使うクラスと名前が一致しているので、「こういう部品がほしい」と思ったら、Visual Studio の XAML エディタで `<` を打って候補を眺めるだけでも、見つかることが多いです。

## コンテンツ モデル：ボタンの中には何でも入る

WPF のコントロールは、「中に何を入れられるか」で大きく 3 つに分かれます。

### 1. 中身が 1 つだけのコントロール（ContentControl）

`Button`、`Label`、`CheckBox`、`Window`、`ScrollViewer`、`Border`（これは `Decorator` ですが同じように使えます）など。`Content` プロパティに 1 つだけ入ります。

```xml title="例（Editor には入れない）"
<Button Content="保存" />
```

文字を入れれば文字のボタンになりますが、`Content` に入れられるのは「文字」だけではありません。

```xml title="例（Editor には入れない）"
<Button>
    <StackPanel Orientation="Horizontal">
        <Image Source="save.png" Width="16" />
        <TextBlock Text="保存" Margin="4,0,0,0" />
    </StackPanel>
</Button>
```

アイコン付きのボタンは、こうして作ります。「ボタンの中に画像と文字を並べたパネルを 1 つ入れた」だけです。`Content` は 1 つしか入らないので、複数を並べたいときは、`StackPanel` などで包んで 1 つにまとめます。

`Content` に文字以外のオブジェクト（たとえば自作のクラス）を入れると、WPF は `ToString()` の結果を文字として出します。その見た目を変えたいときに使うのが `DataTemplate` です（第 14 章）。

### 2. 中身が複数のコントロール（ItemsControl）

`ListBox`、`ComboBox`、`TabControl`、`TreeView`、`Menu`、`DataGrid` など。要素の集まりを `Items`（直接書く）か `ItemsSource`（バインディング）で受け取ります。

```xml title="例（Editor には入れない）"
<ListBox>
    <ListBoxItem Content="Camera" />
    <ListBoxItem Content="Cube" />
</ListBox>
```

直接書くのは固定の項目向きです。データから作るときは `ItemsSource` にバインドして、1 件ごとの見た目を `ItemTemplate` で決めます。

### 3. 子を並べるだけのコントロール（Panel）

`Grid`、`StackPanel`、`DockPanel` など。`Children` に子を並べますが、XAML では `<Children>` を書かずに、そのまま入れ子にします。

## 論理ツリーとビジュアル ツリー

XAML に書いた入れ子は、部品の木になります。たとえばこの XAML は、

```xml title="例（Editor には入れない）"
<Window>
    <Grid>
        <Button Content="OK" />
    </Grid>
</Window>
```

`Window` の下に `Grid`、その下に `Button` という木です。これを論理ツリーと呼びます。自分で書いた構造のことです。

実際に画面に出るときは、各部品が内部でさらに小さな部品で組み立てられています。たとえば `Button` は、枠を描く部品と、中身（`ContentPresenter`）を表示する部品などでできています。こうして実際の描画まで展開した木をビジュアル ツリーと呼びます。

| 名前 | 何のツリーか | 見る機会 |
| --- | --- | --- |
| 論理ツリー | 自分で書いた入れ子 | `DataContext` や `Resources` の継承はこちらをたどる |
| ビジュアル ツリー | 画面に出る部品の全部 | スタイルの調整、マウスのヒットテスト、`VisualTreeHelper` |

普段はあまり意識しなくて構いません。困るのは、「`DataTemplate` や `ControlTemplate` の中にある部品に `x:Name` で名前を付けたのに、コードビハインドから見えない」ときです。テンプレートの中の部品は、テンプレートが展開されたあとのビジュアル ツリーにしかないので、名前では直接触れません。この場合は、バインディングで解決するのが基本です。

## 実行中の画面を調べる

実行中の画面にどんな部品がどう入れ子になっているのかは、Visual Studio の「ライブ ビジュアル ツリー」で見られます（第 7 章）。「この空白は、どの部品の余白なんだろう」という疑問の多くは、これで解決します。

## C++ で考えると

ゲーム エンジンのシーン グラフ（親の `Transform` が子に効く木）を作ったことがあれば、WPF の画面も同じ形です。部品は親子の木になっていて、親の `IsEnabled` が `false` なら子も押せなくなり、`DataContext` は子に受け継がれます。木をたどって親や子を探す操作は、シーン グラフでの `FindChild` に近いものです。

??? failure "`Button` に部品を 2 つ書いたら、`The property 'Content' is set more than once.`"
    `Button` の `Content` は 1 つしか持てないので、`<Button><Image /><TextBlock Text="保存" /></Button>` とは書けません。`StackPanel` などのパネルで 1 つにまとめてから入れます。`<Button><StackPanel Orientation="Horizontal"><Image /><TextBlock Text="保存" /></StackPanel></Button>` のようにします。

## ほかの章との関係

- 部品の並べ方は [第 9 章 レイアウトの仕組み](09-layout.md) で説明します。
- 見た目を変える方法は [第 11 章 スタイル、リソース、テンプレート、トリガー](11-style-template.md) です。
- リスト系の部品の詳細は [第 16 章 リストとデータ表示](16-lists.md) です。

次の章では、部品の大きさと位置がどのように決まるのかを説明します。

[第 9 章 レイアウトの仕組み](09-layout.md) へ進みます。

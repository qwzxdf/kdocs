---
title: 第 6 章 WPF プロジェクトと XAML
tags:
  - C#連携
---

# 第 6 章 WPF プロジェクトと XAML

この章では、第 1 章で作った `Editor` プロジェクトを開いて、WPF のプロジェクトに何が入っているかを読み、XAML という言語でエディタの画面の枠（メニュー、左・中・右のパネル、下のパネル、ステータス バー）を組みます。まだエンジンもデータも出てきません。XAML を書く感覚をつかむための章です。

## WPF の画面は 2 つのファイルでできている

WPF では、1 つの画面を 2 つのファイルで書きます。

| ファイル | 書く言語 | 役目 |
| --- | --- | --- |
| `MainWindow.xaml` | XAML（XML の仲間） | 画面の見た目。どんな部品をどこに置くか |
| `MainWindow.xaml.cs` | C# | 画面の動き。ボタンが押されたときの処理など（コードビハインドと呼びます） |

この 2 つは、実は 1 つのクラスを 2 つのファイルに分けて書いているだけです。XAML に書いたタグは、ビルドのときに C# のコードに変換されます。`<Button />` と書くのは、C# で `new Button()` と書くのと同じ意味です。

画面の部品を C# で 1 つずつ `new` して並べていくと、コードを読んでも画面の形が思い浮かびません。XAML なら、書いた順番と入れ子がそのまま画面の構造になるので、見た目を想像しながら書けます。これが XAML の価値です。

この教材では、最終的にコードビハインドをほとんど使わず、処理はビューモデルに書きます（第 12 章）。それでも、まずこの 2 つのファイルの関係を理解しておくことが土台になります。

## プロジェクトの中身を読む

`Editor` を展開すると、こんなファイルが並んでいます。

```text
Editor\
  Editor.csproj         プロジェクトの設定
  App.xaml / .xaml.cs   アプリ全体の設定（起動時の動作、共通のリソース）
  MainWindow.xaml / .cs 最初に開く画面
  AssemblyInfo.cs       テーマ関連の設定（あまり触らない）
```

### Editor.csproj

プロジェクトをダブルクリックすると、設定ファイルがそのまま開きます。

```xml title="Editor.csproj"
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <OutputType>WinExe</OutputType>
    <TargetFramework>net8.0-windows</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <UseWPF>true</UseWPF>
  </PropertyGroup>
</Project>
```

C++ の `.vcxproj` に比べると、驚くほど短いはずです。`.cs` ファイルは、フォルダーに置くだけで自動的にビルド対象になるので、ファイルを 1 つずつ列挙する必要がありません。

`OutputType` の `WinExe` は「画面を持つ EXE（黒いコンソールが出ない）」、`UseWPF` は「WPF のライブラリを使う」、`Nullable` は第 5 章で触れた null の見張り、`ImplicitUsings` は「よく使う `using` を自動で入れる」という設定です。

### App.xaml

```xml title="App.xaml"
<Application x:Class="Editor.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:local="clr-namespace:Editor"
             StartupUri="MainWindow.xaml">
    <Application.Resources>
    </Application.Resources>
</Application>
```

初めて見ると、`xmlns` がずらずら並んでいて身構えるかもしれません。ひとつずつ読んでいきましょう。

- `<Application>` は `Application` クラスのオブジェクトを作る、という意味です。要素の名前がそのままクラス名になります。
- `x:Class="Editor.App"` は「この XAML は `Editor.App` というクラスの一部です」という宣言です。C# 側の `partial class App` と合体して 1 つのクラスになります。`partial` は、1 つのクラスを複数のファイルに分けて書ける印です。
- `xmlns="..."` は、`Button` や `Grid` のような WPF の部品を、タグ名だけで書けるようにする宣言です。
- `xmlns:x="..."` は、XAML そのものの機能（`x:Class`、`x:Name`、`x:Key` など）を使うための宣言です。`x:` と付いているものは、WPF の部品ではなく XAML の機能だと覚えておくと整理しやすくなります。
- `xmlns:local="clr-namespace:Editor"` は、自分のプロジェクトの名前空間を `local:` という名前で使えるようにする宣言です。自作の部品を XAML に書くときに使います。
- `StartupUri` は、起動時に開く画面です。第 16 章で Prism を入れると、これは使わなくなります。

### MainWindow.xaml と、その相棒

```xml title="MainWindow.xaml"
<Window x:Class="Editor.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="MainWindow" Height="450" Width="800">
    <Grid>
    </Grid>
</Window>
```

```csharp title="MainWindow.xaml.cs"
namespace Editor;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }
}
```

`<Window>` の属性（`Title`、`Height`、`Width`）は、`Window` クラスのプロパティをそのまま設定しています。`Window` は中に置ける物が 1 つだけなので、複数の部品を置きたいときは、`Grid` のような入れ物を 1 つ置いて、その中に並べるのが決まりです。

C# 側の `InitializeComponent()` が肝心で、XAML に書いた内容から実際の部品を作って組み立てる関数です。中身はビルドのときに自動で生成されるので、自分で書く必要はありません。ただし、コンストラクターの最初で呼ぶのを忘れないでください。

## XAML の読み方

XAML は XML なので、ルールは少ししかありません。

### 要素と属性

```xml
<Button Content="押す" Width="80" Height="24" />
```

これは C# で書くとこうなります。

```csharp
var button = new Button { Content = "押す", Width = 80, Height = 24 };
```

要素が `new`、属性がプロパティの設定です。属性の値は文字列で書きますが、プロパティの型に合わせて自動で変換されます（`"80"` が数値の 80 になる）。

### 入れ子は「中身を入れる」

```xml
<Grid>
    <Button Content="OK" />
</Grid>
```

要素の中に要素を書くと、外側の要素の「中身」になります。`Grid` なら子として並び、`Button` や `Window` なら `Content` という 1 つのプロパティに入ります。

中身が文字だけなら、`Content` を書かずに `<Button>押す</Button>` と書けます。多くの部品は「入れ子で書いたものを、どのプロパティに入れるか」があらかじめ決まっていて、その名前を省略できるからです。

### プロパティ要素構文

属性では書けない複雑な値は、`部品名.プロパティ名` という子要素で書きます。

```xml
<Button>
    <Button.Content>
        <StackPanel Orientation="Horizontal">
            <TextBlock Text="保存" />
            <TextBlock Text="(Ctrl+S)" Foreground="Gray" />
        </StackPanel>
    </Button.Content>
</Button>
```

ボタンの中に、文字だけでなく別の部品を入れたいときに使います。WPF のボタンは、中に何でも入れられます。

### 添付プロパティ

```xml
<Grid>
    <Button Grid.Row="1" Grid.Column="2" Content="OK" />
</Grid>
```

`Grid.Row` は、`Button` のプロパティではありません。親の `Grid` が持っているプロパティで、「この子は何行目に置いてください」という親への指示を、子の側に書いておく仕組みです。添付プロパティと呼びます。C++ には近い仕組みがないので、最初は不思議に感じると思います。「子が親に出す注文書」くらいに考えておけば十分です。作り方は第 10 章で扱います。

### 名前を付ける（x:Name）

```xml
<TextBlock x:Name="StatusText" Text="準備完了" />
```

`x:Name` を付けると、コードビハインドから `StatusText.Text = "..."` のように、C# の変数として触れます。この教材ではできるだけ使わず、バインディング（第 12 章）で済ませます。

### 波かっこの値（マークアップ拡張）

```xml
<TextBlock Text="{Binding Name}" />
<Button Background="{StaticResource AccentBrush}" />
```

`{ ... }` で囲まれた値は、「文字列ではなく、何か処理をした結果を入れる」という意味です。これをマークアップ拡張と呼びます。よく見るのは次のものです。

| 書き方 | 意味 |
| --- | --- |
| `{Binding パス}` | データを結び付ける（第 12 章） |
| `{StaticResource キー}` | リソースを探して使う |
| `{DynamicResource キー}` | リソースを探して使い、あとで変わったら追従する |
| `{x:Static 型.メンバー}` | `static` なメンバーを使う |
| `{x:Null}` | `null` |

## 部品の並べ方（レイアウト）

WPF では、ピクセル座標で部品を置きません。代わりに「縦に並べる」「右端に寄せる」「余った分を埋める」といった指示を出し、ウィンドウの大きさに合わせて自動で並べ直してもらいます。この「並べてくれる入れ物」をパネルと呼びます。

| パネル | 並べ方 | 使いどころ |
| --- | --- | --- |
| `Grid` | 行と列の表に置く | 画面全体の分割。いちばんよく使う |
| `StackPanel` | 縦か横に一列に並べる | ボタンの列、入力欄の列 |
| `DockPanel` | 上下左右に張り付けて、最後の子が残りを埋める | メニュー、ツール バー、ステータス バーと本体 |
| `WrapPanel` | 横に並べて、あふれたら折り返す | タイル表示 |
| `Canvas` | 座標で置く | 図形やノード エディタ。普段は使わない |
| `Border` | 1 つの子を枠で囲む | 枠線、背景、余白 |
| `ScrollViewer` | 中身が大きいときにスクロールさせる | 縦に長いパネル |

### Grid の行と列

```xml
<Grid>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="200" />   <!-- 固定 200 -->
        <ColumnDefinition Width="*" />     <!-- 余りを全部もらう -->
        <ColumnDefinition Width="Auto" />  <!-- 中身に必要な分だけ -->
    </Grid.ColumnDefinitions>
    <Grid.RowDefinitions>
        <RowDefinition Height="Auto" />
        <RowDefinition Height="*" />
    </Grid.RowDefinitions>

    <TextBlock Grid.Row="0" Grid.Column="0" Text="左上" />
    <Button    Grid.Row="1" Grid.Column="1" Content="中央" />
</Grid>
```

幅や高さの指定は 3 通りです。数字は固定のサイズ、`Auto` は中身の大きさ、`*` は余った分の取り分です。`*` が 2 つあれば半分ずつ、`*` と `2*` なら 1 対 2 に分け合います。

数字の単位はピクセルではなく、「デバイス非依存単位」といって 96 分の 1 インチです。画面の拡大率が 150% の環境でも、見た目の大きさが変わらないようにするための単位です。

### 余白と配置

| プロパティ | 意味 |
| --- | --- |
| `Margin="4"` | 部品の外側の余白。`"4,2"` なら左右 4 と上下 2、`"1,2,3,4"` なら左・上・右・下の順 |
| `Padding` | 部品の内側の余白 |
| `HorizontalAlignment` | 横の配置。`Left` / `Center` / `Right` / `Stretch`（広げる。既定値） |
| `VerticalAlignment` | 縦の配置 |
| `MinWidth` / `MaxWidth` | 最小・最大の幅 |

`Width` と `Height` を直接指定するのは最小限にしましょう。固定サイズにすると、ウィンドウを広げても部品が広がらなくなります。レイアウトの仕組みの詳しい話は第 9 章にあります。

## エディタの枠を作る

ここまでの知識で、エディタの画面の枠を作ってみます。

### 上・中・下に分ける

画面は、上からメニュー、本体、ステータス バーの 3 つに分かれています。上と下を端に張り付けて、残りを本体にするので `DockPanel` が向いています。

```xml title="MainWindow.xaml"
<Window x:Class="Editor.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="MiniEngine Editor" Height="720" Width="1280"
        Background="#FF1E1E1E">
    <DockPanel>
        <Menu DockPanel.Dock="Top">
            <MenuItem Header="ファイル(_F)">
                <MenuItem Header="新規シーン(_N)" />
                <MenuItem Header="開く(_O)..." />
                <MenuItem Header="保存(_S)" />
                <Separator />
                <MenuItem Header="終了(_X)" />
            </MenuItem>
            <MenuItem Header="編集(_E)">
                <MenuItem Header="元に戻す(_U)" />
                <MenuItem Header="やり直し(_R)" />
            </MenuItem>
            <MenuItem Header="表示(_V)" />
        </Menu>

        <StatusBar DockPanel.Dock="Bottom">
            <StatusBarItem Content="準備完了" />
        </StatusBar>

        <Grid />   <!-- 残りの全部。次で中身を書く -->
    </DockPanel>
</Window>
```

`DockPanel.Dock="Top"` が、さっきの添付プロパティです。「私は上に張り付いてください」と親の `DockPanel` に伝えています。Dock を指定していない最後の子（ここでは `Grid`）が、残りの領域を埋めます。

メニューの `Header` に入っている `_F` は、アクセスキーの印です。`Alt + F` で「ファイル」が開き、画面では `F` に下線が付きます。色の `#FF1E1E1E` は `#AARRGGBB` の順（アルファ、赤、緑、青）で、これは暗い灰色です。

### 本体を左・中・右に分ける

上の `<Grid />` を、次のように書き換えます。

```xml
<Grid>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="240" MinWidth="120" />
        <ColumnDefinition Width="Auto" />
        <ColumnDefinition Width="*" MinWidth="200" />
        <ColumnDefinition Width="Auto" />
        <ColumnDefinition Width="300" MinWidth="160" />
    </Grid.ColumnDefinitions>

    <Border Grid.Column="0" Background="#FF252526">
        <TextBlock Text="シーン ツリー" Foreground="White" Margin="8" />
    </Border>

    <GridSplitter Grid.Column="1" Width="4" HorizontalAlignment="Stretch" Background="#FF3F3F46" />

    <Grid Grid.Column="2">
        <Grid.RowDefinitions>
            <RowDefinition Height="*" MinHeight="120" />
            <RowDefinition Height="Auto" />
            <RowDefinition Height="200" MinHeight="60" />
        </Grid.RowDefinitions>

        <Border Grid.Row="0" Background="Black">
            <TextBlock Text="3D ビューポート" Foreground="Gray" Margin="8" />
        </Border>

        <GridSplitter Grid.Row="1" Height="4" HorizontalAlignment="Stretch" Background="#FF3F3F46" />

        <TabControl Grid.Row="2">
            <TabItem Header="アセット"><TextBlock Text="アセット ブラウザ" Margin="8" /></TabItem>
            <TabItem Header="ログ"><TextBlock Text="ログ" Margin="8" /></TabItem>
        </TabControl>
    </Grid>

    <GridSplitter Grid.Column="3" Width="4" HorizontalAlignment="Stretch" Background="#FF3F3F46" />

    <Border Grid.Column="4" Background="#FF252526">
        <TextBlock Text="プロパティ" Foreground="White" Margin="8" />
    </Border>
</Grid>
```

実行すると、暗い 3 分割の画面が出て、仕切りをドラッグすると幅が変わります。

`GridSplitter` は、ドラッグで行や列の大きさを変えられる仕切りです。自分自身が 1 つの列（または行）を専有するように置くのがコツで、ここでは `Auto` の列を 1 本ずつ割り当てました。縦の仕切りには `Width`、横の仕切りには `Height` を指定します。

`TextBlock` は文字を表示するだけの部品、`TabControl` / `TabItem` はタブです。`Border` は枠を付けたり背景を塗ったりできる、一番シンプルな入れ物です。

## リソースとスタイルの触り

同じ色を何か所にも書くと、あとで直すのが大変です。1 か所に名前を付けて定義し、使うところで名前を呼びます。`App.xaml` の `<Application.Resources>` に書くと、アプリ全体で使えます。

```xml title="App.xaml"
<Application.Resources>
    <SolidColorBrush x:Key="PanelBrush" Color="#FF252526" />

    <Style TargetType="TextBlock">
        <Setter Property="Foreground" Value="#FFDDDDDD" />
    </Style>
</Application.Resources>
```

使う側はこうです。

```xml
<Border Background="{StaticResource PanelBrush}">
```

`x:Key` が付いたものは「名前で呼んだときだけ使われる」リソース、`Style` のように `x:Key` を付けずに `TargetType` だけを指定したものは「その型の部品すべてに自動で効く」スタイルになります。上の例だと、画面中の `TextBlock` の文字色がすべて薄い灰色になります。

リソースは、近い所から順に探されます。部品自身、親、さらに親、ウィンドウ、`App.xaml` の順です。近くに同じ名前があれば、そちらが勝ちます。

スタイルとテンプレートは奥が深いので、第 11 章でまとめて扱います。

## イベントを受け取る

ボタンやメニューを押したときの処理は、`Click` などのイベントにメソッドを結び付けて書けます。

```xml
<MenuItem Header="終了(_X)" Click="OnExit" />
```

```csharp
private void OnExit(object sender, RoutedEventArgs e)
{
    Close();
}
```

`sender` はイベントを起こした部品、`e` はイベントの詳細です。WPF のイベントは「ルーテッド イベント」といって、子から親へと伝わっていく性質があります（第 10 章で説明します）。

この書き方は手軽ですが、画面とロジックが同じクラスに混ざります。エディタのように大きくなるアプリでは、すぐ管理できなくなります。次の章では、処理をビューモデルに移して、データバインディングとコマンドで結び付ける方法を学びます。

## Visual Studio に助けてもらう

XAML は、書いて実行して確かめるのが遅くなりがちです。Visual Studio には、実行中の画面に XAML の変更をその場で反映する「XAML ホット リロード」や、実行中の画面の部品の木を見られる「ライブ ビジュアル ツリー」があります。使い方は第 7 章にまとめました。

## 動かしてみる

`F5` で実行して、次のあたりを確かめてください。

- 暗い画面に、メニュー、3 つのパネル、下のタブ、ステータス バーが出ている。
- 仕切りをドラッグすると幅や高さが変わり、`MinWidth` より狭くならない。
- ウィンドウを広げると、中央の `*` の列だけが伸びる。
- `Alt + F` で「ファイル」メニューが開く。

??? failure "デザイナーに「ビルドが必要です」と出る、部品が見えない"
    一度ビルドしてください。それでも直らなければ、XAML のタグの閉じ忘れや属性名のタイプミスを、エラー一覧で探します。

??? failure "`GridSplitter` が動かない"
    仕切り専用の行（または列）を割り当てていない可能性が高いです。`Grid.Column` が仕切り用の列になっているか、`Width`（横に動かすなら）か `Height`（縦に動かすなら）が 0 でないかを確かめます。

??? failure "`Window` の中に部品を 2 つ書いたらエラーになる"
    `Window` の中身は 1 つだけです。`Grid` や `DockPanel` で包んでください。

??? failure "色が思った色にならない、見えない"
    `#RRGGBB` ではなく `#AARRGGBB` です。先頭がアルファ値なので、`00` から始めると透明になります。

## 関連する章

この先の章で、XAML を掘り下げていきます。

- [第 7 章 Visual Studio で XAML を書くコツ](07-vs-tips.md)
- [第 8 章 コントロールとコンテンツ モデル](08-controls.md)
- [第 9 章 レイアウトの仕組み](09-layout.md)
- [第 10 章 依存関係プロパティ、添付プロパティ、ルーテッド イベント](10-dependency-properties.md)
- [第 11 章 スタイル、リソース、テンプレート、トリガー](11-style-template.md)

次の章では、実行中の画面を調べたり、XAML をその場で直したりする Visual Studio の機能を、先に紹介します。

[第 7 章 Visual Studio で XAML を書くコツ](07-vs-tips.md) へ進みます。

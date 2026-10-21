---
title: 第 6 章 WPF プロジェクトと XAML
tags:
  - C#連携
---

# 第 6 章 WPF プロジェクトと XAML

この章では第 1 章で作った `Editor` プロジェクトの<strong>中身を読み</strong>、XAML という言語で<strong>エディタの画面の骨組み</strong>（メニュー、左・中・右のパネル、下のパネル、ステータス バー）を作ります。この章の画面にはまだエンジンもデータも出てきません。<strong>「画面の枠」を XAML で組む感覚</strong>をつかむ章です。

## この章の考え方

WPF では画面を<strong>2 種類のファイル</strong>で作ります。

| ファイル | 書く言語 | 役割 |
| --- | --- | --- |
| `〜.xaml` | XAML（XML の仲間） | 画面の<strong>構造と見た目</strong>。どんな部品をどこに並べるか |
| `〜.xaml.cs` | C# | 画面の<strong>振る舞い</strong>（コードビハインド）。ボタンが押されたときの処理など |

この 2 つは <strong>1 つのクラスを 2 つのファイルに分けて書いている</strong>だけです。XAML に書いたタグはビルドのときに C# のコードに変換されます。XAML の `<Button />` は C# で言う `new Button()` です。画面の部品を C# のコードで 1 つずつ `new` して並べる代わりに見た目に近い形（XML）で書ける、というのが XAML の価値です。

この教材では最終的にコードビハインドをほとんど使わずビューモデル（第 7 章）に処理を書きます。それでもまず XAML とコードビハインドの関係を理解しておくことが、土台になります。

## この章のゴール

- WPF プロジェクトが作る各ファイルの役割を説明できる。
- XAML の<strong>要素、属性、名前空間、添付プロパティ</strong>を読める。
- `Grid`、`DockPanel`、`StackPanel`、`GridSplitter` で画面を分割できる。
- エディタの画面の骨組みを XAML で作れる。

## 手順 1：WPF プロジェクトの中身を読む

`Editor` プロジェクトを展開すると、次のファイルがあります。

```text
Editor\
  Editor.csproj         プロジェクトの設定
  App.xaml              アプリ全体の設定（リソース、起動時の動作）
  App.xaml.cs           App のコードビハインド
  MainWindow.xaml       最初に開く画面
  MainWindow.xaml.cs    MainWindow のコードビハインド
  AssemblyInfo.cs       テーマ関連の属性
  Dependencies\         参照しているライブラリ（.NET 本体など）
```

### Editor.csproj

プロジェクトをダブルクリック（またはプロジェクトを右クリック →「プロジェクト ファイルの編集」）すると、設定ファイルが開きます。

```xml
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

| 項目 | 意味 |
| --- | --- |
| `Sdk="Microsoft.NET.Sdk"` | この `.csproj` が.NET の標準的なビルド手順を使うこと。ソース ファイルはフォルダー内の `.cs` が<strong>自動で含まれる</strong>（C++ のように、ファイルを 1 つずつ列挙しなくてよい） |
| `OutputType` = `WinExe` | 画面を持つ EXE を作る（黒いコンソールが出ない）。コンソール アプリは `Exe`、ライブラリは `Library` |
| `TargetFramework` = `net8.0-windows` | .NET 8 で、Windows 専用の機能（WPF など）を使う |
| `Nullable` = `enable` | null 許容参照型を有効にする（第 5 章） |
| `ImplicitUsings` = `enable` | よく使う `using` を自動で入れる |
| `UseWPF` = `true` | WPF のライブラリを使う |

### App.xaml と App.xaml.cs

```xml
<Application x:Class="Editor.App"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             xmlns:local="clr-namespace:Editor"
             StartupUri="MainWindow.xaml">
    <Application.Resources>
    </Application.Resources>
</Application>
```

```csharp
namespace Editor;

public partial class App : Application
{
}
```

ここに XAML の読み方の基本が全部あります。

| 部分 | 意味 |
| --- | --- |
| `<Application … >` | `Application` というクラスの<strong>オブジェクトを作る</strong>。要素の名前はクラス名 |
| `x:Class="Editor.App"` | この XAML は `Editor.App` というクラスの一部。<strong>C# 側の `partial class App` と合体</strong>して 1 つのクラスになる |
| `partial class` | 1 つのクラスを複数のファイルに分けて書く仕組み。XAML から自動生成されるコードと自分で書くコードを分けるために使う |
| `xmlns="…presentation"` | 既定の名前空間。`Button` や `Grid` などの WPF の部品が、タグ名だけで書ける |
| `xmlns:x="…xaml"` | `x:` で始まる XAML 自体の機能（`x:Class`、`x:Name`、`x:Key` など） |
| `xmlns:local="clr-namespace:Editor"` | 自分のプロジェクトの名前空間（`Editor`）を `local:` で参照できるようにする。C# の `using` に近い |
| `StartupUri="MainWindow.xaml"` | 起動時に開く画面。Prism を入れるとこの指定は使わない（第 8 章） |
| `<Application.Resources>` | アプリ全体で共有する<strong>リソース</strong>（色、スタイル、テンプレート）を置く場所 |

### MainWindow.xaml

```xml
<Window x:Class="Editor.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="MainWindow" Height="450" Width="800">
    <Grid>
    </Grid>
</Window>
```

```csharp
namespace Editor;

public partial class MainWindow : Window
{
    public MainWindow()
    {
        InitializeComponent();
    }
}
```

| 部分 | 意味 |
| --- | --- |
| `<Window>` | ウィンドウ。属性（`Title`、`Height`、`Width`）は `Window` の<strong>プロパティ</strong>を設定している。C# なら `window.Title = "MainWindow";` |
| `<Grid>` | `Window` の中身（`Content`）。`Window` は子を<strong>1 つだけ</strong>持てるので、複数の部品を置くときは `Grid` などの入れ物を 1 つ置きその中に並べる |
| `InitializeComponent()` | <strong>XAML で書いた内容から、部品を作って組み立てる</strong>関数。XAML から自動生成されコンストラクターの最初で呼ぶ |
| `: Window` | `MainWindow` は `Window` を継承する |

## 手順 2：XAML の文法

### 要素とプロパティ

```xml
<Button Content="押す" Width="80" Height="24" />
```

これは C# で書くと次と同じです。

```csharp
var button = new Button { Content = "押す", Width = 80, Height = 24 };
```

| XAML | C# |
| --- | --- |
| 要素 `<Button>` | `new Button()` |
| 属性 `Width="80"` | `button.Width = 80;`（文字列 `"80"` が、プロパティの型に自動変換される） |
| 子要素 `<Grid><Button/></Grid>` | `grid.Children.Add(button);` または `Content` への代入 |
| 要素の閉じ `/>` | 子がない場合の短い書き方 |

### プロパティ要素構文

属性では書きにくい複雑な値は <strong>`要素名.プロパティ名`</strong> という子要素で書きます。

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

`Button.Content` が `Button` の `Content` プロパティを「子要素の形で」設定しています。多くの部品は <strong>既定の子要素のプロパティ</strong>（`ContentProperty`）が決まっていて、`<Button>押す</Button>` のようにプロパティ名を省略して書けます。

### 添付プロパティ

```xml
<Grid>
    <Button Grid.Row="1" Grid.Column="2" Content="OK" />
</Grid>
```

`Grid.Row` は `Button` のプロパティではなく、<strong>`Grid` が定義して子に付けるプロパティ</strong>です。これを<strong>添付プロパティ</strong>と呼びます。「この部品は親の `Grid` の 1 行目・2 列目に置いてください」という親への指示を、子の側に書く仕組みです。C++ には直接対応するものがありません。

### x:Name（名前を付ける）

```xml
<TextBlock x:Name="StatusText" Text="準備完了" />
```

`x:Name` を付けるとコードビハインドから `StatusText.Text = "…";` のようにこの部品を C# の変数として使えます。ただし、この教材ではできるだけ使いません（データ バインディングで代わりにする。第 7 章）。

### 特別な値の書き方（マークアップ拡張）

```xml
<TextBlock Text="{Binding Name}" />
<Button Background="{StaticResource AccentBrush}" />
```

`{ … }` で囲んだ値は <strong>マークアップ拡張</strong>と呼ばれ「文字列ではなく、特別な処理をした結果の値」を表します。主なものは次のとおりです。

| マークアップ拡張 | 意味 |
| --- | --- |
| `{Binding パス}` | データ バインディング。データのプロパティを画面に結びつける（第 7 章） |
| `{StaticResource キー}` | リソースを起動時に一度だけ引いて使う |
| `{DynamicResource キー}` | リソースが変わったら、追従する（テーマ切り替えで使う） |
| `{x:Static 型.メンバー}` | `static` なメンバーを参照する |
| `{x:Null}` | `null` |

## 手順 3：レイアウトの部品

WPF のレイアウトは <strong>パネル</strong>（子を並べる入れ物）で決まります。ピクセル座標で置くのではなく、<strong>「縦に並べる」「右端に寄せる」「余った分を埋める」</strong>のように指示します。ウィンドウの大きさが変わっても、きれいに並び続けるためです。

| パネル | 並べ方 | 使いどころ |
| --- | --- | --- |
| `Grid` | 行と列の表に置く | 画面全体の分割。<strong>最もよく使う</strong> |
| `StackPanel` | 縦、または横に一列に並べる | ボタンの列、入力欄の列 |
| `DockPanel` | 上下左右に張り付け最後の子が残りを埋める | メニュー バー、ツール バー、ステータス バーと本体 |
| `WrapPanel` | 横に並べあふれたら折り返す | タグの一覧、サムネイル |
| `Canvas` | 座標（`Canvas.Left`、`Canvas.Top`）で置く | 図形、ノード エディタなど。通常は使わない |
| `Border` | 1 つの子を枠で囲む | 枠線、背景、余白 |
| `ScrollViewer` | 子が大きいときにスクロールさせる | 長いプロパティの一覧 |

### Grid の行と列

```xml
<Grid>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="200" />   <!-- 固定 200 -->
        <ColumnDefinition Width="*" />     <!-- 余りを分け合う -->
        <ColumnDefinition Width="Auto" />  <!-- 中身の大きさ -->
    </Grid.ColumnDefinitions>
    <Grid.RowDefinitions>
        <RowDefinition Height="Auto" />
        <RowDefinition Height="*" />
    </Grid.RowDefinitions>

    <TextBlock Grid.Row="0" Grid.Column="0" Text="左上" />
    <Button    Grid.Row="1" Grid.Column="1" Content="中央" />
</Grid>
```

| 幅・高さの指定 | 意味 |
| --- | --- |
| `100`（数字） | 固定のピクセル（正確には、デバイス非依存単位。96 分の 1 インチ） |
| `Auto` | 中身に必要な大きさ |
| `*`（スター） | 余った領域を比率で分ける。`*` と `2*` なら 1 : 2 |

### マージン、余白、配置

| プロパティ | 意味 |
| --- | --- |
| `Margin="4"` / `Margin="4,2"` / `Margin="1,2,3,4"` | 部品の<strong>外側</strong>の余白。1 つの値は上下左右、2 つは左右・上下、4 つは左・上・右・下の順 |
| `Padding` | 部品の<strong>内側</strong>の余白 |
| `HorizontalAlignment` | 横方向の配置。`Left`、`Center`、`Right`、`Stretch`（既定。広げる） |
| `VerticalAlignment` | 縦方向の配置 |
| `Width` / `Height` | 固定の大きさ（普通は、指定しない） |
| `MinWidth` / `MaxWidth` | 最小・最大の大きさ |

## 手順 4：エディタの骨組みを作る

`MainWindow.xaml` を次のように書き換えます。

### 全体の分割

エディタの画面は上から<strong>メニュー、本体、ステータス バー</strong>に分かれます。これには `DockPanel` を使います。

```xml
<Window x:Class="Editor.MainWindow"
        xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
        xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
        Title="MiniEngine Editor" Height="720" Width="1280"
        Background="#FF1E1E1E">
    <DockPanel>
        <!-- 上：メニュー -->
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

        <!-- 下：ステータス バー -->
        <StatusBar DockPanel.Dock="Bottom">
            <StatusBarItem Content="準備完了" />
        </StatusBar>

        <!-- 残り：本体（次の手順で書く） -->
        <Grid />
    </DockPanel>
</Window>
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DockPanel.Dock="Top"` | 添付プロパティ。この子を `DockPanel` の上端に張り付ける。`Bottom`、`Left`、`Right` もある。<strong>`Dock` を指定しない最後の子</strong>が、残りを全部埋める |
| `Menu` / `MenuItem` | メニュー バーとその項目。`Header` が表示文字。入れ子にするとサブメニューになる |
| `_F` | 文字の前の `_` は <strong>アクセスキー</strong>。`Alt + F` でその項目を開ける。`_` は表示では下線になる |
| `Separator` | メニューの区切り線 |
| `StatusBar` / `StatusBarItem` | 画面下端の状態表示 |
| `Background="#FF1E1E1E"` | 色の指定。`#AARRGGBB`（アルファ、赤、緑、青）の 16 進。ここでは暗い灰色 |

### 本体を左・中・右に分ける

`<Grid />` の部分を次のように書き換えます。

```xml
<Grid>
    <Grid.ColumnDefinitions>
        <ColumnDefinition Width="240" MinWidth="120" />
        <ColumnDefinition Width="Auto" />
        <ColumnDefinition Width="*" MinWidth="200" />
        <ColumnDefinition Width="Auto" />
        <ColumnDefinition Width="300" MinWidth="160" />
    </Grid.ColumnDefinitions>

    <!-- 左：シーン ツリー -->
    <Border Grid.Column="0" Background="#FF252526">
        <TextBlock Text="シーン ツリー" Foreground="White" Margin="8" />
    </Border>

    <GridSplitter Grid.Column="1" Width="4" HorizontalAlignment="Stretch" Background="#FF3F3F46" />

    <!-- 中央：ビューポートと下のパネル -->
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
            <TabItem Header="アセット">
                <TextBlock Text="アセット ブラウザ" Margin="8" />
            </TabItem>
            <TabItem Header="ログ">
                <TextBlock Text="ログ" Margin="8" />
            </TabItem>
        </TabControl>
    </Grid>

    <GridSplitter Grid.Column="3" Width="4" HorizontalAlignment="Stretch" Background="#FF3F3F46" />

    <!-- 右：プロパティ -->
    <Border Grid.Column="4" Background="#FF252526">
        <TextBlock Text="プロパティ" Foreground="White" Margin="8" />
    </Border>
</Grid>
```

実行（`F5`）すると 3 つに分かれた暗い画面が出ます。仕切り（`GridSplitter`）をドラッグすると、幅が変わります。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `GridSplitter` | `Grid` の行や列をドラッグで変えられるようにする仕切り。<strong>自分自身が 1 つの行（または列）を占める</strong>ように置く。縦の仕切りは `Width` を横の仕切りは `Height` を指定し、`HorizontalAlignment="Stretch"` にする |
| `TextBlock` | 文字を表示するだけの部品（編集はできない）。`Text` が表示文字 |
| `Foreground` | 文字の色。`Background` は背景色 |
| `TabControl` / `TabItem` | タブの入れ物と 1 枚のタブ。`Header` がタブの見出し中身は子要素 |
| `Border` | 1 つの子を囲む。`Background`、`BorderBrush`（枠の色）、`BorderThickness`（枠の太さ）を持つ |
| `MinWidth` / `MinHeight` | 仕切りで縮めたときの下限 |

## 手順 5：リソースとスタイル

同じ色や見た目を何度も書くのは大変です。<strong>リソース</strong>として 1 か所に定義し、名前で呼び出します。

`App.xaml` の `<Application.Resources>` の中に書きます。

```xml
<Application.Resources>
    <SolidColorBrush x:Key="PanelBrush" Color="#FF252526" />
    <SolidColorBrush x:Key="SplitterBrush" Color="#FF3F3F46" />

    <Style TargetType="TextBlock">
        <Setter Property="Foreground" Value="#FFDDDDDD" />
    </Style>
</Application.Resources>
```

そして `MainWindow.xaml` の側で `{StaticResource PanelBrush}` と書きます。

```xml
<Border Grid.Column="0" Background="{StaticResource PanelBrush}">
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `SolidColorBrush` | 単色の塗り。`Background` などのプロパティは色ではなく<strong>ブラシ</strong>を受け取る |
| `x:Key` | リソースの名前。引くときに使う |
| `Style` | 見た目の設定のまとまり。`TargetType` を指定するとその型の<strong>すべての部品に</strong>、自動で適用される |
| `Setter` | スタイルの 1 項目。`Property`（プロパティ名）と `Value`（値） |
| リソースの探し方 | 部品 → 親 → … → ウィンドウ → `App.xaml` の順に探す。近い所の定義が勝つ |

!!! note "ダーク テーマにするには"
    WPF の標準の部品（`Button`、`TextBox` など）の見た目は白い背景に決まっています。エディタ全体を暗くするには各部品の<strong>テンプレート</strong>を作り直す必要があり大変です。この教材では最小限の色だけを付け本格的なテーマは、ライブラリ（`MaterialDesignInXamlToolkit` など）に任せる方法があることを知っておくにとどめます。

## 手順 6：コードビハインドで反応させる

XAML の部品は `Click` などの<strong>イベント</strong>に C# のメソッドを結びつけられます。

```xml
<MenuItem Header="終了(_X)" Click="OnExit" />
```

```csharp
private void OnExit(object sender, RoutedEventArgs e)
{
    Close();    // ウィンドウを閉じる
}
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Click="OnExit"` | `Click` イベントに `OnExit` メソッドを登録する。メソッドはコードビハインドに書く |
| `object sender` | イベントを起こした部品（ここでは `MenuItem`） |
| `RoutedEventArgs e` | イベントの詳細。<strong>ルーテッド イベント</strong>の情報を持つ |
| ルーテッド イベント | WPF のイベントは、子から親へ<strong>伝わっていく</strong>（バブリング）。例えば、ボタンの `Click` はボタンを含む親でも受け取れる |
| `Close()` | ウィンドウを閉じる。`Window` のメソッド |

ただし、この方式は画面とロジックが同じクラスに混ざります。エディタが大きくなると管理できません。<strong>次の章ではロジックをビューモデルに分けデータ バインディングと `ICommand` で結びつける方法</strong>を学びます。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| 起動 | 暗い画面にメニュー、3 つのパネル、下のタブ、ステータス バーが出る |
| 仕切りのドラッグ | 左右・上下の仕切りを動かすと幅や高さが変わる。`MinWidth` より狭くならない |
| ウィンドウを広げる・縮める | 中央の領域だけが伸び縮みする（`*` の列） |
| `Alt + F` | 「ファイル」メニューが開く |
| 「終了」 | ウィンドウが閉じる |

## よくあるミス

??? failure "XAML のデザイナーに「ビルドが必要」と出る／部品が見えない"
    一度、ビルドする。それでも出ないときは XAML のタグの閉じ忘れ属性名のタイプミス（エラー一覧の `MC3000` など）を確認する。

??? failure "`GridSplitter` が動かない／見えない"
    `GridSplitter` が行や列を専用に占めていない。`Grid.Column` を仕切り用の列に指定しているか `Width`（または `Height`）が 0 でないかを確認する。

??? failure "`Window` に子を 2 つ書いて、エラーになる"
    `Window` の子は 1 つだけ。`Grid` や `DockPanel` などのパネルで包む。

??? failure "XAML の変更が、実行中の画面に反映されない"
    停止してもう一度ビルドして実行する。「ライブ ビジュアル ツリー」の機能を使うと実行中の画面を調べられる。

??? failure "色が思った色にならない"
    `#RRGGBB` ではなく `#AARRGGBB`（先頭がアルファ）の形式になっているか確認する。アルファが `00` だと透明になる。

## この章で作ったもの

- メニュー、左・中・右のパネル、下のタブ、ステータス バーの画面の骨組み。
- `App.xaml` のリソース（ブラシとスタイル）。

## 次の章へ

次の章（[第 7 章 データ バインディングと MVVM](07-binding-mvvm.md)）では、画面の部品とデータを<strong>つなぐ</strong>仕組みを学びます。ボタンを押したときの処理をコードビハインドから、ビューモデルに移します。

---
title: 第 11 章 スタイル、リソース、テンプレート、トリガー
tags:
  - C#連携
---

# 第 11 章 スタイル、リソース、テンプレート、トリガー

エディタの見た目を整える段階になると、「この色を全部のボタンに付けたい」「マウスを乗せたら色を変えたい」「ボタンを丸くしたい」といった要望が出てきます。WPF では、これを `Style`、`Trigger`、`ControlTemplate`、リソースの組み合わせで実現します。名前が似ているものが多くて最初は混乱しやすいので、この章では「どの道具がどこまでできるか」を中心に整理します。

!!! info "このページを読む前に"
    - [第 10 章 依存関係プロパティ、添付プロパティ、ルーテッド イベント](10-dependency-properties.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Themes/Dark.xaml`（新規） | 用途の名前を付けた、暗い配色の色の一覧 |
    | `App.xaml`（変更） | 色の辞書を読み込む |

    リソースやスタイル、トリガー、`ControlTemplate` の説明に出てくる、ほかのコードは、仕組みを見るための例で、Editor には入れません。

## 道具の使い分け

先に結論を書いておきます。

| やりたいこと | 使うもの |
| --- | --- |
| 色やフォントなどのプロパティ値をまとめて設定したい | `Style` + `Setter` |
| 状況（マウスが乗った、無効になった、データが特定の値）で見た目を変えたい | `Trigger`（`Style.Triggers` の中） |
| 部品の「作り」自体を変えたい（丸いボタン、枠を無くすなど） | `ControlTemplate` |
| データ 1 件の見せ方を決めたい | `DataTemplate`（第 14 章） |
| 同じ見た目と動きを部品として使い回したい | `UserControl`（第 27 章） |
| 色やスタイルを画面をまたいで共有したい | リソース（`ResourceDictionary`） |

プロパティ値を変えるだけで済むなら `Style`、部品の中身そのものを作り替えたいなら `ControlTemplate`、という切り分けが目安です。

## リソース

### 置き場所と探し方

リソースは、部品の `Resources` プロパティに定義します。ウィンドウの `Window.Resources` や、アプリ全体の `Application.Resources`（`App.xaml`）がよく使われます。呼ぶときは `{StaticResource キー}` です。

```xml title="例（Editor には入れない）"
<Window.Resources>
    <SolidColorBrush x:Key="AccentBrush" Color="#FF3498DB" />
</Window.Resources>

<Button Background="{StaticResource AccentBrush}" />
```

探されるのは、その部品自身の `Resources`、親の `Resources`、さらに親、ウィンドウ、`App.xaml` の順です。近いところに同じキーがあれば、そちらが使われます。

### StaticResource と DynamicResource

どちらもリソースを呼ぶ書き方ですが、時期が違います。

| | 読み込まれる時期 | あとでリソースが入れ替わったら |
| --- | --- | --- |
| `StaticResource` | XAML を読み込むとき、1 回だけ | 追従しない |
| `DynamicResource` | 使われるたびに探す | 追従する |

テーマの切り替え（ライト / ダーク）のように、実行中にリソースを差し替えたいものは `DynamicResource`、そうでないものは軽い `StaticResource` にします。注意点として、`StaticResource` は、参照するリソースが「より上の行」で定義されていなければ見つかりません。同じファイルの中でも、定義が使うより後ろにあるとエラーになります。

### 別ファイルに切り出す（ResourceDictionary）

リソースが増えてくると、`App.xaml` が長くなります。別ファイルに分けて、`MergedDictionaries` で取り込みます。

```xml title="例：Themes/Colors.xaml"
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <SolidColorBrush x:Key="PanelBrush" Color="#FF252526" />
    <SolidColorBrush x:Key="AccentBrush" Color="#FF3498DB" />
</ResourceDictionary>
```

```xml title="例：App.xaml（辞書を分けるときの形。Editor では次の Dark.xaml を使う）"
<Application.Resources>
    <ResourceDictionary>
        <ResourceDictionary.MergedDictionaries>
            <ResourceDictionary Source="Themes/Colors.xaml" />
            <ResourceDictionary Source="Themes/Controls.xaml" />
        </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
</Application.Resources>
```

第 12 章で `App` を `PrismApplication` に作り替えると、このタグは `prism:PrismApplication.Resources` に変わりますが、中身の書き方は同じです。

プロジェクトの設定（フォント、テーマ、ボタンの大きさなど）は、画面を増やす前の最初の段階で決めてしまうのがおすすめです。後からスタイルを入れると、すでに画面ごとに設定されたプロパティ値と衝突して、調整に手間がかかります。

## スタイル

スタイルは、プロパティ値の設定の束です。

```xml title="例（Editor には入れない）"
<Style x:Key="PrimaryButton" TargetType="Button">
    <Setter Property="Background" Value="{StaticResource AccentBrush}" />
    <Setter Property="Foreground" Value="White" />
    <Setter Property="Padding" Value="12,4" />
</Style>
```

使い方は 2 通りあります。

- `x:Key` を付けたスタイルは、`Style="{StaticResource PrimaryButton}"` と書いた部品だけに効きます。
- `x:Key` を付けず `TargetType` だけにしたスタイルは、その型のすべての部品に自動で効きます（暗黙のスタイル）。

既存のスタイルに少し足したいときは `BasedOn` です。

```xml title="例（Editor には入れない）"
<Style x:Key="DangerButton" TargetType="Button" BasedOn="{StaticResource PrimaryButton}">
    <Setter Property="Background" Value="#FFE74C3C" />
</Style>
```

テーマ ライブラリ（後述）と組み合わせるときは、自作の暗黙スタイルに `BasedOn="{StaticResource {x:Type Button}}"` を付けて、ライブラリのスタイルを受け継がないと、ライブラリの見た目が消えてしまいます。

## トリガー

「マウスが乗ったら色を変える」のような、状況に応じた見た目の変化は、トリガーで書きます。

```xml title="例（Editor には入れない）"
<Style TargetType="Button">
    <Setter Property="Background" Value="#FF3F3F46" />
    <Style.Triggers>
        <Trigger Property="IsMouseOver" Value="True">
            <Setter Property="Background" Value="#FF505058" />
        </Trigger>
        <Trigger Property="IsEnabled" Value="False">
            <Setter Property="Opacity" Value="0.4" />
        </Trigger>
    </Style.Triggers>
</Style>
```

| 種類 | 何をきっかけにするか |
| --- | --- |
| `Trigger` | 部品自身のプロパティの値（`IsMouseOver`、`IsEnabled` など） |
| `DataTrigger` | バインディングしたデータの値（第 41 章で `IsEditing` に使った） |
| `MultiTrigger` / `MultiDataTrigger` | 複数の条件がすべて満たされたとき |
| `EventTrigger` | イベントが起きたとき。アニメーションを開始するのに使う |

トリガーが終わる（条件が外れる）と、`Setter` の値は自動で元に戻ります。条件が外れたときの後始末を書く必要がありません。

## コントロール テンプレート

ここまでは、プロパティ値を変える話でした。ボタンの見た目そのもの（角丸、枠、押したときの動き）を変えるには、`ControlTemplate` で部品の作り自体を書き換えます。

WPF の `Button` の見た目は、実は `Button` の `Template` プロパティに入っている `ControlTemplate` で決まっています。これを差し替えると、機能（クリックされると `Click` が起きる）はそのままに、見た目だけを入れ替えられます。

```xml title="例（Editor には入れない）"
<Style x:Key="RoundButton" TargetType="Button">
    <Setter Property="Background" Value="#FF3498DB" />
    <Setter Property="Foreground" Value="White" />
    <Setter Property="Template">
        <Setter.Value>
            <ControlTemplate TargetType="Button">
                <Border x:Name="Root"
                        Background="{TemplateBinding Background}"
                        CornerRadius="12"
                        Padding="{TemplateBinding Padding}">
                    <ContentPresenter HorizontalAlignment="Center" VerticalAlignment="Center" />
                </Border>
                <ControlTemplate.Triggers>
                    <Trigger Property="IsMouseOver" Value="True">
                        <Setter TargetName="Root" Property="Opacity" Value="0.85" />
                    </Trigger>
                    <Trigger Property="IsPressed" Value="True">
                        <Setter TargetName="Root" Property="Opacity" Value="0.7" />
                    </Trigger>
                </ControlTemplate.Triggers>
            </ControlTemplate>
        </Setter.Value>
    </Setter>
</Style>
```

出てくる部品を順に説明します。

- `ContentPresenter` は、ボタンの `Content`（中身の文字や画像）を表示する場所です。テンプレートに必ず 1 つ置かないと、ボタンの中身が消えてしまいます。
- `TemplateBinding` は、テンプレートを適用された部品（この場合は `Button`）のプロパティをテンプレートの中の部品に結び付ける書き方です。`Background="{TemplateBinding Background}"` は、「ボタンの `Background` をこの `Border` の背景にする」の意味です。使う側が `Background` を指定できるようになります。
- `x:Name="Root"` と `TargetName="Root"` で、テンプレートの中の特定の部品にトリガーが効くようにしています。

### スタイルのトリガーが効かないとき

初心者がいちばんハマる落とし穴です。

> `Style` に `IsMouseOver` のトリガーを書いて、背景を変えようとしたのに、マウスを乗せても色が変わらない。

原因は、標準の `Button` テンプレートの中にすでに「マウスが乗ったら色を変える」トリガーが入っているからです。テンプレート内部のトリガーはスタイルのトリガーより強く、スタイルでは上書きできません。

対処は 2 つです。

1. 自分でテンプレートを書き直して、トリガーも自分で書く（上の例のとおり）。
2. 標準のテンプレートをコピーして、必要な所だけ直す。Visual Studio のデザイナーで部品を右クリックして、「テンプレートの編集 → コピーして編集」を選ぶと、標準のテンプレートの全文がリソースとして取り出されます。

標準のテンプレートは長いですが、読んでみると勉強になります。

### VisualStateManager

状態ごとの見た目の変化をトリガーの代わりに `VisualStateManager`（VSM）で書く方法もあります。状態に名前（`MouseOver`、`Pressed`、`Disabled` など）が付いていて、状態から状態への切り替えにアニメーションを付けやすいのが特徴です。WinUI や UWP ではこちらが標準ですが、WPF では、トリガーのほうがよく使われています。

## どれを選ぶか迷ったら

| こんなとき | 選ぶもの |
| --- | --- |
| 全部のボタンの色と余白をそろえたい | 暗黙の `Style` |
| 特別なボタンだけ色を変えたい | キー付きの `Style`（+ `BasedOn`） |
| ボタンを丸くしたい、枠をなくしたい | `ControlTemplate` |
| 「保存ボタン + ステータス表示」のように、複数の部品をひとまとめにしたい | `UserControl` |
| リストの 1 行の見せ方を変えたい | `DataTemplate` |

## 暗い配色を自分で作る

エディタは、暗い配色にしたくなります。ライブラリを入れる前に自分で作れる範囲を知っておきましょう。考え方は、色の置き場所を 1 か所に集めることです。

まず、色に「用途の名前」を付けて、`ResourceDictionary` に書きます。「灰色」ではなく「パネルの背景」のように、役目で名前を付けるのがコツです。

```xml title="Themes/Dark.xaml（新規）"
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <SolidColorBrush x:Key="Window.Background" Color="#FF1E1E1E" />
    <SolidColorBrush x:Key="Panel.Background"  Color="#FF252526" />
    <SolidColorBrush x:Key="Panel.Border"      Color="#FF3F3F46" />
    <SolidColorBrush x:Key="Text.Primary"      Color="#FFDDDDDD" />
    <SolidColorBrush x:Key="Text.Secondary"    Color="#FF9A9A9A" />
    <SolidColorBrush x:Key="Accent"            Color="#FF3794FF" />
</ResourceDictionary>
```

同じキーで、明るい配色の `Themes/Light.xaml` も作ります。キーがそろっていれば、中身の色だけを入れ替えられます。

`App.xaml` で、片方を読み込みます。

```xml title="App.xaml（変更）"
<Application.Resources>
    <ResourceDictionary>
        <ResourceDictionary.MergedDictionaries>
            <ResourceDictionary Source="Themes/Dark.xaml" />
        </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
</Application.Resources>
```

画面側では、色を直接書かずに、名前で呼びます。入れ替えに追従させるので、`StaticResource` ではなく `DynamicResource` です。

```xml title="例（Editor には入れない）"
<Border Background="{DynamicResource Panel.Background}"
        BorderBrush="{DynamicResource Panel.Border}" BorderThickness="1">
    <TextBlock Text="プロパティ" Foreground="{DynamicResource Text.Primary}" />
</Border>
```

実行中に切り替えるときは、読み込み済みの辞書を差し替えます。

```csharp title="例（Editor には入れない）"
public static void ApplyTheme(string name)   // "Dark" または "Light"
{
    var dictionaries = Application.Current.Resources.MergedDictionaries;
    dictionaries.Clear();
    dictionaries.Add(new ResourceDictionary { Source = new Uri($"Themes/{name}.xaml", UriKind.Relative) });
}
```

`DynamicResource` を使っている部品は、辞書が変わると、自動で新しい色を取り直します。

ここまでで色は一括で変えられますが、これで WPF の標準の部品がすべて暗くなるわけではありません。`TextBlock` や自作のパネルは名前付きの色で塗れます。ところが、`Button`、`ComboBox`、`TabControl` のような標準の部品は、`ControlTemplate` の中に色が書き込まれていて、リソースの色を変えても見た目が変わりません。`SystemColors`（`SystemColors.ControlBrushKey` など）を上書きすると、`ListBox` の選択色や `Menu` のように反応する部品もありますが、全部ではありません。

選択肢は 3 つあります。

| 方法 | 手間 | 向いている場合 |
| --- | --- | --- |
| 次の節のテーマ ライブラリを使う | 小さい | ほぼ全部の標準部品が最初から暗くなる |
| 使う部品だけ `ControlTemplate` を書き直す | 大きい | 使う部品が少なく、見た目を完全に決めたい |
| .NET 9 以降で、標準の Fluent テーマ（`ThemeMode`）を使う | 小さい | ライブラリを足さずに済む。.NET 9 以降が必要 |

この教材のエディタは、第 6 章で書いた枠のように、色を名前付きのリソースで管理しておき、標準の部品の見た目はテーマに任せる形をおすすめします。導入の手順は、第 13 章で書きます。

## アイコンを Path で描く（Geometry と Freezable）

ツール バーの再生ボタンや、ツリーの矢印のようなアイコンは、画像ファイルではなく、`Path` で描くと便利です。拡大しても粗くならず、`Fill` を `DynamicResource` にすれば、テーマの色に追従します。

図形は、`Geometry`（形の定義）として、リソースに置きます。

```xml title="例（Editor には入れない）"
<Geometry x:Key="Icon.Play">M 4,2 L 14,8 L 4,14 Z</Geometry>
<Geometry x:Key="Icon.Stop">M 3,3 L 13,3 L 13,13 L 3,13 Z</Geometry>
```

```xml title="例（Editor には入れない）"
<Button ToolTip="再生">
    <Path Data="{StaticResource Icon.Play}" Fill="{DynamicResource Accent}"
          Width="16" Height="16" Stretch="Uniform" />
</Button>
```

`Data` に書いている文字列は、パス ミニ言語といって、ペンの動かし方を命令で書きます。

| 命令 | 意味 |
| --- | --- |
| `M x,y` | ペンをその座標へ移動する（線は引かない） |
| `L x,y` | 現在の位置から、その座標まで線を引く |
| `H x` / `V y` | 横線、縦線 |
| `C x1,y1 x2,y2 x,y` | 3 次ベジェ曲線 |
| `A rx,ry 回転 大弧 向き x,y` | 円弧 |
| `Z` | 図形を閉じる |

小文字にすると、座標が現在位置からの相対値になります。アイコンのパスは、自分で書くより、SVG の `d` 属性の値を借りて作ることが多いです（この書き方は、SVG のパスとほぼ同じです）。

ここで出てきた `Geometry` や `SolidColorBrush` は、`Freezable` というクラスの仲間です。`Freezable` は「凍結（`Freeze()`）」できるオブジェクトで、凍結すると、変更できなくなる代わりに、変更の通知を管理する手間がなくなり、軽くなって、スレッドをまたいで使えるようにもなります。

```csharp title="例（Editor には入れない）"
var brush = new SolidColorBrush(Colors.Red);
brush.Freeze();                       // これ以降、brush.Color = ... は例外になる
```

XAML のリソースに置いたブラシは、変更しない前提なら、凍結しておくのがおすすめです。大量の部品が同じブラシを使うエディタでは、描画が少し軽くなります。

```xml title="例（Editor には入れない）"
<SolidColorBrush x:Key="Panel.Background" Color="#FF252526"
                 xmlns:po="http://schemas.microsoft.com/winfx/2006/xaml/presentation/options"
                 xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
                 mc:Ignorable="po" po:Freeze="True" />
```

ただし、凍結したブラシは、あとから `Color` を変えられません。`Accent` を実行中に書き換えるような使い方をするものは、凍結しないでください（辞書ごと差し替えるテーマの切り替えなら、問題ありません）。

## 見た目をまるごと変えるテーマ ライブラリ

WPF の標準の部品は、白を基調にした古い見た目です。標準の部品までダーク テーマにしたい、今風にしたい、という場合に全部の `ControlTemplate` を書き直すのは現実的ではありません。そこで、テーマを提供するライブラリが公開されています。

- WPF-UI、ModernWpf：Windows 11 風の見た目。
- MaterialDesignInXamlToolkit：Material Design 風。
- MahApps.Metro：Metro 風のウィンドウとコントロール。
- HandyControl：多くのコントロールが入った UI ライブラリ。

NuGet で入れて、`App.xaml` の `MergedDictionaries` に読み込みます。WPF-UI の入れ方と、.NET 9 以降の標準の Fluent テーマは、[第 13 章](13-theme.md)で手順を書きます。ほかのライブラリは、各ライブラリの README に導入手順が書かれています。使うときは、自作のスタイルの `BasedOn` を忘れないようにしてください。

また、日本語環境の表示崩れを避けるために、`FontFamily` は明示的に指定しておくのがおすすめです。OS によって標準のフォントが違うので、`Meiryo UI` や `Yu Gothic UI` を `Window` のスタイルで指定します。

```xml title="例（Editor には入れない）"
<Style TargetType="Window">
    <Setter Property="FontFamily" Value="Yu Gothic UI" />
</Style>
```

## C++ で考えると

リソース辞書は、アセット ストアのようなものです。名前（`x:Key`）で色やブラシを登録しておいて、必要な場所から名前で引きます。`StaticResource` は読み込み時に 1 回だけ引く、定数に近い参照です。`DynamicResource` は、引く先が差し替わったら追いかける参照で、このあとの「暗い配色を自分で作る」のような、テーマの切り替えに使います。

??? failure "`Style` を書いたのに、見た目が変わらない"
    原因はたいてい次の 3 つです。1 つ目は、`x:Key` を付けたスタイルを、部品側で `Style="{StaticResource 名前}"` と指定していないことです。`x:Key` 付きは、指定した部品にしか効きません。2 つ目は、部品の属性に直接書いた値が、スタイルより優先されることです。スタイルで `Background` を決めても、部品側に `Background="Red"` があれば、そちらが勝ちます。3 つ目は、暗黙のスタイルが、`TargetType` と完全に同じ型にしか効かないことです。`Button` 用のスタイルは、`Button` を継承した自作の部品には効きません。

## この章のまとめ

- プロパティ値の束は `Style`、状況での変化は `Trigger`、部品の作り替えは `ControlTemplate`。
- リソースは近い所から探される。画面をまたぐものは `ResourceDictionary` に切り出して `MergedDictionaries`。
- スタイルのトリガーが効かないときは、標準テンプレート内のトリガーが原因。「コピーして編集」でテンプレートを取り出す。
- 色は用途の名前を付けて `ResourceDictionary` に集め、`DynamicResource` で使うと、実行中にテーマを切り替えられる。
- アイコンは `Path` と `Geometry` で描く。変えないブラシは `Freeze()` する。
- 標準の部品まで見た目を大きく変えたいなら、テーマ ライブラリを使う。

次の章では、画面の部品とデータを結び付けるデータバインディングと、画面とロジックを分ける MVVM を学びます。

[第 14 章 データバインディングと MVVM](14-binding-mvvm.md) へ進みます。

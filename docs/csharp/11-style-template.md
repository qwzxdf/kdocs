---
title: 第 11 章 スタイル、リソース、テンプレート、トリガー
tags:
  - C#連携
---

# 第 11 章 スタイル、リソース、テンプレート、トリガー

エディタの見た目を整える段階になると、「この色を全部のボタンに付けたい」「マウスを乗せたら色を変えたい」「ボタンを丸くしたい」といった要望が出てきます。WPF では、これを `Style`、`Trigger`、`ControlTemplate`、リソースの組み合わせで実現します。名前が似ているものが多くて最初は混乱しやすいので、この章では「どの道具がどこまでできるか」を中心に整理します。

## 道具の使い分け

先に結論を書いておきます。

| やりたいこと | 使うもの |
| --- | --- |
| 色やフォントなどのプロパティ値を、まとめて設定したい | `Style` + `Setter` |
| 状況（マウスが乗った、無効になった、データが特定の値）で見た目を変えたい | `Trigger`（`Style.Triggers` の中） |
| 部品の「作り」自体を変えたい（丸いボタン、枠を無くすなど） | `ControlTemplate` |
| データ 1 件の見せ方を決めたい | `DataTemplate`（第 12 章） |
| 同じ見た目と動きを、部品として使い回したい | `UserControl`（第 21 章） |
| 色やスタイルを、画面をまたいで共有したい | リソース（`ResourceDictionary`） |

プロパティ値を変えるだけで済むなら `Style`、部品の中身そのものを作り替えたいなら `ControlTemplate`、という切り分けが目安です。

## リソース

### 置き場所と探し方

リソースは、部品の `Resources` プロパティに定義します。ウィンドウの `Window.Resources` や、アプリ全体の `Application.Resources`（`App.xaml`）がよく使われます。呼ぶときは `{StaticResource キー}` です。

```xml
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

```xml title="Themes/Colors.xaml"
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
    <SolidColorBrush x:Key="PanelBrush" Color="#FF252526" />
    <SolidColorBrush x:Key="AccentBrush" Color="#FF3498DB" />
</ResourceDictionary>
```

```xml title="App.xaml"
<prism:PrismApplication.Resources>
    <ResourceDictionary>
        <ResourceDictionary.MergedDictionaries>
            <ResourceDictionary Source="Themes/Colors.xaml" />
            <ResourceDictionary Source="Themes/Controls.xaml" />
        </ResourceDictionary.MergedDictionaries>
    </ResourceDictionary>
</prism:PrismApplication.Resources>
```

プロジェクトの設定（フォント、テーマ、ボタンの大きさなど）は、画面を増やす前の最初の段階で決めてしまうのがおすすめです。後からスタイルを入れると、すでに画面ごとに設定されたプロパティ値と衝突して、調整に手間がかかります。

## スタイル

スタイルは、プロパティ値の設定の束です。

```xml
<Style x:Key="PrimaryButton" TargetType="Button">
    <Setter Property="Background" Value="{StaticResource AccentBrush}" />
    <Setter Property="Foreground" Value="White" />
    <Setter Property="Padding" Value="12,4" />
</Style>
```

使い方は 2 通りあります。

- `x:Key` を付けたスタイルは、`Style="{StaticResource PrimaryButton}"` と書いた部品だけに効きます。
- `x:Key` を付けず `TargetType` だけにしたスタイルは、その型のすべての部品に、自動で効きます（暗黙のスタイル）。

既存のスタイルに少し足したいときは `BasedOn` です。

```xml
<Style x:Key="DangerButton" TargetType="Button" BasedOn="{StaticResource PrimaryButton}">
    <Setter Property="Background" Value="#FFE74C3C" />
</Style>
```

テーマ ライブラリ（後述）と組み合わせるときは、自作の暗黙スタイルに `BasedOn="{StaticResource {x:Type Button}}"` を付けて、ライブラリのスタイルを受け継がないと、ライブラリの見た目が消えてしまいます。

## トリガー

「マウスが乗ったら色を変える」のような、状況に応じた見た目の変化は、トリガーで書きます。

```xml
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
| `DataTrigger` | バインディングしたデータの値（第 35 章で `IsEditing` に使った） |
| `MultiTrigger` / `MultiDataTrigger` | 複数の条件がすべて満たされたとき |
| `EventTrigger` | イベントが起きたとき。アニメーションを開始するのに使う |

トリガーが終わる（条件が外れる）と、`Setter` の値は自動で元に戻ります。条件が外れたときの後始末を書く必要がありません。

## コントロール テンプレート

ここまでは、プロパティ値を変える話でした。ボタンの見た目そのもの（角丸、枠、押したときの動き）を変えるには、`ControlTemplate` で部品の作り自体を書き換えます。

WPF の `Button` の見た目は、実は `Button` の `Template` プロパティに入っている `ControlTemplate` で決まっています。これを差し替えると、機能（クリックされると `Click` が起きる）はそのままに、見た目だけを入れ替えられます。

```xml
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
- `TemplateBinding` は、テンプレートを適用された部品（この場合は `Button`）のプロパティを、テンプレートの中の部品に結び付ける書き方です。`Background="{TemplateBinding Background}"` は、「ボタンの `Background` をこの `Border` の背景にする」の意味です。使う側が `Background` を指定できるようになります。
- `x:Name="Root"` と `TargetName="Root"` で、テンプレートの中の特定の部品に、トリガーが効くようにしています。

### スタイルのトリガーが効かないとき

初心者がいちばんハマる落とし穴です。

> `Style` に `IsMouseOver` のトリガーを書いて、背景を変えようとしたのに、マウスを乗せても色が変わらない。

原因は、標準の `Button` テンプレートの中に、すでに「マウスが乗ったら色を変える」トリガーが入っているからです。テンプレート内部のトリガーはスタイルのトリガーより強く、スタイルでは上書きできません。

対処は 2 つです。

1. 自分でテンプレートを書き直して、トリガーも自分で書く（上の例のとおり）。
2. 標準のテンプレートをコピーして、必要な所だけ直す。Visual Studio のデザイナーで部品を右クリックして、「テンプレートの編集 → コピーして編集」を選ぶと、標準のテンプレートの全文が、リソースとして取り出されます。

標準のテンプレートは長いですが、読んでみると勉強になります。

### VisualStateManager

状態ごとの見た目の変化を、トリガーの代わりに `VisualStateManager`（VSM）で書く方法もあります。状態に名前（`MouseOver`、`Pressed`、`Disabled` など）が付いていて、状態から状態への切り替えにアニメーションを付けやすいのが特徴です。WinUI や UWP ではこちらが標準ですが、WPF では、トリガーのほうがよく使われています。

## どれを選ぶか迷ったら

| こんなとき | 選ぶもの |
| --- | --- |
| 全部のボタンの色と余白をそろえたい | 暗黙の `Style` |
| 特別なボタンだけ色を変えたい | キー付きの `Style`（+ `BasedOn`） |
| ボタンを丸くしたい、枠をなくしたい | `ControlTemplate` |
| 「保存ボタン + ステータス表示」のように、複数の部品をひとまとめにしたい | `UserControl` |
| リストの 1 行の見せ方を変えたい | `DataTemplate` |

## 見た目をまるごと変えるテーマ ライブラリ

WPF の標準の部品は、白を基調にした古い見た目です。ダーク テーマにしたい、今風にしたい、という場合は、全部の部品の `ControlTemplate` を書き直すことになり、現実的ではありません。そのために、テーマを提供するライブラリが公開されています。

- WPF-UI、ModernWpf：Windows 11 風の見た目。
- MaterialDesignInXamlToolkit：Material Design 風。
- MahApps.Metro：Metro 風のウィンドウとコントロール。
- HandyControl：多くのコントロールが入った UI ライブラリ。

NuGet で入れて、`App.xaml` の `MergedDictionaries` に読み込みます。各ライブラリの README に、導入手順が書かれています。使うときは、自作のスタイルの `BasedOn` を忘れないようにしてください。

また、日本語環境の表示崩れを避けるために、`FontFamily` は明示的に指定しておくのがおすすめです。OS によって標準のフォントが違うので、`Meiryo UI` や `Yu Gothic UI` を、`Window` のスタイルで指定します。

```xml
<Style TargetType="Window">
    <Setter Property="FontFamily" Value="Yu Gothic UI" />
</Style>
```

## この章のまとめ

- プロパティ値の束は `Style`、状況での変化は `Trigger`、部品の作り替えは `ControlTemplate`。
- リソースは近い所から探される。画面をまたぐものは `ResourceDictionary` に切り出して `MergedDictionaries`。
- スタイルのトリガーが効かないときは、標準テンプレート内のトリガーが原因。「コピーして編集」でテンプレートを取り出す。
- 見た目を大きく変えたいなら、テーマ ライブラリを使う。

次の章では、画面の部品とデータを結び付けるデータバインディングと、画面とロジックを分ける MVVM を学びます。

[第 12 章 データバインディングと MVVM](12-binding-mvvm.md) へ進みます。

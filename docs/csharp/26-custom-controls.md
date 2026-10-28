---
title: 第 26 章 UserControl とカスタム コントロール
tags:
  - C#連携
---

# 第 26 章 UserControl とカスタム コントロール

画面を作っていると、「同じ部品の組み合わせを何度も書いている」と気づく瞬間があります。たとえばプロパティ パネルの「ラベル + 数値入力 3 つ」は、位置にも回転にも拡大にも出てきます。こういうときは、ひとまとめにして名前を付けた部品にします。WPF では、そのために 2 つの方法があります。

!!! info "このページを読む前に"
    - [第 25 章 MVVM ライブラリを比べる](25-mvvm-libraries.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## どちらを選ぶか

| | UserControl | カスタム コントロール（Control を継承） |
| --- | --- | --- |
| 作り方 | XAML で、既存の部品を組み合わせる | C# のクラス + 見た目を `ControlTemplate` で別に書く |
| 手軽さ | 簡単。普通の画面と同じ感覚 | 手間がかかる |
| 見た目の差し替え | 難しい（中身が固定） | 使う側がテンプレートを差し替えられる |
| 向いている場面 | アプリの中で使い回す部品 | ライブラリとして配る部品、見た目を何通りにも変えたい部品 |

アプリの中でしか使わない部品なら、`UserControl` でほとんど足ります。この教材の `SceneTreeView` などのビューも、実は `UserControl` です。カスタム コントロールは、ボタンやスライダーのように、機能はそのままで見た目を何度も作り替えたい部品に向いています。

## UserControl で、数値入力の部品を作る

「ラベル + 数値入力」の部品 `LabeledNumber` を作ります。

1. `Controls` フォルダーを作り、「追加 → 新しい項目 → ユーザー コントロール (WPF)」で `LabeledNumber.xaml` を作ります。

```xml title="Controls/LabeledNumber.xaml"
<UserControl x:Class="Editor.Controls.LabeledNumber"
             xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
             xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
             x:Name="Root">
    <Grid>
        <Grid.ColumnDefinitions>
            <ColumnDefinition Width="72" />
            <ColumnDefinition Width="*" />
        </Grid.ColumnDefinitions>
        <TextBlock Grid.Column="0" Text="{Binding Label, ElementName=Root}" VerticalAlignment="Center" />
        <TextBox Grid.Column="1"
                 Text="{Binding Value, ElementName=Root, StringFormat=F3, UpdateSourceTrigger=LostFocus}" />
    </Grid>
</UserControl>
```

2. 外から指定できるプロパティを依存関係プロパティとして公開します（第 10 章）。

```csharp title="Controls/LabeledNumber.xaml.cs"
namespace Editor.Controls;

public partial class LabeledNumber : UserControl
{
    public static readonly DependencyProperty LabelProperty =
        DependencyProperty.Register(nameof(Label), typeof(string), typeof(LabeledNumber), new PropertyMetadata(""));

    public static readonly DependencyProperty ValueProperty =
        DependencyProperty.Register(nameof(Value), typeof(double), typeof(LabeledNumber),
            new FrameworkPropertyMetadata(0.0, FrameworkPropertyMetadataOptions.BindsTwoWayByDefault));

    public string Label { get => (string)GetValue(LabelProperty); set => SetValue(LabelProperty, value); }
    public double Value { get => (double)GetValue(ValueProperty); set => SetValue(ValueProperty, value); }

    public LabeledNumber()
    {
        InitializeComponent();
    }
}
```

3. 使う側は、普通の部品のように書きます。

```xml
<controls:LabeledNumber Label="位置 X" Value="{Binding PositionX}" />
```

ここで注意してほしいのが、`UserControl` 内部の `DataContext` です。部品の中で `{Binding Value}` と書くと、使う側から引き継いだ `DataContext`（たとえば親のビューモデル）の `Value` を探しに行ってしまいます。そこで、ここでは `ElementName=Root` で、部品自身の `Value` プロパティを指しました。

もう 1 つの方法は、部品の `DataContext` を部品自身にすることですが、そうすると、使う側が `Value="{Binding PositionX}"` と書いたときの `PositionX` の探し先も変わってしまい、親のビューモデルが見えなくなります。`UserControl` を作るときの典型的なハマりどころなので、`ElementName` か `RelativeSource` で自分自身を指す書き方を覚えておいてください。

## カスタム コントロールを作る

テンプレートで見た目を差し替えられる部品を作るときは、`Control` を継承します。

1. 「追加 → 新しい項目 → カスタム コントロール (WPF)」を選ぶと、`.cs` ファイルと、`Themes\Generic.xaml` ができます。
2. `.cs` には、機能（プロパティとロジック）だけを書きます。

```csharp title="Controls/StepperBox.cs"
[TemplatePart(Name = "PART_Up", Type = typeof(ButtonBase))]
[TemplatePart(Name = "PART_Down", Type = typeof(ButtonBase))]
public class StepperBox : Control
{
    static StepperBox()
    {
        DefaultStyleKeyProperty.OverrideMetadata(typeof(StepperBox), new FrameworkPropertyMetadata(typeof(StepperBox)));
    }

    public static readonly DependencyProperty ValueProperty =
        DependencyProperty.Register(nameof(Value), typeof(int), typeof(StepperBox),
            new FrameworkPropertyMetadata(0, FrameworkPropertyMetadataOptions.BindsTwoWayByDefault));

    public int Value { get => (int)GetValue(ValueProperty); set => SetValue(ValueProperty, value); }

    public override void OnApplyTemplate()
    {
        base.OnApplyTemplate();
        if (GetTemplateChild("PART_Up") is ButtonBase up) up.Click += (_, _) => Value++;
        if (GetTemplateChild("PART_Down") is ButtonBase down) down.Click += (_, _) => Value--;
    }
}
```

3. 見た目は `Themes\Generic.xaml` の `ControlTemplate` に書きます。

```xml title="Themes/Generic.xaml"
<ResourceDictionary xmlns="http://schemas.microsoft.com/winfx/2006/xaml/presentation"
                    xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml"
                    xmlns:local="clr-namespace:Editor.Controls">
    <Style TargetType="local:StepperBox">
        <Setter Property="Template">
            <Setter.Value>
                <ControlTemplate TargetType="local:StepperBox">
                    <StackPanel Orientation="Horizontal">
                        <Button x:Name="PART_Down" Content="−" Width="24" />
                        <TextBlock Text="{TemplateBinding Value}" Width="40" TextAlignment="Center" VerticalAlignment="Center" />
                        <Button x:Name="PART_Up" Content="＋" Width="24" />
                    </StackPanel>
                </ControlTemplate>
            </Setter.Value>
        </Setter>
    </Style>
</ResourceDictionary>
```

ポイントは 4 つです。

- `DefaultStyleKeyProperty.OverrideMetadata(...)` が、「このクラスの既定のスタイル（と、その中のテンプレート）は `Generic.xaml` から探して」という指定です。これを忘れると、見た目が何も出ません。
- 機能（`Value` の増減）と見た目（`ControlTemplate`）が別ファイルに分かれています。使う側は、同じ `StepperBox` に対して、別のテンプレートを当てれば、別の見た目にできます。
- `PART_Up` のように `PART_` で始まる名前は、「テンプレートに必ずあってほしい部品」を示す慣習です。`[TemplatePart]` 属性でそれを宣言しておき、`OnApplyTemplate` で `GetTemplateChild` を使って取り出します。
- `TemplateBinding` で、部品のプロパティ（`Value`）をテンプレートの中の部品に結び付けています（第 11 章）。

`Themes\Generic.xaml` の置き場所は、**`Themes` フォルダーの直下**で、名前も `Generic.xaml` と決まっています。`AssemblyInfo.cs` に `[assembly: ThemeInfo(ResourceDictionaryLocation.None, ResourceDictionaryLocation.SourceAssembly)]` があることも確認してください（WPF のプロジェクト テンプレートで最初から入っています）。

## 部品の上に重ねて描く（Adorner）

部品の上に選択枠や、ドラッグ中の目印を重ねたいことがあります。`Adorner`（装飾）は、そのための仕組みです。レイアウトに影響せず、部品の上の「装飾レイヤー」に描かれるので、元の部品の大きさや並びを変えずに、枠や記号を足せます。

自分で作るときは、`Adorner` を継承して、`OnRender` で描きます。

```csharp title="Controls/SelectionAdorner.cs"
using System.Windows.Documents;
using System.Windows.Media;

namespace Editor.Controls;

// 部品の周りに、点線の枠を重ねる
public sealed class SelectionAdorner : Adorner
{
    private static readonly Pen s_pen = CreatePen();

    public SelectionAdorner(UIElement adornedElement) : base(adornedElement)
    {
        IsHitTestVisible = false;     // マウスの操作を下の部品に通す
    }

    protected override void OnRender(DrawingContext drawingContext)
    {
        // AdornedElement は、装飾される側の部品
        var rect = new Rect(AdornedElement.RenderSize);
        drawingContext.DrawRectangle(null, s_pen, rect);
    }

    private static Pen CreatePen()
    {
        var pen = new Pen(Brushes.DeepSkyBlue, 1) { DashStyle = DashStyles.Dash };
        pen.Freeze();
        return pen;
    }
}
```

付けるときは、部品がいる `AdornerLayer` を取って、`Add` します。

```csharp
var layer = AdornerLayer.GetAdornerLayer(targetElement);
var adorner = new SelectionAdorner(targetElement);
layer?.Add(adorner);

// 外すとき
layer?.Remove(adorner);
```

`GetAdornerLayer` は、部品がウィンドウに表示されたあとでないと、`null` を返すことがあります。`Loaded` のあとに呼んでください。

`Adorner` は、`Window` の中の部品に対してだけ働きます。`HwndHost` で埋め込んだ 3D ビューポートの上には、重ねられません（第 36 章。WPF とは別のウィンドウだからです）。ビューポートの上の選択枠やギズモは、WPF の `Adorner` ではなく、エンジン側で描きます（第 42 章）。`Adorner` は、シーン ツリーやアセット ブラウザのような、WPF の部品の上で使います。

## 作らないほうがいい場合

自作の部品を作る前に次の可能性を考えてみてください。

- 既存の部品の `Style` や `ControlTemplate` を変えれば、同じ見た目にならないか（第 11 章）。
- 既存の部品の `Content` に、他の部品を入れれば済まないか（第 8 章）。
- `DataTemplate` で、データ 1 件の見せ方を決めれば済まないか。

自作部品は、作るコストだけでなく、直すコストも抱えます。標準の部品で済む場合は、そちらを選ぶのが得です。

??? failure "自作の `NumberBox` の `Value` に `{Binding}` したのに、値が反映されない"
    `Value` を普通のプロパティ（`public double Value { get; set; }`）で書いていないか確かめてください。バインディングの対象にできるのは、依存関係プロパティだけです（第 10 章）。普通のプロパティだと、XAML 側で `Value="{Binding ...}"` と書いた時点で、実行時にバインディング エラーが出ます。

## この章のまとめ

- アプリの中で使い回すだけなら `UserControl`。外から指定する値は、依存関係プロパティで公開する。
- `UserControl` の中のバインディングは、`ElementName` などで自分自身を指す。`DataContext` を書き換えない。
- 見た目を差し替えたい部品は、`Control` を継承したカスタム コントロール。機能は C#、見た目は `Generic.xaml`。
- 部品の上に枠や目印を重ねたいときは `Adorner`。ただし `HwndHost` の上には重ねられない。
- 作る前にスタイルやテンプレートで済まないかを考える。

次の章では、イベントをコマンドに結んで、コードビハインドを減らす方法を見ます。

[第 27 章 コードビハインドを減らす（Behaviors）](27-behaviors.md) へ進みます。

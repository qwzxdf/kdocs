---
title: 第 10 章 依存関係プロパティ、添付プロパティ、ルーテッド イベント
tags:
  - C#連携
---

# 第 10 章 依存関係プロパティ、添付プロパティ、ルーテッド イベント

WPF の解説を読んでいると、「依存関係プロパティ」「添付プロパティ」「ルーテッド イベント」という言葉に必ず出会います。本編では、それぞれの使い方だけを知っていれば進めたので、詳しい説明は後回しにしていました。この章で、なぜそういう仕組みがあるのか、自分でも作れるようになるところまで説明します。

!!! info "このページを読む前に"
    - [第 9 章 レイアウトの仕組み](09-layout.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章での Editor"
    この章では、Editor にファイルを足しません。依存関係プロパティを自分で作る例（`NumberBox`）は、書き方を見るための実験です。Editor で実際に使う部品は、第 27 章の `LabeledNumber` で作ります。

## 依存関係プロパティ

### 普通のプロパティではだめなのか

第 5 章のプロパティは、フィールドに値を入れて読み書きするだけの仕組みでした。WPF の `Button.Width` や `TextBox.Text` も、見た目は同じプロパティです。けれど、次のようなことは普通のプロパティではできません。

- バインディングで `Text="{Binding Name}"` とつなぐ。
- スタイルで `Width` の値をまとめて設定する。
- トリガーで、マウスが乗ったときだけ `Background` を変える。
- 親の `FontSize` を子の部品が自動で受け継ぐ。
- アニメーションで値を滑らかに動かす。

これらは全部、「値がどこから決まるか」が複数あるために起きる問題です。`Width` の値は、直接書いたもの、スタイルのもの、トリガーが一時的に上書きしたもの、アニメーションの途中の値、バインディングの結果など、いくつもの候補の中から優先順位で決まります。この仕組みを担当するのが依存関係プロパティ（DependencyProperty）です。

名前の「依存」は、値が他の要素の状態に依存して決まる、というところから来ています。

### 普通のプロパティとの見分け方

WPF のクラスのプロパティのうち、画面に関係するもの（`Width`、`Text`、`Background`、`IsEnabled` など）のほとんどが依存関係プロパティです。バインディングの対象（ターゲット）になれるのは、依存関係プロパティだけです。反対に、バインディングの元（ソース）になるビューモデルのプロパティは、普通のプロパティで構いません（その代わり、`INotifyPropertyChanged` が要ります）。

### 自分で作る

自作のコントロール（第 27 章）には、バインディングやスタイルで操作できる値を依存関係プロパティとして公開したくなります。書き方は決まっています。

最初の引数の `nameof(Value)` は、`Value` という名前を文字列 `"Value"` に変える式です。文字列を直接書いてもいいのですが、プロパティの名前を後で変えたときに、文字列だけが取り残されます。`nameof` ならコンパイラーが名前を追いかけるので、変え忘れがコンパイル エラーになります。C++ でマクロの `#名前` で文字列にする書き方があるのに近いですが、`nameof` は名前が存在しないとエラーになる点が違います。

```csharp title="実験：NumberBox.xaml.cs（抜粋。Editor には入れない）"
public partial class NumberBox : UserControl
{
    public static readonly DependencyProperty ValueProperty =
        DependencyProperty.Register(
            nameof(Value),                 // プロパティの名前
            typeof(double),                // 型
            typeof(NumberBox),             // 持ち主のクラス
            new FrameworkPropertyMetadata(
                0.0,                       // 既定値
                FrameworkPropertyMetadataOptions.BindsTwoWayByDefault,
                OnValueChanged));          // 値が変わったときに呼ぶ関数

    public double Value
    {
        get => (double)GetValue(ValueProperty);
        set => SetValue(ValueProperty, value);
    }

    private static void OnValueChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        var box = (NumberBox)d;
        box.UpdateText();
    }
}
```

読み方のコツは、3 つの部品に分けて見ることです。

1. `ValueProperty` という `static readonly` のフィールドが「このプロパティの登録証」です。名前は「プロパティ名 + Property」と付ける慣習で、`Register` が返したものを保存します。
2. `Value` は、見かけ上の普通のプロパティです。`get` で `GetValue(ValueProperty)`、`set` で `SetValue(ValueProperty, value)` を呼びます。値は自分のフィールドではなく、WPF が持つ辞書のような場所に入ります。
3. `OnValueChanged` のような関数を登録しておくと、値が変わったときに呼ばれます（バインディング経由で変わった場合も）。

`FrameworkPropertyMetadataOptions` には、`AffectsMeasure`（値が変わるとレイアウトをやり直す）、`AffectsRender`（再描画する）、`BindsTwoWayByDefault`（バインディングが既定で双方向になる）、`Inherits`（子に継承される）などがあります。見た目に関わる値なら、該当するものを付けておくと、WPF が自動で再描画してくれます。

Visual Studio には `propdp` というコード スニペットがあります。`propdp` と打って `Tab` を 2 回押すと、上の雛形が出ます。

### 値の優先順位

同じプロパティに複数のところから値が来たときは、おおむね次の順で強い値が勝ちます。アニメーション、ローカル値（`Width="100"` と直接書いたもの）、テンプレートのトリガー、スタイルのトリガー、スタイルの Setter、継承された値、既定値、という並びです。

「スタイルで色を指定したのに、反映されない」といった問題のかなりの部分は、より強い値（ローカル値など）が別の所で設定されているせいです。

## 添付プロパティ

第 6 章で出てきた `Grid.Row` や `DockPanel.Dock` が、添付プロパティです。「持ち主のクラスではなく、他のクラスの部品に付けられるプロパティ」と考えてください。

```xml title="例（Editor には入れない）"
<Button Grid.Row="1" Grid.Column="2" />
```

`Button` に `Grid.Row` という値を付けていますが、`Button` クラスに `Row` はありません。`Grid` が「子に付けてもらうプロパティ」を定義していて、`Grid` は子の `Button` から値を読んで配置を決めます。

自作の添付プロパティは、`RegisterAttached` で作ります。

```csharp title="例（Editor には入れない）"
public static class Ui
{
    public static readonly DependencyProperty IsHighlightedProperty =
        DependencyProperty.RegisterAttached(
            "IsHighlighted", typeof(bool), typeof(Ui), new PropertyMetadata(false, OnChanged));

    public static bool GetIsHighlighted(DependencyObject obj) => (bool)obj.GetValue(IsHighlightedProperty);
    public static void SetIsHighlighted(DependencyObject obj, bool value) => obj.SetValue(IsHighlightedProperty, value);

    private static void OnChanged(DependencyObject d, DependencyPropertyChangedEventArgs e)
    {
        // d（付けられた部品）に対して何かする
    }
}
```

```xml title="例（Editor には入れない）"
<Border local:Ui.IsHighlighted="True" />
```

`Get...` と `Set...` の名前の付け方が決まりになっています（XAML が、この名前の関数を探すからです）。添付プロパティの使いどころは、部品の振る舞いを後から足したいときです。第 12 章の `ViewModelLocator.AutoWireViewModel` も、添付プロパティが `True` にされたら、その部品の `DataContext` を設定する、という仕組みでできています。

## ルーテッド イベント

普通の C# のイベントは、起きた場所で、登録した人にだけ知らせます。WPF のイベントの多くは、ルーテッド イベントといって、部品の木をたどって伝わっていきます。

```xml title="例（Editor には入れない）"
<StackPanel Button.Click="OnAnyButtonClick">
    <Button Content="A" />
    <Button Content="B" />
</StackPanel>
```

この `StackPanel` は、中の `Button` が押されるたびに、`OnAnyButtonClick` を呼びます。ボタン 1 つ 1 つにハンドラーを付けなくても、親でまとめて受けられます。

伝わり方は 3 種類です。

| 方式 | 向き | 例 |
| --- | --- | --- |
| バブル | 起きた部品 → 親 → さらに親へ（上へ） | `Click`、`MouseDown`、`KeyDown` |
| トンネル | いちばん上の親 → 子 → 起きた部品へ（下へ） | `PreviewMouseDown`、`PreviewKeyDown` |
| ダイレクト | 起きた部品だけ | `MouseEnter` |

入力系のイベントは、`Preview` 付き（トンネル）と付かない方（バブル）がペアになっています。トンネルが先に、親から順に呼ばれ、続いてバブルが呼ばれます。「親が先に見て、止めたければ止められる」のがトンネルです。

ハンドラーの引数 `e`（`RoutedEventArgs`）のうち、よく使うのは次の 3 つです。

| メンバー | 意味 |
| --- | --- |
| `e.Handled` | `true` にすると、それ以上伝わらない |
| `e.Source` | イベントの発生元として扱われる部品（論理ツリー上） |
| `e.OriginalSource` | 実際に発生した部品（ビジュアル ツリー上）。たとえば、ボタンの中の `TextBlock` |

第 41 章のシーン ツリーの `PreviewMouseLeftButtonDown` は、まさにこのトンネルを使って、クリックされた場所の部品から `TreeViewItem` までをたどっています。

??? failure "イベント ハンドラーが呼ばれない"
    子のどこかで `e.Handled = true` にされていないか確認してください。`Button` の `Click` は、`MouseLeftButtonDown` を受け取った時点で `Handled` にしてしまうので、ボタンの上の `MouseLeftButtonDown` を親で受けても呼ばれません。このときはトンネル（`PreviewMouseLeftButtonDown`）で受けます。

## C++ で考えると

普通のプロパティは、オブジェクトごとのフィールドに値を持ちます。WPF の部品は、見た目に関わるプロパティが数百あるので、全部をフィールドで持つと、1 つの `Button` が大きくなりすぎます。そこで依存関係プロパティは、プロパティの定義（名前、型、既定値）を `static` に 1 つだけ持ち、各オブジェクトには、既定値から変えられた値だけを記録します。ゲームで言うと、全オブジェクトが全項目を持つ代わりに、既定と違うものだけを持つ疎なデータ構造に近い作りです。バインディングやスタイルが値を書き込める理由も、値の出どころを覚えている、この仕組みにあります。

## この章のまとめ

- 画面に関する値は、依存関係プロパティ。バインディングやスタイル、トリガーの対象になれる。
- 自作するときは `Register` と `GetValue` / `SetValue` の決まった形で書く。
- 添付プロパティは、他のクラスの部品に付ける値。親が子へ指示を出すときや、振る舞いを後付けするときに使う。
- ルーテッド イベントは、木をたどって伝わる。親でまとめて受けられる。止めたければ `e.Handled`。

次の章では、見た目を整えるスタイル、リソース、テンプレート、トリガーを扱います。

[第 11 章 スタイル、リソース、テンプレート、トリガー](11-style-template.md) へ進みます。

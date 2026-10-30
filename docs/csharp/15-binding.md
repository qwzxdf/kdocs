---
title: 第 15 章 バインディングを掘り下げる
tags:
  - C#連携
---

# 第 15 章 バインディングを掘り下げる

第 14 章で、シーン ツリーとプロパティ パネルがつながりました。ただ、使い込むと不満が出てきます。リストの 1 行ごとに削除ボタンを付けたい。位置は「1.0, 0.0, 2.0」のようにまとめて見せたい。オブジェクトが増えたので、名前で絞り込みたい。名前を空にしたら、怒ってほしい。この章では、これらを Editor に足しながら、バインディングの細かい設定を順に見ていきます。

!!! info "このページを読む前に"
    - [第 14 章 データバインディングと MVVM](14-binding-mvvm.md)（前の章。この章は、そこで作った Editor に足していく）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Scene/SceneObjectViewModel.cs`（変更） | `Scale` を足す。名前が空ならエラーにする（`ObservableValidator`） |
    | `MainWindowViewModel.cs`（変更） | 削除コマンド、名前での絞り込み |
    | `MainWindow.xaml`（変更） | スケールのスライダー、位置の表示、削除ボタン、検索ボックス、ステータス バー |

## 表示を整える

### StringFormat：位置を読みやすく

シーン ツリーの各行には、第 14 章で `X: 1.0` のように X だけを出しました。X、Y、Z をまとめて出したいので、3 つの値から 1 つの文字列を作ります。これには `MultiBinding` を使います。

```xml title="MainWindow.xaml（変更：ListBox の ItemTemplate の中）"
<TextBlock Foreground="Gray" Margin="8,0,0,0">
    <TextBlock.Text>
        <MultiBinding StringFormat="({0:F1}, {1:F1}, {2:F1})">
            <Binding Path="X" />
            <Binding Path="Y" />
            <Binding Path="Z" />
        </MultiBinding>
    </TextBlock.Text>
</TextBlock>
```

オブジェクトの行が `Cube (1.0, 0.0, 2.0)` のように出ます。位置を書き換えると、フォーカスを外した時点で、リストの数字も変わります。

`{0}` が最初の `Binding` の値、`{1}` が 2 つ目、という並びです。書式の指定は C# の `ToString` と同じで、`F1` なら小数 1 桁、`yyyy/MM/dd` なら日付です。値が 1 つだけの普通のバインディングでも、同じように使えます。

```xml
<TextBlock Text="{Binding X, StringFormat=X: {0:F2}}" />
<TextBlock Text="{Binding X, StringFormat={}{0:F2} m}" />
```

書式文字列が `{` で始まる場合は、XAML が「マークアップ拡張だ」と誤解します。先頭に `{}` を付けて逃がします。

`StringFormat` だけで足りない計算が必要なときは、`IMultiValueConverter` を実装します。次の例は仕組みを見るためのもので、Editor には入れません。

```csharp title="実験：IMultiValueConverter の中身（Editor には入れない）"
public class SumConverter : IMultiValueConverter
{
    public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        => values.OfType<float>().Sum();

    public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
```

値を渡す `ConverterParameter` もあります。`Converter={StaticResource GreaterThan}, ConverterParameter=0` のように固定の値を渡せば、しきい値だけ違うコンバーターを何個も作らなくて済みます。

### ElementName：同じ画面の部品から読む

`SceneObjectViewModel` に、拡大率の `Scale` を足します。位置と同じ形（`[ObservableProperty]` を付けたフィールド）で、初期値は 1 です。

```csharp title="Scene/SceneObjectViewModel.cs（変更：フィールドとプロパティを足す）"
[ObservableProperty]
private float _scale = 1f;
```

プロパティ パネルに、スライダーを置きます。

```xml title="MainWindow.xaml（変更：右のパネルに足す）"
<TextBlock Text="スケール" Foreground="Gray" Margin="0,8,0,0" />
<Slider x:Name="ScaleSlider" Minimum="0.1" Maximum="10"
        Value="{Binding Selected.Scale}" />
<TextBlock Foreground="White"
           Text="{Binding Value, ElementName=ScaleSlider, StringFormat=F2}" />
```

スライダーを動かすと、下の数字が追従します。`Slider.Value` は、既定で双方向のバインディングなので、動かした値が `Scale` に書き戻され、`Scale` が変われば動きます。

`ElementName` は、`x:Name` を付けた部品を指して、その部品のプロパティを読みます。ビューモデルを通さず、画面の中だけで完結する連動に便利です。ここでは、下の数字を `Selected.Scale` から読んでも同じ結果になります。`ElementName` を使ったのは、スライダーを動かしている途中の値を、そのまま出したかったからです。

### FallbackValue と TargetNullValue：何も選んでいないとき

ウィンドウの下のステータス バーに、選択中のオブジェクトの名前を出します。第 6 章で、ここには「準備完了」と書いてありました。

```xml title="MainWindow.xaml（変更：StatusBar）"
<StatusBar DockPanel.Dock="Bottom">
    <StatusBarItem Content="準備完了" />
    <Separator />
    <StatusBarItem>
        <TextBlock Text="{Binding Selected.Name, TargetNullValue=(なし), FallbackValue=(なし)}" />
    </StatusBarItem>
</StatusBar>
```

| 設定 | 使われるとき |
| --- | --- |
| `TargetNullValue=(なし)` | 元の値が `null` のとき |
| `FallbackValue=(なし)` | バインディングが失敗したとき（パスが見つからない、途中が `null`、など） |

`Selected` が `null` のとき、`Selected.Name` は途中でたどれなくなります。この場合に使われるのが `FallbackValue` です。`Name` そのものが `null` のときは `TargetNullValue` が使われます。どちらも空白のまま放置せず、人が読める言葉に置き換えるための設定です。

## 別の場所のコマンドを呼ぶ

### RelativeSource：リストの中のボタンから、リストの外のコマンドを呼ぶ

シーン ツリーの各行に、削除ボタンを付けます。`MainWindowViewModel` に、削除のコマンドを足します。

引数を受け取るコマンドは、`[RelayCommand]` を付けたメソッドに引数を 1 つ書くだけで作れます。`ICommand` の `Execute` の引数は `object?` ですが、生成される `RelayCommand<T>` が `T` に取り出して渡してくれるので、受け取る関数は `T` で書けます。

```csharp title="MainWindowViewModel.cs（変更：コンストラクターとメソッドを足す）"
[RelayCommand]
private void Delete(SceneObjectViewModel obj)       // DeleteCommand が生成される
{
    Objects.Remove(obj);
    if (Selected == obj) Selected = null;
}
```

削除したオブジェクトが選ばれていたら、`Selected` を `null` にします。右のパネルが丸ごと消えるのは、第 14 章で作った `HasSelection` のおかげです。

ボタンを置くのは、`ListBox` の `ItemTemplate` の中です。ところが、そこの `DataContext` は、リストの 1 要素の `SceneObjectViewModel` になっています。`DeleteCommand` は、その外の `MainWindowViewModel` にあります。

```xml title="MainWindow.xaml（変更：ItemTemplate）"
<DataTemplate>
    <DockPanel LastChildFill="False">
        <Button DockPanel.Dock="Right" Content="×" Padding="6,0"
                Command="{Binding DataContext.DeleteCommand,
                          RelativeSource={RelativeSource AncestorType=ListBox}}"
                CommandParameter="{Binding}" />
        <TextBlock Text="{Binding Name}" FontWeight="Bold" />
        <!-- 位置の TextBlock は前のとおり -->
    </DockPanel>
</DataTemplate>
```

`RelativeSource={RelativeSource AncestorType=ListBox}` は、「上にたどって最初に見つかる `ListBox`」を指します。その `DataContext` は、`ListBox` に設定された `MainWindowViewModel` なので、`DataContext.DeleteCommand` で届きます。`CommandParameter="{Binding}"` は、何も書かない `{Binding}` で、その行の `DataContext`、つまりそのオブジェクト自身を渡します。

### 深掘り：RelativeSource とパスの書き方

`RelativeSource` で指せるものは、次のとおりです。

| 書き方 | 指すもの |
| --- | --- |
| `RelativeSource={RelativeSource Self}` | その部品自身 |
| `RelativeSource={RelativeSource AncestorType=Window}` | 上にたどって最初に見つかる `Window` |
| `RelativeSource={RelativeSource TemplatedParent}` | テンプレートを適用されている部品（`TemplateBinding` の正式形） |

`Path` には、ドットでたどる書き方やインデックスも使えます。

| 書き方 | 意味 |
| --- | --- |
| `{Binding Selected.Name}` | `Selected` プロパティの `Name` |
| `{Binding Objects[0]}` | 0 番目の要素 |
| `{Binding Scores[Alice]}` | 辞書の `"Alice"` キーの値 |
| `{Binding}` または `{Binding .}` | `DataContext` そのもの |

## 名前で絞り込む

オブジェクトが増えてくると、探すのが大変になります。シーン ツリーの上に検索ボックスを置いて、名前に文字を含むものだけを残します。

### UpdateSourceTrigger と Delay

検索ボックスは、1 文字打つたびに絞り込んでほしいので、入力のたびに反映します。

```xml title="MainWindow.xaml（変更：左のパネル）"
<DockPanel Grid.Column="0" Background="#FF252526">
    <TextBox DockPanel.Dock="Top" Margin="8"
             Text="{Binding FilterText, UpdateSourceTrigger=PropertyChanged, Delay=300}" />
    <Button DockPanel.Dock="Bottom" Content="オブジェクトを追加" Margin="8"
            Command="{Binding AddCommand}" />
    <ListBox ...>
```

`Delay=300` は、入力が止まってから 300 ミリ秒たったら反映する指定です。1 文字ごとに絞り込みを走らせると、オブジェクトが数千個になったとき、打つたびに画面が重くなります。入力が止まるまで少し待つ、というときに使います。

### CollectionView：元のリストを変えずに見せ方だけ変える

絞り込み自体は、`ObservableCollection` を書き換えずに行います。`ListBox` などに `ObservableCollection` を渡すと、WPF は裏で `CollectionView` というラッパーを作って、並べ替え、絞り込み、グループ化、「現在の項目」の管理をしています。この `CollectionView` を取り出して、条件を設定します。

```csharp title="MainWindowViewModel.cs（変更）"
using System.ComponentModel;
using System.Windows.Data;

private readonly ICollectionView _objectsView;

[ObservableProperty]
private string _filterText = "";

// コンストラクターの中、Objects を作ったあと
_objectsView = CollectionViewSource.GetDefaultView(Objects);
_objectsView.Filter = o => o is SceneObjectViewModel s
    && s.Name.Contains(FilterText, StringComparison.OrdinalIgnoreCase);

// FilterText が変わったときに呼ばれる（生成される partial メソッド）
partial void OnFilterTextChanged(string value) => _objectsView.Refresh();     // 条件が変わったので、かけ直す
```

`Filter` に、「この要素を残すか」を返す関数を渡します。条件が変わったら、`Refresh()` で、かけ直してもらいます。`ListBox` は `Objects` をそのまま受け取っていますが、裏でこの `CollectionView` を通して見ているので、絞り込みの結果だけが並びます。

`partial void OnFilterTextChanged(string value)` は、`[ObservableProperty]` が用意してくれる、「値が変わったあとに呼ばれる」フックです。`On` + プロパティ名 + `Changed` という名前で書くと、ジェネレーターがその呼び出しを、`FilterText` の `set` に組み込みます。`set` の中身を自分で書き足さなくても、変わったときの処理だけを別に書けます。フックには `Changing`（変わる前）の版もあります。

並べ替えやグループ化も、同じ `CollectionView` で設定します。Editor には入れませんが、書き方はこうです。

```csharp title="実験：並べ替えとグループ化（Editor には入れない）"
_objectsView.SortDescriptions.Add(new SortDescription("Name", ListSortDirection.Ascending));
_objectsView.GroupDescriptions.Add(new PropertyGroupDescription("Kind"));
```

### 深掘り：Mode と UpdateSourceTrigger の既定値

データが流れる向き（`Mode`）と、画面からデータへ書き戻すタイミング（`UpdateSourceTrigger`）は、何も書かなければ部品ごとの既定値になります。「更新されない」トラブルの多くは、この既定値を知らなかったことが原因です。

| `Mode` | データの流れ |
| --- | --- |
| `OneWay` | データ → 画面 |
| `TwoWay` | データ ⇄ 画面 |
| `OneTime` | 最初の 1 回だけデータ → 画面。あとで変わっても追従しない |
| `OneWayToSource` | 画面 → データ |
| `Default` | 部品ごとの既定値に従う |

`Default` のときは、入力を受け付けるプロパティ（`TextBox.Text`、`CheckBox.IsChecked`、`Slider.Value` など）が `TwoWay`、それ以外（`TextBlock.Text` など）が `OneWay` になります。`OneTime` は、起動時にだけ読めばよい値に使うと、通知の仕組みを使わないので軽くなります。ただし、あとから変えても画面が追従しないので、うっかり付けると「更新されない」の原因になります。

| `UpdateSourceTrigger` | 書き戻すタイミング |
| --- | --- |
| `PropertyChanged` | 画面の値が変わるたびにすぐ |
| `LostFocus` | その部品からフォーカスが外れたとき |
| `Explicit` | コードで `UpdateSource()` を呼んだとき |
| `Default` | 部品ごとの既定値。ほとんどは `PropertyChanged`、`TextBox.Text` だけ `LostFocus` |

初心者がつまずく定番は、`TextBox` だけ既定が `LostFocus` なことです。入力しても `Tab` や別の場所のクリックでフォーカスを外すまで、ビューモデルの値が変わりません。数値を入れる欄で `1.` と打った途中に `1` へ戻されてしまう現象も、`PropertyChanged` にしたときに起きがちです。第 14 章で位置の入力欄を既定のままにしたのは、そのためでした。

## 入力の検証

ユーザーが入れた値が不正なとき、赤い枠を出したり、メッセージを出したりする仕組みが、バインディングには組み込まれています。方法は 3 つあります。Editor には、名前を空にできないようにする規則を入れたいので、そのうち 1 つを選びます。

### 1. 例外で知らせる（簡易）

プロパティの `set` の中で、不正な値なら例外を投げます。バインディング側で `ValidatesOnExceptions=True` を付けると、例外が検証エラーとして扱われます。

```csharp title="実験：例外で知らせる（Editor には入れない）"
public string Name
{
    get => _name;
    set
    {
        if (string.IsNullOrWhiteSpace(value)) throw new ArgumentException("名前を入力してください");
        SetProperty(ref _name, value);
    }
}
```

```xml
<TextBox Text="{Binding Selected.Name, ValidatesOnExceptions=True}" />
```

手軽ですが、例外を日常的に投げるのは重く、デバッガーで毎回止まって煩わしいので、おすすめは次の 2 番です。

### 2. INotifyDataErrorInfo（おすすめ）

ビューモデルが `INotifyDataErrorInfo` を実装して、エラーを覚えておく方法です。非同期の検証（サーバーに確認する）や、1 つのプロパティに複数のエラーを持たせることもできます。

自分で実装すると、メンバーは 3 つです。エラーがあるかを返す `HasErrors`、プロパティごとのエラーを返す `GetErrors`、エラーが変わったことを知らせる `ErrorsChanged` です。`ErrorsChanged` の意味は `PropertyChanged` と同じで、これが起きたとき、WPF は `GetErrors` を呼び直して、入力欄の赤い枠を出したり消したりします。プロパティ名ごとにエラーを持ち、「消すときだけ通知する」「同じエラーを入れ直したときは通知しない」といった分岐も書く必要があるので、手で書くと長くなります。

CommunityToolkit.Mvvm の `ObservableValidator` は、これを実装済みの基底クラスです。検証の規則は、`System.ComponentModel.DataAnnotations` の属性（`[Required]` など）で書きます。

```csharp title="Scene/SceneObjectViewModel.cs（変更）"
using System.ComponentModel.DataAnnotations;
using CommunityToolkit.Mvvm.ComponentModel;

public partial class SceneObjectViewModel : ObservableValidator      // ObservableObject の代わり
{
    [ObservableProperty]
    [NotifyDataErrorInfo]                                  // 値が変わるたびに検証する
    [Required(ErrorMessage = "名前を入力してください")]      // 空、空白だけならエラー
    private string _name;

    // ほかは前のとおり
}
```

`ObservableValidator` は `ObservableObject` を継承しているので、これまでの `[ObservableProperty]` や `[RelayCommand]` は、そのまま使えます。基底クラスを差し替えるだけです。

`[NotifyDataErrorInfo]` は、「このプロパティの値が変わるたびに、下に並べた検証の属性で検証して、結果を `INotifyDataErrorInfo` に出して」という指示です。`[Required]` の `ErrorMessage` が、画面に出るメッセージになります。

名前の入力欄を全部消すと、入力欄が赤い枠になります。WPF の `Binding` は、`INotifyDataErrorInfo` のエラーを自動で拾ってくれます（`ValidatesOnNotifyDataErrors` の既定が `true`）。XAML は、これまでの `{Binding Selected.Name}` のままです。

エラーになった値も、プロパティには入ります。検証は「エラーを記録する」だけで、値の代入は止めません。エラーのまま保存してしまわないよう、保存の前に `HasErrors` を確かめてください。

`[Range(0.1, 10)]` や `[StringLength(32)]` のように、使える属性はほかにもあります。複雑な条件は、`[CustomValidation]` で自分のメソッドを指定するか、`SetProperty(ref _name, value, validate: true)` で手で検証を呼びます。

### 3. ValidationRule（XAML 側で完結）

規則を、画面の側のクラスに書く方法もあります。

```csharp title="実験：ValidationRule（Editor には入れない）"
public class RangeRule : ValidationRule
{
    public double Min { get; set; }
    public double Max { get; set; }

    public override ValidationResult Validate(object value, CultureInfo cultureInfo)
    {
        if (!double.TryParse((string)value, out var d)) return new ValidationResult(false, "数字を入れてください");
        return d >= Min && d <= Max ? ValidationResult.ValidResult : new ValidationResult(false, $"{Min}〜{Max} の範囲で入力してください");
    }
}
```

```xml
<TextBox>
    <TextBox.Text>
        <Binding Path="Selected.Scale" UpdateSourceTrigger="PropertyChanged">
            <Binding.ValidationRules>
                <local:RangeRule Min="0.1" Max="10" />
            </Binding.ValidationRules>
        </Binding>
    </TextBox.Text>
</TextBox>
```

XAML だけで完結するのが長所ですが、規則が画面に埋まるので、ビューモデルのテストには入りません。ビューモデルに規則を持たせるなら 2 番を選びます。

### 赤枠の見た目を変える

検証エラーのとき、既定では入力欄に赤い枠が出ますが、メッセージは出ません。メッセージも見せたいので、`Validation.ErrorTemplate` を差し替えたスタイルを作って、名前の入力欄に使います。

```xml title="MainWindow.xaml（変更：Window.Resources に足す）"
<Style x:Key="ValidatedTextBox" TargetType="TextBox"
       BasedOn="{StaticResource {x:Type TextBox}}">
    <Setter Property="Validation.ErrorTemplate">
        <Setter.Value>
            <ControlTemplate>
                <StackPanel>
                    <AdornedElementPlaceholder />
                    <TextBlock Foreground="#FFF48771"
                               Text="{Binding [0].ErrorContent}" />
                </StackPanel>
            </ControlTemplate>
        </Setter.Value>
    </Setter>
</Style>
```

```xml title="MainWindow.xaml（変更：名前の入力欄）"
<TextBox Style="{StaticResource ValidatedTextBox}"
         Text="{Binding Selected.Name, UpdateSourceTrigger=PropertyChanged}" />
```

`AdornedElementPlaceholder` は、元の入力欄が入る場所です。このテンプレートの中の `DataContext` は、エラーの一覧なので、`[0].ErrorContent` が先頭のエラーのメッセージになります。`Validation.HasError`（添付プロパティ）をスタイルのトリガーで見ると、エラーのときにツールチップを出す、といった表現もできます。

## 動かないときに調べる

バインディングは、失敗しても例外を出しません。次の順で調べてください。

1. Visual Studio の「出力」ウィンドウで、`System.Windows.Data Error` を探す。パスが見つからない、型が変換できない、などが書かれています。
2. Visual Studio 2026 では、実行中に「デバッグ → ウィンドウ → XAML バインディング エラー」（名前は版によって違います）で、一覧を見られます。
3. 調べたいバインディングに `PresentationTraceSources.TraceLevel=High` を付ける。
4. 「ライブ ビジュアル ツリー」と「ライブ プロパティ エクスプローラー」で、その部品の `DataContext` が何かを確かめる（第 7 章）。

```xml
xmlns:diag="clr-namespace:System.Diagnostics;assembly=WindowsBase"

<TextBlock Text="{Binding Selected.Name, diag:PresentationTraceSources.TraceLevel=High}" />
```

3 番を付けると、そのバインディングが「どこでどのオブジェクトを探して、何が見つかったか」を出力に詳しく書き出してくれます。うまくいかないバインディングの原因が分からないときの最後の手段です。

よくある原因の一覧です。

| 症状 | 原因 |
| --- | --- |
| 何も出ない | プロパティ名のつづり、`public` でない、フィールドになっている |
| 何も出ない | `DataContext` が `null`、または違うオブジェクト |
| 初期値は出るが、変えても追従しない | `INotifyPropertyChanged` の実装漏れ、通知の呼び忘れ |
| 画面で入力しても、データが変わらない | `Mode` が `OneWay`、または `UpdateSourceTrigger=LostFocus` のまま |
| `DataTemplate` の中で、親のプロパティが見つからない | `DataContext` がリストの 1 要素になっている。`RelativeSource` で祖先に回る |
| `ContextMenu` の中でバインディングが効かない | `ContextMenu` は別のウィンドウ扱い。`PlacementTarget` 経由で書く（第 41 章） |

### 実行しなくても確認する：デザイン時の DataContext

XAML エディタのデザイナーでも、バインディングのパスを補完してもらうには、デザイン時だけ有効な `d:DataContext` を書きます。`MainWindow.xaml` の `Window` タグに足します。

```xml title="MainWindow.xaml（変更：Window タグ）"
<Window ...
        xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
        xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
        xmlns:vm="clr-namespace:Editor"
        mc:Ignorable="d"
        d:DataContext="{d:DesignInstance Type=vm:MainWindowViewModel}">
```

`d:DesignInstance` を指定すると、Visual Studio は `MainWindowViewModel` のプロパティを知っているものとして、パスの入力補完を出します。つづり間違いを、実行前に減らせます。

### 深掘り：コードからバインディングを作る

XAML に書けないとき（部品をコードで作るときなど）は、コードでも作れます。Editor には入れません。

```csharp title="実験：コードでバインディング（Editor には入れない）"
var binding = new Binding("Name")
{
    Source = viewModel.Selected,
    Mode = BindingMode.TwoWay,
    UpdateSourceTrigger = UpdateSourceTrigger.PropertyChanged,
};
textBox.SetBinding(TextBox.TextProperty, binding);
```

`TextBox.TextProperty` は、依存関係プロパティの登録証です（第 10 章）。バインディングのターゲットは、このように依存関係プロパティでなければなりません。

## 動かして確かめる

`F5` で実行して、次を確かめてください。

- スライダーを動かすと、下の数字が追従する。別のオブジェクトを選ぶと、スライダーの位置が切り替わる。
- 左のリストに、`Cube (1.0, 0.0, 2.0)` のように位置が出る。
- 行の「×」で削除できる。選んでいる行を消すと、右のパネルが消える。
- ステータス バーに、選択中の名前が出る。何も選んでいないと `(なし)` と出る。
- 検索ボックスに `c` と打つと、`Camera` と `Cube` だけが残る。
- 名前を全部消すと赤い枠とメッセージが出る。

??? failure "削除ボタンを押しても、何も起きない"
    「出力」ウィンドウに `BindingExpression path error` が出ていないかを確かめます。`DataContext.DeleteCommand` の `DeleteCommand` が `public` のプロパティか、`RelativeSource` の `AncestorType` が `ListBox` かを見てください。

??? failure "検索ボックスに打っても、絞り込まれない"
    `Delay=300` のため、打ち終わって 0.3 秒たつまで反映されません。それでも変わらないときは、`partial void OnFilterTextChanged` で `_objectsView.Refresh()` を呼んでいるかを確かめます。

??? failure "名前を空にしても、赤い枠が出ない"
    `SceneObjectViewModel` の土台が `ObservableValidator` になっているか、`Name` のフィールドに `[NotifyDataErrorInfo]` と `[Required]` が付いているかを確かめます。`[NotifyDataErrorInfo]` を忘れると、値が変わっても検証が走りません。

## ここまでの Editor

```text
Editor/
├─ Scene/
│   └─ SceneObjectViewModel.cs       Scale、名前の検証（ObservableValidator）を足した
├─ MainWindowViewModel.cs            削除、絞り込みを足した
└─ MainWindow.xaml                   検索ボックス、削除ボタン、スライダー、ステータス バー
```

## この章のまとめ

- 部品の値は `ElementName`、祖先の `DataContext` は `RelativeSource` で読む。
- 見せ方は `StringFormat`、`MultiBinding`、`TargetNullValue`、`FallbackValue` で整える。
- 絞り込みや並べ替えは、`CollectionView` で見せ方だけを変える。
- 検証は `INotifyDataErrorInfo` に持たせるのが、いちばん素直。CommunityToolkit.Mvvm なら、`ObservableValidator` と `[Required]` などの属性で書ける。
- 動かないときは、まず「出力」ウィンドウを見る。

次の章では、リストやグリッドで大量のデータを見せる方法を扱います。

[第 16 章 リストとデータ表示](16-lists.md) へ進みます。

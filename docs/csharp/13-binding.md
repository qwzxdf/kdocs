---
title: 第 13 章 バインディングを掘り下げる
tags:
  - C#連携
---

# 第 13 章 バインディングを掘り下げる

第 12 章では、`{Binding プロパティ名}` の基本を説明しました。実際に画面を作り込んでいくと、「親のビューモデルのコマンドを、リストの中のボタンから呼びたい」「2 つの値を組み合わせて表示したい」「入力が不正なら赤く表示したい」といった場面が、必ず出てきます。この章では、そのあたりを一通りそろえます。

!!! info "このページを読む前に"
    - [第 12 章 データバインディングと MVVM](12-binding-mvvm.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## Mode と UpdateSourceTrigger の既定値

データが流れる向き（`Mode`）と、画面からデータへ書き戻すタイミング（`UpdateSourceTrigger`）は、何も書かなければ部品ごとの既定値になります。「更新されない」トラブルの多くは、この既定値を知らなかったことが原因です。

### Mode

| 値 | データの流れ |
| --- | --- |
| `OneWay` | データ → 画面 |
| `TwoWay` | データ ⇄ 画面 |
| `OneTime` | 最初の 1 回だけデータ → 画面。あとで変わっても追従しない |
| `OneWayToSource` | 画面 → データ |
| `Default` | 部品ごとの既定値に従う |

`Default` のときは、入力を受け付けるプロパティ（`TextBox.Text`、`CheckBox.IsChecked`、`Slider.Value` など）が `TwoWay`、それ以外（`TextBlock.Text` など）が `OneWay` になります。

`OneTime` は、起動時にだけ読めばよい値（変わらない設定値など）に使うと、通知の仕組みを使わないので軽くなります。ただし、後から変えても画面が追従しないので、うっかり付けると「更新されない」の原因になります。

### UpdateSourceTrigger

| 値 | 書き戻すタイミング |
| --- | --- |
| `PropertyChanged` | 画面の値が変わるたびにすぐ |
| `LostFocus` | その部品からフォーカスが外れたとき |
| `Explicit` | コードで `UpdateSource()` を呼んだとき |
| `Default` | 部品ごとの既定値。ほとんどは `PropertyChanged`、`TextBox.Text` だけ `LostFocus` |

初心者がつまずく定番は、`TextBox` だけ既定が `LostFocus` なことです。入力しても `Tab` や別の場所のクリックでフォーカスを外すまで、ビューモデルの値が変わりません。1 文字ごとに反映したいときは、`UpdateSourceTrigger=PropertyChanged` を付けます。

ただし、1 文字ごとに反映すると、重い処理（検索や再描画）を毎回起こすことになります。入力が止まるまで少し待ちたいときは、`Delay=300`（ミリ秒）を併用します。

```xml
<TextBox Text="{Binding FilterText, UpdateSourceTrigger=PropertyChanged, Delay=300}" />
```

数値を入れるときに、`1.` と打った途中で、`1` に戻されてしまう現象も、`PropertyChanged` にしたときに起きがちです。そういう入力欄は、`LostFocus`（既定）のままにしておくほうが扱いやすいです。

## どこからデータを取るか

`{Binding Name}` と書いたときの探し先は、`DataContext` でした。それ以外のところから取りたいときの書き方がいくつかあります。

### ElementName：同じ画面の別の部品から

```xml
<Slider x:Name="Volume" Minimum="0" Maximum="100" />
<TextBlock Text="{Binding Value, ElementName=Volume}" />
```

`x:Name` を付けた部品を指して、その部品のプロパティを読みます。スライダーを動かすと、横の文字が追従します。ビューモデルを通さず、画面の中だけで完結する連動に便利です。

### RelativeSource：自分や祖先を指す

```xml
<!-- 親の ListBox の DataContext にある DeleteCommand を、リストの中のボタンから呼ぶ -->
<Button Content="削除"
        Command="{Binding DataContext.DeleteCommand,
                  RelativeSource={RelativeSource AncestorType=ListBox}}"
        CommandParameter="{Binding}" />
```

`DataTemplate` の中は、`DataContext` がリストの 1 要素になっています。1 件ごとのボタンから、リスト全体を持っているビューモデルのコマンドを呼びたいときに、祖先の `ListBox` の `DataContext` へ回り込むのに使います。

| 書き方 | 指すもの |
| --- | --- |
| `RelativeSource={RelativeSource Self}` | その部品自身 |
| `RelativeSource={RelativeSource AncestorType=Window}` | 上にたどって最初に見つかる `Window` |
| `RelativeSource={RelativeSource TemplatedParent}` | テンプレートを適用されている部品（`TemplateBinding` の正式形） |

`CommandParameter="{Binding}"` と何も書かずに `{Binding}` だけにすると、`DataContext` そのもの（この場合はリストの 1 要素）を渡せます。

### パスの書き方

`Path` には、ドットでたどる書き方や、インデックスも使えます。

| 書き方 | 意味 |
| --- | --- |
| `{Binding Player.Name}` | `Player` プロパティの `Name` |
| `{Binding Items[0]}` | 0 番目の要素 |
| `{Binding Scores[Alice]}` | 辞書の `"Alice"` キーの値 |
| `{Binding}` または `{Binding .}` | `DataContext` そのもの |

## 表示を整える

### StringFormat

```xml
<TextBlock Text="{Binding Hp, StringFormat=HP: {0}}" />
<TextBlock Text="{Binding Position.X, StringFormat={}{0:F2} m}" />
```

`{0}` が値の入る場所です。書式の指定は C# の `ToString` と同じです（`F2` なら小数 2 桁、`yyyy/MM/dd` なら日付）。書式文字列が `{` で始まる場合は、XAML が「マークアップ拡張だ」と誤解するので、先頭に `{}` を付けて逃がします。

### FallbackValue と TargetNullValue

| 設定 | 使われるとき |
| --- | --- |
| `FallbackValue=---` | バインディングが失敗したとき（パスが見つからない、など） |
| `TargetNullValue=(なし)` | 元の値が `null` のとき |

選択が何もないときに、空白でなく「(なし)」と出したい、といった場面に便利です。

### MultiBinding：複数の値から 1 つの表示を作る

```xml
<TextBlock>
    <TextBlock.Text>
        <MultiBinding StringFormat="{}{0} ({1} 個)">
            <Binding Path="Name" />
            <Binding Path="Children.Count" />
        </MultiBinding>
    </TextBlock.Text>
</TextBlock>
```

複数の値をまとめるときは、`StringFormat` だけで足りることもあります。計算が必要なら、`IMultiValueConverter` を実装します。

```csharp
public class AddConverter : IMultiValueConverter
{
    public object Convert(object[] values, Type targetType, object parameter, CultureInfo culture)
        => values.OfType<double>().Sum();

    public object[] ConvertBack(object value, Type[] targetTypes, object parameter, CultureInfo culture)
        => throw new NotSupportedException();
}
```

### コンバーターに引数を渡す

```xml
<TextBlock Visibility="{Binding Count, Converter={StaticResource GreaterThan}, ConverterParameter=0}" />
```

`ConverterParameter` で、固定の値を渡せます。しきい値だけ違うコンバーターを何個も作らなくて済みます。

## コレクションの見せ方を変える（CollectionView）

`ListBox` などに `ObservableCollection` を渡すと、WPF は裏で `CollectionView` というラッパーを作って、並べ替え、絞り込み、グループ化、「現在の項目」の管理をしています。この `CollectionView` を取り出せば、元のコレクションを変えずに、見せ方だけを変えられます。

```csharp
var view = CollectionViewSource.GetDefaultView(Items);

view.Filter = o => o is Item i && i.Name.Contains(Keyword);          // 絞り込み
view.SortDescriptions.Add(new SortDescription("Name", ListSortDirection.Ascending));   // 並べ替え
view.GroupDescriptions.Add(new PropertyGroupDescription("Kind"));    // グループ化
```

絞り込みの条件を変えたら、`view.Refresh()` を呼んで、かけ直します（第 40 章の検索ボックスで使っています）。

## 入力の検証

ユーザーが入れた値が不正なとき、赤い枠を出したり、メッセージを出したりする仕組みが、バインディングには組み込まれています。方法は 3 つあります。

### 1. 例外で知らせる（簡易）

プロパティの `set` の中で、不正な値なら例外を投げます。バインディング側で `ValidatesOnExceptions=True` を付けると、例外が検証エラーとして扱われます。

```csharp
public int Hp
{
    get => _hp;
    set
    {
        if (value < 0) throw new ArgumentException("HP は 0 以上にしてください");
        SetProperty(ref _hp, value);
    }
}
```

```xml
<TextBox Text="{Binding Hp, ValidatesOnExceptions=True}" />
```

手軽ですが、例外を日常的に投げるのは重く、デバッガーで毎回止まって煩わしいので、おすすめは次の 2 つです。

### 2. INotifyDataErrorInfo（おすすめ）

ビューモデルが `INotifyDataErrorInfo` を実装して、エラーを覚えておきます。非同期の検証（サーバーに確認する）や、1 つのプロパティに複数のエラーを持たせることもできます。

```csharp
public class PlayerViewModel : BindableBase, INotifyDataErrorInfo
{
    private readonly Dictionary<string, List<string>> _errors = new();

    public bool HasErrors => _errors.Count > 0;
    public event EventHandler<DataErrorsChangedEventArgs>? ErrorsChanged;

    public IEnumerable GetErrors(string? propertyName)
        => propertyName != null && _errors.TryGetValue(propertyName, out var list) ? list : Enumerable.Empty<string>();

    private int _hp;
    public int Hp
    {
        get => _hp;
        set
        {
            if (SetProperty(ref _hp, value)) Validate(nameof(Hp), value >= 0, "HP は 0 以上にしてください");
        }
    }

    private void Validate(string property, bool ok, string message)
    {
        if (ok) _errors.Remove(property);
        else _errors[property] = new List<string> { message };
        ErrorsChanged?.Invoke(this, new DataErrorsChangedEventArgs(property));
    }
}
```

Prism の `BindableBase` には含まれていませんが、`ErrorsContainer<T>` という補助クラスがあります。また CommunityToolkit.Mvvm の `ObservableValidator` を使うと、`[Range(0, 100)]` のような属性（DataAnnotations）だけで検証を書けます（第 20 章）。

WPF の `Binding` は、`INotifyDataErrorInfo` のエラーを自動で拾ってくれます（`ValidatesOnNotifyDataErrors` の既定が `true`）。

### 3. ValidationRule（XAML 側で完結）

```csharp
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
        <Binding Path="Hp" UpdateSourceTrigger="PropertyChanged">
            <Binding.ValidationRules>
                <local:RangeRule Min="0" Max="100" />
            </Binding.ValidationRules>
        </Binding>
    </TextBox.Text>
</TextBox>
```

XAML だけで完結するのが長所ですが、規則が画面に埋まるので、ビューモデルのテストには入りません。ビューモデルに規則を持たせるなら 2 番を選びます。

### 赤枠の見た目を変える

検証エラーのとき、既定では入力欄に赤い枠が出ます。メッセージも見せたいなら、`Validation.ErrorTemplate` を差し替えます。

```xml
<TextBox Text="{Binding Hp, UpdateSourceTrigger=PropertyChanged}">
    <Validation.ErrorTemplate>
        <ControlTemplate>
            <StackPanel>
                <AdornedElementPlaceholder />
                <TextBlock Foreground="Red"
                           Text="{Binding [0].ErrorContent}" />
            </StackPanel>
        </ControlTemplate>
    </Validation.ErrorTemplate>
</TextBox>
```

`AdornedElementPlaceholder` は、元の入力欄が入る場所です。`Validation.HasError`（添付プロパティ）をスタイルのトリガーで見ると、エラーのときにツールチップを出す、といった表現もできます。

## 動かないときに調べる

バインディングは、失敗しても例外を出しません。次の順で調べてください。

1. Visual Studio の「出力」ウィンドウで、`System.Windows.Data Error` を探す。パスが見つからない、型が変換できない、などが書かれています。
2. Visual Studio 2026 では、実行中に「デバッグ → ウィンドウ → XAML バインディング エラー」（名前は版によって違います）で、一覧を見られます。
3. 調べたいバインディングに、`PresentationTraceSources.TraceLevel=High` を付ける。
4. 「ライブ ビジュアル ツリー」と「ライブ プロパティ エクスプローラー」で、その部品の `DataContext` が何かを確かめる（第 7 章）。

```xml
xmlns:diag="clr-namespace:System.Diagnostics;assembly=WindowsBase"

<TextBlock Text="{Binding Name, diag:PresentationTraceSources.TraceLevel=High}" />
```

3 番を付けると、そのバインディングが「どこでどのオブジェクトを探して、何が見つかったか」を、出力に詳しく書き出してくれます。うまくいかないバインディングの原因が分からないときの最後の手段です。

よくある原因の一覧です。

| 症状 | 原因 |
| --- | --- |
| 何も出ない | プロパティ名のつづり、`public` でない、フィールドになっている |
| 何も出ない | `DataContext` が `null`、または違うオブジェクト |
| 初期値は出るが、変えても追従しない | `INotifyPropertyChanged` の実装漏れ、通知の呼び忘れ |
| 画面で入力しても、データが変わらない | `Mode` が `OneWay`、または `UpdateSourceTrigger=LostFocus` のまま |
| `DataTemplate` の中で、親のプロパティが見つからない | `DataContext` がリストの 1 要素になっている。`RelativeSource` で祖先に回る |
| `ContextMenu` の中でバインディングが効かない | `ContextMenu` は別のウィンドウ扱い。`PlacementTarget` 経由で書く（第 35 章） |

## コードからバインディングを作る

XAML に書けないとき（部品をコードで作るときなど）は、コードでも作れます。

```csharp
var binding = new Binding("Hp")
{
    Source = viewModel,
    Mode = BindingMode.TwoWay,
    UpdateSourceTrigger = UpdateSourceTrigger.PropertyChanged,
};
textBox.SetBinding(TextBox.TextProperty, binding);
```

`TextBox.TextProperty` は、依存関係プロパティの登録証です（第 10 章）。バインディングのターゲットは、このように依存関係プロパティでなければなりません。

## 実行しなくても確認できる：デザイン時の DataContext

XAML エディタのデザイナーでも、バインディングの中身を見えるようにするには、デザイン時だけ有効な `d:DataContext` を書きます。

```xml
<UserControl xmlns:d="http://schemas.microsoft.com/expression/blend/2008"
             xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006"
             mc:Ignorable="d"
             d:DataContext="{d:DesignInstance Type=vm:PropertyViewModel}">
```

`d:DesignInstance` を指定すると、Visual Studio は `PropertyViewModel` のプロパティを知っているものとして、バインディングのパスを入力補完してくれます。パスのつづり間違いを、実行前に減らせます。

次の章では、リストやグリッドで大量のデータを見せる方法を扱います。

[第 14 章 リストとデータ表示](14-lists.md) へ進みます。

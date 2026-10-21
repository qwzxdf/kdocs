---
title: 第 7 章 データ バインディングと MVVM
tags:
  - C#連携
---

# 第 7 章 データ バインディングと MVVM

この章では WPF の中心になる考え方、<strong>データ バインディング</strong>と <strong>MVVM</strong> を学びます。エディタの画面は「データが変わったら、画面も変わる」「画面で入力したら、データも変わる」の連続です。これを手作業で書くと更新の書き忘れだらけになります。WPF は <strong>「このデータはこの部品に結びつけた」と宣言するだけ</strong>で、同期してくれます。

## この章の考え方

C++ で GUI を書いたことがあれば、次のようなコードを書いた経験があるはずです。

```cpp
// データが変わったら、画面を更新する
void OnHpChanged(int hp) {
  hp_label->SetText(std::to_string(hp));
  hp_bar->SetValue(hp);
}
// 画面で入力されたら、データを更新する
void OnTextEdited(const std::string& s) {
  player.hp = std::stoi(s);
}
```

画面の部品が増えるたびに「どこで何を更新するか」を手で書いて回ります。データを変える場所が増えると、更新を呼び忘れて画面が古いままになります。

WPF のデータ バインディングはこの更新を <strong>宣言</strong>に置き換えます。

```xml
<TextBox Text="{Binding Hp}" />
```

これだけで「この `TextBox` の `Text` はデータの `Hp` と結びついている」と宣言したことになります。`Hp` が変われば `TextBox` が変わり `TextBox` に入力すれば、`Hp` が変わります。

そして、データを持つクラスを画面（ビュー）とは別に作ります。これが <strong>MVVM</strong> です。

| 役割 | 名前 | 内容 | この教材では |
| --- | --- | --- | --- |
| M | <strong>Model</strong>（モデル） | アプリの本来のデータと処理 | エンジン側（C++）、`Scene` のデータなど |
| V | <strong>View</strong>（ビュー） | 画面。XAML | `MainWindow.xaml` など |
| VM | <strong>ViewModel</strong>（ビューモデル） | 画面に見せるデータと、画面からの操作を受ける処理 | `MainWindowViewModel` など（C#） |

ビューはビューモデルの<strong>プロパティを見る</strong>だけです。ビューモデルはビューを<strong>知りません</strong>。この一方向の関係のおかげでビューモデルは、画面なしでテストでき画面を作り替えても、ロジックは変わりません。

## この章のゴール

- `DataContext` と `{Binding}` でプロパティを画面に結びつけられる。
- `INotifyPropertyChanged` が何のためにあるか説明できる。
- `ICommand` でボタンの処理をビューモデルに移せる。
- `ObservableCollection` でリストの変更を画面に反映できる。

## 手順 1：最初のバインディング

この章の実験は新しいウィンドウで行います。`Editor` に `ViewModels` フォルダーを作り `PlayerViewModel.cs` を書きます。

```csharp
namespace Editor.ViewModels;

public class PlayerViewModel
{
    public string Name { get; set; } = "Alice";
    public int Hp { get; set; } = 100;
}
```

`MainWindow.xaml` に 2 つの `TextBox` を置き（既存の内容は、実験の間だけ置き換えて構いません）、`MainWindow.xaml.cs` で<strong>データの持ち主</strong>を指定します。

```xml
<StackPanel Margin="16">
    <TextBlock Text="名前" />
    <TextBox Text="{Binding Name}" />
    <TextBlock Text="HP" Margin="0,8,0,0" />
    <TextBox Text="{Binding Hp}" />
</StackPanel>
```

```csharp
public MainWindow()
{
    InitializeComponent();
    DataContext = new ViewModels.PlayerViewModel();
}
```

実行すると `TextBox` に「Alice」と「100」が出ます。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `{Binding Name}` | この部品のプロパティを <strong>`DataContext` の `Name` プロパティ</strong>に結びつける。`Name` は<strong>パス</strong>（プロパティの名前） |
| <strong>`DataContext`</strong> | 「バインディングが、データを探しに行く先」。<strong>すべての部品が持つプロパティ</strong>で、設定しなければ親の値を<strong>引き継ぐ</strong>。`Window` に設定すれば中の全部品が使える |
| 既定の向き | `TextBox.Text` のバインディングは、<strong>双方向</strong>（データ ⇄ 画面）。`TextBlock.Text` はデータ → 画面の一方向 |
| 型の自動変換 | `TextBox` の文字列 `"100"` を `int` の `Hp` に自動で変換する。変換できない入力（`abc`）はエラーになり赤枠が出る |

## 手順 2：変更を画面に伝える（INotifyPropertyChanged）

次に、コードから `Hp` を変えてみます。`PlayerViewModel` にメソッドを足します。

```csharp
public void Heal() { Hp += 10; }
```

ボタンを足して押したら `Heal` を呼びます（まずコードビハインドで試します）。

```xml
<Button Content="回復" Click="OnHeal" />
```

```csharp
private void OnHeal(object sender, RoutedEventArgs e)
{
    ((ViewModels.PlayerViewModel)DataContext).Heal();
}
```

押しても画面の HP は<strong>変わりません</strong>。`Hp` の値は変わっているのに画面はそれを知らないからです。

画面に知らせるには `PlayerViewModel` が <strong>`INotifyPropertyChanged`</strong> というインターフェースを実装し、値が変わるたびに<strong>「変わった」と通知</strong>します。

```csharp
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace Editor.ViewModels;

public class PlayerViewModel : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    private string _name = "Alice";
    public string Name
    {
        get => _name;
        set
        {
            if (_name == value) return;      // 変わっていなければ通知しない
            _name = value;
            OnPropertyChanged();
        }
    }

    private int _hp = 100;
    public int Hp
    {
        get => _hp;
        set
        {
            if (_hp == value) return;
            _hp = value;
            OnPropertyChanged();
        }
    }

    public void Heal() { Hp += 10; }

    // 「このプロパティが変わった」と通知する
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

今度はボタンを押すと画面の HP が変わります。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `INotifyPropertyChanged` | 「プロパティが変わったら、`PropertyChanged` イベントで知らせる」という約束のインターフェース。WPF のバインディングは `DataContext` がこれを実装していれば、そのイベントを<strong>自動で購読</strong>する |
| `PropertyChanged` イベント | プロパティが変わったときに発生させる。引数に変わったプロパティの<strong>名前</strong>を渡す |
| `PropertyChangedEventHandler` | `PropertyChanged` のデリゲート型。`(object? sender, PropertyChangedEventArgs e)` を受け取る |
| `PropertyChangedEventArgs` | 変わったプロパティの名前（`PropertyName`）を持つ引数オブジェクト |
| `[CallerMemberName]` | <strong>属性</strong>。引数に付けるとコンパイラが <strong>呼び出したメンバーの名前</strong>を自動で入れてくれる。`Hp` の `set` から呼べば `"Hp"` が入る。文字列を手で書くと名前を変えたときに壊れる |
| `if (_hp == value) return;` | 値が変わっていなければ通知しない。無駄な更新と無限ループを防ぐ |

### 属性

`[CallerMemberName]` のように角かっこで囲んで、宣言の前に付けるものを<strong>属性</strong>（Attribute）と呼びます。クラス、メソッド、引数などに追加の情報を付ける仕組みです。C++ の `[[nodiscard]]` に似ていますが、C# の属性は実行時にも読み取れる点が違います。この教材では後で `[DllImport]`、`[StructLayout]` などたくさん出てきます。

### 通知を忘れるとどうなるか

`_hp = value;` だけで `OnPropertyChanged()` を呼ばないとデータは変わっても、画面は変わりません。<strong>WPF のバグの大半は通知忘れ</strong>です。この書き方はプロパティごとに定型文が増えて、面倒です。次の章の Prism がこの定型文を短くしてくれます（`BindableBase`）。

## 手順 3：バインディングの設定

`{Binding}` にはいくつかの設定を付けられます。

```xml
<TextBox Text="{Binding Hp, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />
<TextBlock Text="{Binding Hp, StringFormat=HP: {0}}" />
```

| 設定 | 意味 |
| --- | --- |
| `Mode` | 同期の向き。`OneWay`（データ → 画面）、`TwoWay`（両方向）、`OneTime`（最初の 1 回だけ）、`OneWayToSource`（画面 → データ） |
| `UpdateSourceTrigger` | 画面からデータへ <strong>いつ</strong>書き戻すか。`TextBox` の既定は `LostFocus`（フォーカスを失ったとき）。`PropertyChanged` にすると 1 文字入力するたびに書き戻す |
| `StringFormat` | 表示の書式。`{0}` が値。`{0:F2}` で小数 2 桁 |
| `Converter` | 値を表示用に変換する関数（次の節） |
| `FallbackValue` | バインディングが失敗したときに表示する値 |
| `ElementName` | `DataContext` ではなく同じ XAML の別の部品（`x:Name`）を元にする |
| `RelativeSource` | 親や自分自身を元にする |

## 手順 4：値の変換（IValueConverter）

データの型と表示したい型が違うときは、<strong>コンバーター</strong>を使います。例えば、`bool` の `IsDead` を表示・非表示（`Visibility`）に変えます。

```csharp
using System.Globalization;
using System.Windows.Data;

namespace Editor.Converters;

public class BoolToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return (value is true) ? Visibility.Visible : Visibility.Collapsed;
    }

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
    {
        return value is Visibility.Visible;
    }
}
```

`App.xaml` のリソースに登録し使います。

```xml
<Application.Resources>
    <converters:BoolToVisibilityConverter x:Key="BoolToVisibility" />
</Application.Resources>
```

```xml
<TextBlock Text="死亡" Visibility="{Binding IsDead, Converter={StaticResource BoolToVisibility}}" />
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `IValueConverter` | `Convert`（データ → 画面）と `ConvertBack`（画面 → データ）の 2 つを持つインターフェース |
| `Visibility` | 部品の表示状態。`Visible`（見える）、`Hidden`（見えないが場所は残る）、`Collapsed`（見えず場所もつぶれる） |
| `xmlns:converters` | 名前空間の宣言を足す必要がある: `xmlns:converters="clr-namespace:Editor.Converters"` |
| `value is true` | 型の判定とパターン。`value` が `bool` の `true` であれば成功 |

WPF には `BooleanToVisibilityConverter` という標準のコンバーターもあります。自作の目的は仕組みを知ることです。

## 手順 5：コマンド（ICommand）

ボタンの処理を `Click` イベントではなく、ビューモデルの<strong>コマンド</strong>に結びつけます。

```csharp
public interface ICommand
{
    event EventHandler? CanExecuteChanged;
    bool CanExecute(object? parameter);
    void Execute(object? parameter);
}
```

| メンバー | 役割 |
| --- | --- |
| `Execute(parameter)` | 実行する処理 |
| `CanExecute(parameter)` | 今、実行してよいか。`false` ならボタンは<strong>自動で無効（グレー）</strong>になる |
| `CanExecuteChanged` | 「実行できるかどうかが変わった」と知らせるイベント。ボタンがこれを受けて `CanExecute` を呼び直す |

`ICommand` を実装した小さなクラスを書いてみます。

```csharp
using System.Windows.Input;

namespace Editor;

public class RelayCommand : ICommand
{
    private readonly Action _execute;
    private readonly Func<bool>? _canExecute;

    public RelayCommand(Action execute, Func<bool>? canExecute = null)
    {
        _execute = execute;
        _canExecute = canExecute;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => _canExecute?.Invoke() ?? true;
    public void Execute(object? parameter) => _execute();

    // 「実行できるかどうかが変わったかも」と通知する
    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
```

ビューモデルはこのコマンドをプロパティとして公開します。

```csharp
public class PlayerViewModel : INotifyPropertyChanged
{
    public PlayerViewModel()
    {
        HealCommand = new RelayCommand(Heal, () => Hp < 100);
    }

    public RelayCommand HealCommand { get; }

    private void Heal()
    {
        Hp = Math.Min(100, Hp + 10);
        HealCommand.RaiseCanExecuteChanged();   // HP が変わったので、押せるかどうかを再確認させる
    }
    // …（Hp、Name のプロパティは前のとおり）
}
```

```xml
<Button Content="回復" Command="{Binding HealCommand}" />
```

HP が 100 になるとボタンが<strong>自動で無効</strong>になります。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Command="{Binding HealCommand}"` | ボタンの `Command` プロパティにビューモデルのコマンドを結びつける。ボタンが押されると `Execute` が呼ばれる |
| `Action` / `Func<bool>` | 第 5 章のデリゲート。「実行する処理」と「実行してよいか」を関数として受け取る |
| `readonly` | コンストラクターでだけ代入できるフィールド。C++ の `const` メンバーに近い |
| `HealCommand { get; }` | `set` のない自動実装プロパティ。コンストラクターの中でだけ代入できる |
| `RelayCommand` | `ICommand` を関数 2 つで実装する、定番の小さなクラス。Prism の `DelegateCommand` がこれと同じ役割 |
| コマンドの利点 | 処理が、画面から<strong>切り離される</strong>。メニュー、ボタン、ショートカット キーが同じコマンドを共有できる。`CanExecute` で有効・無効が自動で決まる |

## 手順 6：コレクションの変更を伝える（ObservableCollection）

リストの<strong>要素が増減</strong>したときも画面に伝える必要があります。`List<T>` は通知しないので <strong>`ObservableCollection<T>`</strong> を使います。

```csharp
using System.Collections.ObjectModel;

public class SceneViewModel
{
    public ObservableCollection<string> Objects { get; } = new() { "Camera", "Cube", "Light" };

    public RelayCommand AddCommand { get; }

    public SceneViewModel()
    {
        AddCommand = new RelayCommand(() => Objects.Add($"Object {Objects.Count}"));
    }
}
```

```xml
<StackPanel>
    <ListBox ItemsSource="{Binding Objects}" Height="120" />
    <Button Content="追加" Command="{Binding AddCommand}" />
</StackPanel>
```

ボタンを押すたびにリストに行が増えます。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `ObservableCollection<T>` | 追加・削除・入れ替えを `CollectionChanged` イベントで通知するリスト。`List<T>` と同じように使える |
| `ItemsSource` | リスト系の部品（`ListBox`、`TreeView`、`DataGrid` など）に <strong>要素の集まり</strong>を渡すプロパティ |
| `ListBox` | 縦に項目を並べ選択できる部品 |
| `new()`（対象型 new） | 型が左辺から分かるときは、`new()` と省略できる。`= new ObservableCollection<string>()` と同じ |
| コレクション初期化子 `{ "a", "b" }` | 作ると同時に要素を入れる |

!!! warning "コレクションを丸ごと差し替えるならプロパティ通知が要る"
    `Objects = new ObservableCollection<string>(…)` のように<strong>入れ物ごと差し替える</strong>場合は、`ObservableCollection` の通知では足りません。そのプロパティ（`Objects`）自体に `INotifyPropertyChanged` の通知が必要です。普段は入れ物を作り替えず `Clear()` と `Add()` で中身を変えるのが安全です。

## 手順 7：項目の見た目を決める（DataTemplate）

`ListBox` に文字列ではなく <strong>自作のクラスのリスト</strong>を渡すと既定ではクラス名が表示されます。見た目を決めるのが <strong>`DataTemplate`</strong> です。

```csharp
public class ObjectItem
{
    public string Name { get; set; } = "";
    public string Kind { get; set; } = "";
}
```

```xml
<ListBox ItemsSource="{Binding Items}">
    <ListBox.ItemTemplate>
        <DataTemplate>
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="{Binding Name}" FontWeight="Bold" />
                <TextBlock Text="{Binding Kind}" Foreground="Gray" Margin="8,0,0,0" />
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

`DataTemplate` の中では `DataContext` が <strong>リストの 1 要素</strong>（ここでは `ObjectItem`）になります。そのため、`{Binding Name}` は各要素の `Name` を指します。

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DataTemplate` | データ 1 件をどんな部品で表示するかのひな形 |
| `ItemTemplate` | リスト系の部品が、各項目に使う `DataTemplate` |
| `FontWeight` | 文字の太さ。`Bold` など |
| `Orientation` | `StackPanel` の並べる向き。`Vertical`（既定）、`Horizontal` |

## 手順 8：MVVM の全体像

ここまで出てきたものを 1 枚にまとめます。

```text
View（XAML）                          ViewModel（C#）
 ┌───────────────────┐   Binding     ┌───────────────────────────┐
 │ TextBox Text ─────┼──────────────▶│ Hp  (INotifyPropertyChanged) │
 │ Button Command ───┼──────────────▶│ HealCommand (ICommand)       │
 │ ListBox ItemsSource┼─────────────▶│ Objects (ObservableCollection)│
 └───────────────────┘               └───────────────┬───────────┘
        ▲        DataContext を設定                   │ 使う
        └─── ビューは、VM を「見る」だけ                ▼
                                                  Model（エンジン／データ）
```

| 規則 | 理由 |
| --- | --- |
| ビューモデルはビュー（`Window`、`Button` など）を<strong>参照しない</strong> | 画面なしで、テストできる。画面を差し替えられる |
| ビューのコードビハインドは <strong>ほぼ空</strong>にする | ロジックは、ビューモデルに置く |
| 画面への通知は `INotifyPropertyChanged` と `ObservableCollection` で行う | 画面を直接触らずデータを変えるだけで、画面が追従する |
| 操作は `ICommand` で受ける | ボタンだけでなく、メニューやショートカットからも使える |

## よくあるミス

??? failure "バインディングが効かず何も表示されない"
    出力ウィンドウに `System.Windows.Data Error: 40 : BindingExpression path error: 'Nam' property not found…` のようなメッセージが出る。プロパティ名のタイプミス、`DataContext` の設定忘れプロパティが<strong>フィールド</strong>になっている（`{ get; set; }` が無い）ことが原因。WPF のバインディングは <strong>`public` なプロパティ</strong>しか見ない。

??? failure "コードで値を変えたのに、画面が変わらない"
    `INotifyPropertyChanged` の通知を忘れている。`set` の中で `OnPropertyChanged()` を呼んでいるか確認する。

??? failure "リストに追加しても、画面に出ない"
    `List<T>` を使っている。`ObservableCollection<T>` に変える。

??? failure "`TextBox` に入力しても、すぐにデータが変わらない"
    `UpdateSourceTrigger` の既定は `LostFocus`。入力のたびに反映するなら `UpdateSourceTrigger=PropertyChanged` を指定する。

??? failure "ボタンが、無効のままで戻らない"
    `CanExecute` の結果が変わったのに、`CanExecuteChanged` を発生させていない。`RaiseCanExecuteChanged()` を呼ぶ。

## この章のまとめ

- `DataContext` を設定し `{Binding パス}` で部品とプロパティを結びつける。
- データ側が `INotifyPropertyChanged` で通知すれば、画面が追従する。
- 操作は `ICommand`、リストは `ObservableCollection`、見た目は `DataTemplate` で決める。
- 画面（ビュー）とロジック（ビューモデル）を分けるのが MVVM。

## 次の章へ

`INotifyPropertyChanged` や `RelayCommand` を毎回、自分で書くのは大変です。次の章（[第 8 章 Prism の導入](08-prism-bootstrap.md)）では、Prism を導入しこれらの定型文をライブラリに任せます。同時にアプリの<strong>起動の流れ</strong>を Prism 流に作り直します。

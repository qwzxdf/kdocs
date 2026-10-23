---
title: 第 12 章 データバインディングと MVVM
tags:
  - C#連携
---

# 第 12 章 データバインディングと MVVM

WPF を使う最大の理由は、データバインディングです。エディタのように、画面とデータが何十か所もつながっているアプリでは、これがあるかないかで、コードの量がまるで変わります。この章では、バインディングの仕組みと、それを前提に画面とロジックを分ける MVVM という考え方を、小さな例で試しながら見ていきます。

!!! info "このページを読む前に"
    - [第 11 章 スタイル、リソース、テンプレート、トリガー](11-style-template.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


## バインディングがないと何が大変か

画面の部品に HP を表示するコードを、C++ の GUI ライブラリで書くとしましょう。

```cpp
void OnHpChanged(int hp) {            // データが変わったら、画面を更新する
  hp_label->SetText(std::to_string(hp));
  hp_bar->SetValue(hp);
}
void OnTextEdited(const std::string& s) {   // 画面で入力されたら、データを更新する
  player.hp = std::stoi(s);
}
```

部品が増えるたびに「どこで何を更新するか」を手で書いて回ることになります。HP を変える場所が増えれば、更新の呼び忘れも増えます。呼び忘れると、画面が古いまま残ります。

バインディングは、この更新を宣言に置き換えます。

```xml
<TextBox Text="{Binding Hp}" />
```

たったこれだけで「この `TextBox` の文字は、データの `Hp` とつながっている」と宣言したことになります。`Hp` が変われば `TextBox` が変わり、`TextBox` に入力すれば `Hp` が変わります。更新の呼び忘れという種類のバグが、なくなります。

## 最初のバインディング

小さな実験をしてみましょう。`Editor` に `ViewModels` フォルダーを作って、HP と名前を持つだけのクラスを置きます。

```csharp title="ViewModels/PlayerViewModel.cs"
namespace Editor.ViewModels;

public class PlayerViewModel
{
    public string Name { get; set; } = "Alice";
    public int Hp { get; set; } = 100;
}
```

画面の側は、入力欄を 2 つ置きます。

```xml title="MainWindow.xaml（実験用に中身を置き換える）"
<StackPanel Margin="16">
    <TextBlock Text="名前" />
    <TextBox Text="{Binding Name}" />
    <TextBlock Text="HP" Margin="0,8,0,0" />
    <TextBox Text="{Binding Hp}" />
</StackPanel>
```

最後に、「バインディングはどのオブジェクトを見に行けばいいのか」を教えます。

```csharp title="MainWindow.xaml.cs"
public MainWindow()
{
    InitializeComponent();
    DataContext = new ViewModels.PlayerViewModel();
}
```

実行すると、入力欄に `Alice` と `100` が出ます。

`{Binding Name}` の `Name` は、「どこかのオブジェクトの `Name` プロパティ」という意味です。そのどこかを決めているのが `DataContext` です。`DataContext` は、すべての部品が持っているプロパティで、ここに設定したオブジェクトが、バインディングの探し先になります。部品に設定しなければ、親の `DataContext` を引き継ぎます。つまり、ウィンドウに 1 回設定すれば、中の全部品がそれを見に行きます。

ここまでは、バインディングの基本の形です。「画面の部品 → `{Binding プロパティ名}` → `DataContext` のオブジェクト」という順に、矢印をたどって読めば、どの値がどこから来ているか追えます。慣れるまでは、この矢印を毎回たどってみてください。

`TextBox` の `Text` は、初期状態で双方向になっています。画面で書き換えたら `Hp` が変わり、逆に `Hp` が変われば画面が変わります（ただし、後者はもう少し準備が要ります。すぐ次の節です）。文字列 `"100"` が `int` の `Hp` に自動で変換される点も覚えておいてください。`abc` のように変換できないものを入れると、入力欄が赤い枠になって、値は反映されません。

## 画面が更新されない

コードから HP を変えてみます。`PlayerViewModel` にメソッドを足して、ボタンで呼びます。

```csharp
public void Heal() { Hp += 10; }
```

```xml
<Button Content="回復" Click="OnHeal" />
```

```csharp
private void OnHeal(object sender, RoutedEventArgs e)
{
    ((ViewModels.PlayerViewModel)DataContext).Heal();
}
```

押しても、画面の HP は変わりません。デバッガーで見ると `Hp` は確かに増えています。画面だけが、それを知らないのです。

バインディングは、最初に値を読むだけで、その後は「値が変わったよ」という知らせを待っています。通常のプロパティは、変わっても誰にも知らせません。知らせてもらうには、`INotifyPropertyChanged` というインターフェースを実装して、値が変わるたびに `PropertyChanged` イベントを起こします。

```csharp title="ViewModels/PlayerViewModel.cs"
using System.ComponentModel;
using System.Runtime.CompilerServices;

namespace Editor.ViewModels;

public class PlayerViewModel : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    private int _hp = 100;
    public int Hp
    {
        get => _hp;
        set
        {
            if (_hp == value) return;      // 変わっていなければ知らせない
            _hp = value;
            OnPropertyChanged();           // 「Hp が変わった」と知らせる
        }
    }

    // Name も同じ形で書く（省略）

    public void Heal() { Hp += 10; }

    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

今度は、ボタンを押すと画面の HP が変わります。

`[CallerMemberName]` は、呼び出した側のメンバーの名前（ここでは `Hp`）を、コンパイラーが引数に自動で入れてくれる属性です。`OnPropertyChanged()` と書くだけで `"Hp"` が渡されるので、名前を文字列で書き間違えたり、名前を変えたときに直し忘れたりする心配がなくなります。

属性は、`[...]` で宣言に追加の情報を付ける C# の仕組みです。C++ の `[[nodiscard]]` に似ていますが、実行時にも読み取れる点が違います。これから `[DllImport]` や `[StructLayout]` など、いくつも出てきます。

WPF でありがちな事故の大半は、この通知の書き忘れです。`set` の中に `OnPropertyChanged()` を書いたか、値が変わったのに通知しない道が残っていないか。画面が更新されないときは、まずここを疑ってください。

プロパティごとに同じ定型文を書くのは面倒ですが、次の章で Prism の `BindableBase` が 1 行にしてくれます。

## 画面が古いままのときのチェックリスト

バインディングは、間違えても例外が出ません。静かに何も表示されないだけです。そこで、症状別に確認する順番を決めておくと便利です。

画面に何も出ないとき。

1. `{Binding ...}` のプロパティ名のつづりを確かめる。`Massage` と `Message` のような 1 文字違いが定番です。
2. そのプロパティが `public` で、フィールドではなく `{ get; set; }` のプロパティになっているか。WPF のバインディングは、フィールドを見ません。
3. `DataContext` が設定されているか。設定した対象は、その部品の親の位置か。
4. Visual Studio の「出力」ウィンドウに `BindingExpression path error` が出ていないか。バインディングの失敗はここにだけ書かれます。

値は出るのに、変えても画面が追従しないとき。

1. `INotifyPropertyChanged` を実装しているか。
2. `set` の中で `PropertyChanged` を起こしているか。
3. 起こすときのプロパティ名は合っているか。
4. コレクションなら、`List<T>` ではなく `ObservableCollection<T>` か（後で説明します）。

入力しても、すぐにデータへ反映されないとき。

- `TextBox` の `Text` は、入力欄からフォーカスが外れたときに初めてデータへ反映されます。1 文字入力するたびに反映したければ、`UpdateSourceTrigger=PropertyChanged` を付けます。

バインディングの細かい設定の違いは第 13 章にまとめました。

## バインディングの設定

`{Binding}` には、いくつかの設定を足せます。

```xml
<TextBox Text="{Binding Hp, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />
<TextBlock Text="{Binding Hp, StringFormat=HP: {0}}" />
```

`Mode` は、データがどちら向きに流れるかです。`OneWay` はデータから画面へだけ、`TwoWay` は双方向、`OneTime` は最初に読むだけ、`OneWayToSource` は画面からデータへだけです。何も書かなければ、部品とプロパティごとの既定値になり、入力を受け付ける `TextBox.Text` のようなものは双方向、`TextBlock.Text` のようなものは一方向になります。

`UpdateSourceTrigger` は、画面からデータへ書き戻すタイミングです。`TextBox` の既定は `LostFocus` で、これが先ほどのチェックリストの最後の項目の理由でした。

`StringFormat` は表示形式の指定で、`{0:F2}` なら小数 2 桁になります。ほかにも `Converter`、`FallbackValue`、`ElementName`、`RelativeSource` などがあります。

## 値の変換（Converter）

データの型と、画面に出したい型が違うことがあります。たとえば `bool` の `IsDead` を、`Visibility`（見える / 見えない）に変えたい場合です。こういうときは、変換用のクラスを書きます。

```csharp title="Converters/BoolToVisibilityConverter.cs"
using System.Globalization;
using System.Windows.Data;

namespace Editor.Converters;

public class BoolToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        => value is true ? Visibility.Visible : Visibility.Collapsed;

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => value is Visibility.Visible;
}
```

`Convert` がデータから画面へ、`ConvertBack` が画面からデータへの変換です。使うには、`App.xaml` のリソースに登録して名前で呼びます。

```xml
<Application.Resources>
    <converters:BoolToVisibilityConverter x:Key="BoolToVisibility" />
</Application.Resources>
```

```xml
<TextBlock Text="死亡"
           Visibility="{Binding IsDead, Converter={StaticResource BoolToVisibility}}" />
```

`Visibility` には `Visible`（見える）、`Hidden`（見えないが場所は残る）、`Collapsed`（見えず、場所も詰まる）の 3 つがあります。この変換は WPF にも `BooleanToVisibilityConverter` という名前で最初から入っているので、普段は自作しなくても構いません。ここでは仕組みを知るために書きました。

## ボタンの処理をビューモデルに移す（ICommand）

先ほどの `Click="OnHeal"` は、ボタンの処理が画面のコードビハインドに書かれています。ボタンが何十個にもなると、画面のコードが処理だらけになります。バインディングが「データの受け渡し」を画面から切り離してくれたように、「操作」も切り離せます。それがコマンドです。

`ICommand` というインターフェースは 3 つのメンバーを持っています。

| メンバー | 役目 |
| --- | --- |
| `Execute(parameter)` | 実行する処理 |
| `CanExecute(parameter)` | 今、実行してよいか。`false` ならボタンが自動で無効になる |
| `CanExecuteChanged` | 「実行してよいかどうかが変わったかも」という知らせ |

便利なのは `CanExecute` です。HP が満タンのときは回復ボタンを押せなくする、といった判断をビューモデルに書けば、ボタンの有効・無効を画面側でいじる必要がなくなります。

`ICommand` を実装した、小さなクラスを自作してみます。

```csharp title="RelayCommand.cs"
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

    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
```

「実行する関数」と「実行してよいかを返す関数」を渡すだけの、単純なクラスです。ビューモデルで使うとこうなります。

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
        HealCommand.RaiseCanExecuteChanged();   // 押せるかどうかを聞き直してもらう
    }
    // Hp、Name のプロパティは前のとおり
}
```

```xml
<Button Content="回復" Command="{Binding HealCommand}" />
```

HP が 100 に達すると、ボタンが自動でグレーになります。`RaiseCanExecuteChanged()` を呼ぶのを忘れると、ボタンの状態が更新されません。この手書きも、次の章で Prism の `DelegateCommand` の `ObservesProperty` が引き受けてくれます。

## コレクションの変更も知らせる（ObservableCollection）

リストに要素を足したり消したりしたときも、画面へ知らせる必要があります。`List<T>` は何も知らせないので、`ObservableCollection<T>` を使います。

```csharp
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

ボタンを押すたびに、一覧に行が増えます。`ItemsSource` は、リスト系の部品に「要素の集まり」を渡すプロパティです。

ひとつ注意があります。`Objects = new ObservableCollection<string>(...)` のように、入れ物ごと差し替えると、`ObservableCollection` の通知では足りません。そのプロパティ自体の `PropertyChanged` が必要です。普段は入れ物を作り替えず、`Clear()` と `Add()` で中身を変えるほうが安全です。

## 項目の見た目を決める（DataTemplate）

`ListBox` に、文字列ではなく自作クラスのリストを渡すと、初期状態ではクラス名がそのまま出てしまいます。1 件ごとの見た目を決めるのが `DataTemplate` です。

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

大事なのは、`DataTemplate` の中では `DataContext` が「リストの 1 要素」になることです。だから `{Binding Name}` は、各要素の `Name` を指します。親のビューモデルの `Name` ではありません。「あれ、ここの `DataContext` は何だろう」と迷ったときは、`DataTemplate` の中なら 1 要素、それ以外なら親から引き継いだもの、と考えれば追えます。

## MVVM という考え方

ここまでで出てきた道具をまとめると、こうなります。

| 役割 | 呼び方 | この教材では |
| --- | --- | --- |
| データとその操作 | ViewModel（ビューモデル） | `PlayerViewModel`、`SceneTreeViewModel` など |
| 画面 | View（ビュー） | XAML |
| 本来のデータ・ロジック | Model（モデル） | エンジン側、`SceneDocument` など |

ビューはビューモデルのプロパティを見るだけです。ビューモデルはビューを知りません。この一方通行のおかげで、画面を作り替えてもロジックは壊れず、ビューモデルを画面なしでテストすることもできます。

```text
View（XAML）                   ViewModel（C#）
  TextBox.Text  ──Binding──▶   Hp  （INotifyPropertyChanged）
  Button.Command ─Binding──▶   HealCommand （ICommand）
  ListBox.ItemsSource ─────▶   Objects （ObservableCollection）
                                │ 使う
                                ▼
                              Model（エンジン、ドキュメント）
```

「このコードはどこに書けばよいか」で迷ったときの目安も、書いておきます。

| こういう処理は | ここに書く |
| --- | --- |
| 画面に見せる値、入力された値の検証 | ビューモデル |
| ボタンを押したときの処理 | ビューモデル（コマンド） |
| ファイルやエンジンの呼び出し | ビューモデルから、サービス（インターフェース）を通して |
| 見た目だけの話（アニメーション、部品の配置の微調整） | XAML か、ビューのコードビハインド |
| ウィンドウや部品そのものを触る処理（`HwndHost` のイベントを受けるなど） | ビューのコードビハインド（ビューモデルに橋渡しするだけにする） |
| `MessageBox`、ファイル ダイアログ | サービスに包んで、ビューモデルから呼ぶ（第 18 章） |

コードビハインドを絶対に使ってはいけない、という決まりではありません。画面の部品そのものを相手にする処理は、ビューのコードビハインドに書いたほうが素直です。ただしロジックは書かず、ビューモデルへ橋渡しするだけにとどめます。

## ここまでのまとめ

- `DataContext` に入れたオブジェクトを、`{Binding プロパティ名}` が見に行く。
- 画面が追従するには、`INotifyPropertyChanged`（プロパティ）と `ObservableCollection`（コレクション）で変更を知らせる。
- 操作は `ICommand`、リストの 1 件の見た目は `DataTemplate`。
- 画面で困ったら、「出力」ウィンドウの `BindingExpression path error` を見る。

## 関連する章

- [第 13 章 バインディングを掘り下げる](13-binding.md)：Mode と UpdateSourceTrigger の既定値、ElementName、RelativeSource、MultiBinding、入力検証、デバッグ
- [第 14 章 リストとデータ表示](14-lists.md)：ListBox / ListView / DataGrid / ComboBox の使い分けと選択
- [第 22 章 コードビハインドを減らす](22-behaviors.md)：Behaviors でイベントをコマンドに結ぶ
- [第 20 章 MVVM ライブラリを比べる](20-mvvm-libraries.md)：Prism の `BindableBase` と CommunityToolkit.Mvvm、ReactiveProperty

次の章では、バインディングの設定を細かく見ていきます。「更新されない」の原因の多くは、ここにあります。

[第 13 章 バインディングを掘り下げる](13-binding.md) へ進みます。

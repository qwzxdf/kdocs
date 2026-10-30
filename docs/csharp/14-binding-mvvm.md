---
title: 第 14 章 データバインディングと MVVM
tags:
  - C#連携
---

# 第 14 章 データバインディングと MVVM

第 6 章で作ったエディタは、枠だけで中身が空っぽです。シーン ツリーには「シーン ツリー」という文字が、プロパティには「プロパティ」という文字が置いてあるだけで、オブジェクトを選んでも何も起きません。この章では、この 2 つのパネルを、データバインディングでつなぎます。シーン ツリーで選んだオブジェクトの名前と位置が、プロパティ パネルに出て、そこで書き換えられるようにします。

WPF を使う最大の理由は、データバインディングです。画面とデータが何十か所もつながるエディタでは、これがあるかないかで、コードの量がまるで変わります。

!!! info "このページを読む前に"
    - [第 13 章 見た目のテーマを入れる](13-theme.md)（前の章。ここまでの内容が前提になる）
    - [第 12 章 Prism の導入と起動の流れ](12-prism-bootstrap.md)（`BindableBase` と `DelegateCommand` は、ここで入れた Prism のもの）
    - [第 6 章 WPF プロジェクトと XAML](06-wpf-xaml.md)（この章は、そこで作った `MainWindow.xaml` を書き換えていく）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Scene/SceneObjectViewModel.cs`（新規） | シーンの 1 オブジェクト（名前と位置） |
    | `MainWindowViewModel.cs`（変更） | オブジェクトの一覧と、選択中のオブジェクト |
    | `MainWindow.xaml`（変更） | 左にシーン ツリー、右にプロパティ パネルを作る |

    値の変化を画面に知らせる土台（`BindableBase`）とボタンの処理（`DelegateCommand`）は、第 12 章で入れた Prism のものを使います。自分では書きません。そのかわり、中でどんなことが起きているのかは、「深掘り」の節で見ます。

    このあと、各節の終わりに「深掘り」を置いています。作った物の中に出てきた仕組みを、1 つずつ見ていく節です。

## バインディングがないと何が大変か

オブジェクトの位置を画面の入力欄に出すコードを、C++ の GUI ライブラリで書くとしましょう。

```cpp
void OnPositionChanged(const Vec3& pos) {      // データが変わったら、画面を更新する
  x_edit->SetText(std::to_string(pos.x));
  y_edit->SetText(std::to_string(pos.y));
}
void OnXEdited(const std::string& s) {         // 画面で入力されたら、データを更新する
  selected->position.x = std::stof(s);
}
```

部品が増えるたびに「どこで何を更新するか」を手で書いて回ることになります。位置を変える場所が増えれば、更新の呼び忘れも増えます。呼び忘れると、画面が古いまま残ります。

バインディングは、この更新を宣言に置き換えます。

```xml
<TextBox Text="{Binding X}" />
```

これだけで、「この `TextBox` の文字は、データの `X` とつながっている」と宣言したことになります。`X` が変われば `TextBox` が変わり、`TextBox` に入力すれば `X` が変わります。更新の呼び忘れという種類のバグがなくなります。

## まず、選んだオブジェクトを表示する

最初は、画面に出すだけにします。オブジェクトを表すクラスを、`Editor` の下に `Scene` フォルダーを作って置きます。

この教材では、フォルダーを「種類」（ビュー、ビューモデル、モデル）ではなく「機能」（シーン、アセット、ログ…）で切ります。ひとつの機能を直すとき、触るファイルが同じフォルダーに集まるからです。その機能の画面、ビューモデル、データの型は、まとめて同じフォルダーに置きます。複数の機能が使う道具だけは、あとで `Shared` フォルダーに置きます。

```csharp title="Scene/SceneObjectViewModel.cs（新規）"
namespace Editor.Scene;

public class SceneObjectViewModel
{
    public SceneObjectViewModel(string name, float x = 0, float y = 0, float z = 0)
    {
        Name = name;
        X = x;
        Y = y;
        Z = z;
    }

    public string Name { get; set; }
    public float X { get; set; }
    public float Y { get; set; }
    public float Z { get; set; }
}
```

次に、ウィンドウ全体のデータを持つクラスです。今は、選択中のオブジェクトを 1 つ持つだけです。

```csharp title="MainWindowViewModel.cs（変更）"
using Editor.Scene;

namespace Editor;

public class MainWindowViewModel
{
    public string Title => "MiniEngine Editor";
    public SceneObjectViewModel Selected { get; set; } = new("Cube", 1, 0, 2);
}
```

第 12 章で作った `MainWindowViewModel` に、`Selected` を足しました。このクラスをウィンドウに持たせる作業は、もう要りません。`AutoWireViewModel="True"` を付けてあるので、ViewModelLocator が見つけて、`DataContext` に入れてくれます。`Title` は、第 12 章で確かめたときの「（ビューモデルから）」を消した形にしました。

最後に、第 6 章で「プロパティ」という文字だけを置いた右のパネルを、入力欄に差し替えます。

```xml title="MainWindow.xaml（変更：右のパネル）"
<Border Grid.Column="4" Background="#FF252526" Padding="8">
    <StackPanel>
        <TextBlock Text="プロパティ" Foreground="White" FontWeight="Bold" />

        <TextBlock Text="名前" Foreground="Gray" Margin="0,8,0,0" />
        <TextBox Text="{Binding Selected.Name}" />

        <TextBlock Text="位置" Foreground="Gray" Margin="0,8,0,0" />
        <TextBox Text="{Binding Selected.X}" />
        <TextBox Text="{Binding Selected.Y}" Margin="0,4,0,0" />
        <TextBox Text="{Binding Selected.Z}" Margin="0,4,0,0" />
    </StackPanel>
</Border>
```

`F5` で実行すると、右のパネルに `Cube`、`1`、`0`、`2` が出ます。

### 深掘り：`{Binding Selected.Name}` はどこを見ているのか

`{Binding Selected.Name}` の `Selected.Name` は、「どこかのオブジェクトの `Selected` プロパティの、さらに `Name` プロパティ」という意味です。その「どこかのオブジェクト」を決めているのが `DataContext` です。

`DataContext` は、すべての部品が持っているプロパティで、ここに設定したオブジェクトが、バインディングの探し先になります。部品に設定しなければ、親の `DataContext` を引き継ぎます。上では ViewModelLocator が `MainWindow` に 1 回設定しただけですが、ウィンドウの中のすべての部品が、それを見に行きます。

読むときは、「画面の部品 → `{Binding パス}` → `DataContext` のオブジェクト」の順に矢印をたどります。右パネルの `TextBox` なら、`TextBox` → `Selected.Name` → `MainWindowViewModel` の `Selected` → その `Name`、です。慣れるまでは、この矢印を毎回たどってみてください。

`TextBox` の `Text` は、初期状態で双方向になっています。画面で書き換えると `Name` が変わります。文字列 `"1"` が `float` の `X` に自動で変換される点も覚えておいてください。`abc` のように変換できないものを入れると、入力欄が赤い枠になって、値は反映されません。

## 画面が更新されない

次は、コードの側から値を変えてみます。位置を原点に戻す「位置をリセット」ボタンを、プロパティ パネルに足します。

```csharp title="Scene/SceneObjectViewModel.cs（変更：メソッドを足す）"
public void Reset()
{
    X = 0;
    Y = 0;
    Z = 0;
}
```

```xml title="MainWindow.xaml（変更：パネルの最後に足す）"
<Button Content="位置をリセット" Margin="0,12,0,0" Click="OnReset" />
```

```csharp title="MainWindow.xaml.cs（変更）"
private void OnReset(object sender, RoutedEventArgs e)
{
    ((MainWindowViewModel)DataContext).Selected.Reset();
}
```

実行して押しても、入力欄の `1`、`0`、`2` は変わりません。デバッガーで見ると、`X`、`Y`、`Z` は確かに 0 になっています。画面だけが、それを知らないのです。

### 深掘り：INotifyPropertyChanged

バインディングは、最初に値を読んだあと、「値が変わったよ」という知らせを待っています。通常のプロパティは、変わっても誰にも知らせません。知らせるには、`INotifyPropertyChanged` というインターフェースを実装して、値が変わるたびに `PropertyChanged` イベントを起こします。

```csharp
using System.ComponentModel;
using System.Runtime.CompilerServices;

public class SceneObjectViewModel : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    private float _x;
    public float X
    {
        get => _x;
        set
        {
            if (_x == value) return;      // 変わっていなければ知らせない
            _x = value;
            OnPropertyChanged();          // 「X が変わった」と知らせる
        }
    }

    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
```

`[CallerMemberName]` は、呼び出した側のメンバーの名前（ここでは `X`）をコンパイラーが引数に自動で入れてくれる属性です。`OnPropertyChanged()` と書くだけで `"X"` が渡されるので、名前を文字列で書き間違えたり、名前を変えたときに直し忘れたりしません。

属性は、`[...]` で宣言に追加の情報を付ける C# の仕組みです。C++ の `[[nodiscard]]` に似ていますが、実行時にも読み取れる点が違います。これから `[DllImport]` や `[StructLayout]` など、いくつも出てきます。

WPF でありがちな事故の大半は、この通知の書き忘れです。`set` の中に `OnPropertyChanged()` を書いたか、値が変わったのに通知しない道が残っていないか。画面が更新されないときは、まずここを疑ってください。

### Prism の BindableBase を使う

とはいえ、プロパティごとにこの 10 行を書くのは大変です。オブジェクトの名前と位置だけで 4 つ、これから増えていく他のビューモデルを含めると、数十個になります。共通の部分は、基底クラスに移すのが定番で、Prism にはそれが用意されています。`BindableBase` です。

```csharp title="Scene/SceneObjectViewModel.cs（変更：全体）"
using Prism.Mvvm;

namespace Editor.Scene;

public class SceneObjectViewModel : BindableBase
{
    private string _name;
    private float _x, _y, _z;

    public SceneObjectViewModel(string name, float x = 0, float y = 0, float z = 0)
    {
        _name = name;
        _x = x;
        _y = y;
        _z = z;
    }

    public string Name { get => _name; set => SetProperty(ref _name, value); }
    public float X { get => _x; set => SetProperty(ref _x, value); }
    public float Y { get => _y; set => SetProperty(ref _y, value); }
    public float Z { get => _z; set => SetProperty(ref _z, value); }

    public void Reset()
    {
        X = 0;
        Y = 0;
        Z = 0;
    }
}
```

`BindableBase` は、`INotifyPropertyChanged` の実装と、`SetProperty` という補助の関数を持っています。`SetProperty(ref _x, value)` は、「値が前と違うときだけ、フィールドを入れ替えて、変わったと知らせる」という関数です。さきほど手で書いた `if (_x == value) return;` から `OnPropertyChanged()` までを、1 行にまとめたものです。変わったかどうかを `bool` で返すので、変わったときだけ別の処理をしたいときにも使えます（あとで出てきます）。

`ref _x` の `ref` は、フィールドそのものへの参照を渡す印です。C++ の `T&` に当たります。`SetProperty` は呼び出し側のフィールド `_x` を書き換えなければならないので、値のコピーではなく参照で受け取ります。呼ぶ側にも `ref` と書く決まりです。

通知を名前で送りたいときは、`RaisePropertyChanged(nameof(HasSelection))` と書きます。`nameof` は名前をコンパイル時に文字列にする書き方です。

中身は、次のような形です。Prism の実物はもう少し細かいのですが、働きは同じです。

```csharp title="BindableBase の中身（イメージ。Editor には入れない）"
public abstract class BindableBase : INotifyPropertyChanged
{
    public event PropertyChangedEventHandler? PropertyChanged;

    protected bool SetProperty<T>(ref T storage, T value, [CallerMemberName] string? propertyName = null)
    {
        if (EqualityComparer<T>.Default.Equals(storage, value)) return false;
        storage = value;
        RaisePropertyChanged(propertyName);
        return true;
    }

    protected void RaisePropertyChanged([CallerMemberName] string? propertyName = null)
        => PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
}
```

もう一度実行して「位置をリセット」を押すと、入力欄が 0 になります。

### 画面が古いままのときのチェックリスト

バインディングは、間違えても例外が出ません。静かに何も表示されないだけです。症状別に、確認する順番を決めておくと便利です。

画面に何も出ないとき。

1. `{Binding ...}` のプロパティ名のつづりを確かめる。`Massage` と `Message` のような 1 文字違いが定番です。
2. そのプロパティが `public` で、フィールドではなく `{ get; set; }` のプロパティになっているか。WPF のバインディングは、フィールドを見ません。
3. `DataContext` が設定されているか。設定した対象は、その部品の親の位置か。
4. Visual Studio の「出力」ウィンドウに `BindingExpression path error` が出ていないか。バインディングの失敗はここにだけ書かれます。

値は出るのに、変えても画面が追従しないとき。

1. `INotifyPropertyChanged` を実装しているか。
2. `set` の中で `PropertyChanged` を起こしているか。
3. 起こすときのプロパティ名は合っているか。
4. コレクションなら、`List<T>` ではなく `ObservableCollection<T>` か（あとで使います）。

入力しても、すぐにデータへ反映されないとき。

- `TextBox` の `Text` は、入力欄からフォーカスが外れたときに初めてデータへ反映されます。次の節で扱います。

## 入力のたびに反映する

名前の `TextBox` に文字を打っても、フォーカスを外すまでは `Name` が変わりません。あとで、シーン ツリーに名前を出すようにすると、打っている最中に反映されたほうが気持ちがよいので、設定を足します。

```xml title="MainWindow.xaml（変更：名前の入力欄）"
<TextBox Text="{Binding Selected.Name, UpdateSourceTrigger=PropertyChanged}" />
```

位置の入力欄は、このままにします。理由は、深掘りで説明します。

### 深掘り：`{Binding}` の設定

`{Binding}` には、いくつかの設定を足せます。

```xml
<TextBox Text="{Binding Selected.Name, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />
<TextBlock Text="{Binding Selected.X, StringFormat=X: {0:F2}}" />
```

`Mode` は、データがどちら向きに流れるかです。

| 値 | 向き |
| --- | --- |
| `OneWay` | データから画面へだけ |
| `TwoWay` | 双方向 |
| `OneTime` | 最初に読むだけ |
| `OneWayToSource` | 画面からデータへだけ |

何も書かなければ、部品とプロパティごとの既定値になります。入力を受け付ける `TextBox.Text` のようなものは双方向で、`TextBlock.Text` のようなものは一方向です。

`UpdateSourceTrigger` は、画面からデータへ書き戻すタイミングです。`TextBox` の既定は `LostFocus` で、これが先ほどのチェックリストの最後の項目の理由でした。数値の入力欄に `PropertyChanged` を付けると、`1.` のように小数点を打った途中の文字列が、そのたびに数値へ変換されて、入力しにくくなることがあります。そのため、数値は既定のまま、名前だけに付けました。

`StringFormat` は表示形式の指定で、`{0:F2}` なら小数 2 桁になります。ほかにも `Converter`、`FallbackValue`、`ElementName`、`RelativeSource` などがあります。第 15 章で詳しく扱います。

## ボタンの処理をビューモデルに移す

「位置をリセット」は、`Click="OnReset"` で、コードビハインドの `OnReset` を呼んでいます。ボタンが何十個にもなると、画面のコードが処理だらけになります。バインディングがデータの受け渡しを画面から切り離してくれたように、操作も切り離せます。それがコマンドです。

コマンドを作る部品は、Prism の `DelegateCommand` を使います。「実行する処理」と「いま実行してよいか」を、関数として渡して作ります。

使うのは `SceneObjectViewModel` です。リセットは、すでに原点にいるときは押せなくしたいので、`canExecute` も渡します。

```csharp title="Scene/SceneObjectViewModel.cs（変更）"
using Prism.Commands;

public SceneObjectViewModel(string name, float x = 0, float y = 0, float z = 0)
{
    _name = name;
    _x = x;
    _y = y;
    _z = z;
    ResetCommand = new DelegateCommand(Reset, () => _x != 0 || _y != 0 || _z != 0)
        .ObservesProperty(() => X)
        .ObservesProperty(() => Y)
        .ObservesProperty(() => Z);
}

public DelegateCommand ResetCommand { get; }

private void Reset()
{
    X = 0;
    Y = 0;
    Z = 0;
}
```

`DelegateCommand` の 1 つ目の引数が、押されたときの処理（`Reset`）で、2 つ目が「押してよいか」の判断です。ここでは、どれかが 0 以外なら押せる、としています。

`ObservesProperty(() => X)` は、「`X` が変わったら、押してよいかをもう一度聞き直して」という宣言です。`() => X` は、プロパティを指す式で、Prism がそこからプロパティ名を取り出しています。`X`、`Y`、`Z` の `set` の側には、何も足していません。コマンドの側から、プロパティを見張っているわけです。

`Reset` は、`public` から `private` に変えました。外からは、コマンドを通して呼ぶからです。ボタンは、`Click` をやめて `Command` にします。

```xml title="MainWindow.xaml（変更：ボタン）"
<Button Content="位置をリセット" Margin="0,12,0,0"
        Command="{Binding Selected.ResetCommand}" />
```

コードビハインドの `OnReset` は、もう使いません。`MainWindow.xaml.cs` から消してください。実行すると、位置がすべて 0 のときはボタンが灰色になり、どれかを 0 以外に書き換えると、押せるようになります。

### 深掘り：ICommand

`ICommand` というインターフェースは、3 つのメンバーを持っています。

| メンバー | 役目 |
| --- | --- |
| `Execute(parameter)` | 実行する処理 |
| `CanExecute(parameter)` | 今、実行してよいか。`false` ならボタンが自動で無効になる |
| `CanExecuteChanged` | 「実行してよいかどうかが変わったかも」という知らせ |

便利なのは `CanExecute` です。ボタンの有効、無効の判断をビューモデルに書けば、画面の側でボタンを無効にする処理を書かなくて済みます。

`CanExecuteChanged` は、「実行してよいかどうかが変わったかもしれないので、もう一度聞き直してください」という合図です。プロパティの `PropertyChanged` と同じ役割で、これが起きないと、ボタンの状態が更新されません。`DelegateCommand` には `RaiseCanExecuteChanged()` という、この合図を手で出す関数もあります。ただ、呼び忘れるとボタンの状態が古いままになるので、プロパティに連動するものは、`ObservesProperty` に任せるほうが安全です。

`DelegateCommand` の中身は、「`Action` と `Func<bool>` を受け取って、`ICommand` の 3 つのメンバーに渡す」だけの小さなクラスです。自分で `ICommand` を実装するときも、コンストラクターで受け取った関数を `Execute` と `CanExecute` から呼ぶだけの形になります。

## シーン ツリーを作る

右のパネルが動いたので、左のシーン ツリーに、オブジェクトを並べます。複数のオブジェクトを持つ `MainWindowViewModel` に書き直します。

```csharp title="MainWindowViewModel.cs（変更：全体）"
using System.Collections.ObjectModel;
using Prism.Commands;
using Prism.Mvvm;
using Editor.Scene;

namespace Editor;

public class MainWindowViewModel : BindableBase
{
    private SceneObjectViewModel? _selected;

    public MainWindowViewModel()
    {
        Objects = new ObservableCollection<SceneObjectViewModel>
        {
            new("Camera", 0, 2, -5),
            new("Cube", 1, 0, 2),
            new("Light", 3, 5, 0),
        };
        Selected = Objects[1];
        AddCommand = new DelegateCommand(Add);
    }

    public string Title => "MiniEngine Editor";

    public ObservableCollection<SceneObjectViewModel> Objects { get; }

    public SceneObjectViewModel? Selected
    {
        get => _selected;
        set
        {
            if (SetProperty(ref _selected, value))
                RaisePropertyChanged(nameof(HasSelection));
        }
    }

    public bool HasSelection => _selected is not null;

    public DelegateCommand AddCommand { get; }

    private void Add()
    {
        var obj = new SceneObjectViewModel($"Object {Objects.Count}");
        Objects.Add(obj);
        Selected = obj;
    }
}
```

`Selected` は、選択が外れたときに `null` になるので、型を `SceneObjectViewModel?` にしました。`HasSelection` は、このあと画面の表示と非表示の切り替えに使います。`Selected` が変わったときに、`HasSelection` も変わったと知らせているのが、`RaisePropertyChanged(nameof(HasSelection))` の行です。

画面は、第 6 章で「シーン ツリー」という文字だけを置いた、左のパネルを差し替えます。

```xml title="MainWindow.xaml（変更：左のパネル）"
<DockPanel Grid.Column="0" Background="#FF252526">
    <Button DockPanel.Dock="Bottom" Content="オブジェクトを追加" Margin="8"
            Command="{Binding AddCommand}" />
    <ListBox ItemsSource="{Binding Objects}"
             SelectedItem="{Binding Selected}"
             Background="Transparent" BorderThickness="0" Foreground="White"
             DisplayMemberPath="Name" />
</DockPanel>
```

実行すると、`Camera`、`Cube`、`Light` が並びます。クリックすると、右のパネルの中身が選んだオブジェクトに切り替わります。名前の入力欄に文字を打つと、左のリストの名前も同時に変わります。「オブジェクトを追加」を押すと、行が増えて、その行が選ばれます。

### 深掘り：ObservableCollection

リストに要素を足したり消したりしたときも、画面へ知らせる必要があります。`List<T>` は何も知らせないので、`ObservableCollection<T>` を使います。要素の追加と削除が、そのまま画面に反映されます。

ひとつ注意があります。`Objects = new ObservableCollection<...>(...)` のように、入れ物ごと差し替えると、`ObservableCollection` の通知では足りません。そのプロパティ自体の `PropertyChanged` が必要です。普段は入れ物を作り替えず、`Clear()` と `Add()` で中身を変えるほうが安全です。上の `Objects` が、`{ get; }` だけで `set` を持たないのは、そのためです。

`ItemsSource` は、リスト系の部品に「要素の集まり」を渡すプロパティです。`SelectedItem` は、選んでいる 1 件で、`ListBox` の側で選び直すと `Selected` に書き戻されます。第 16 章で詳しく扱います。

### 深掘り：項目の見た目（DataTemplate）

`DisplayMemberPath="Name"` は、「各要素の `Name` を文字で出す」だけの簡単な指定です。名前と位置を並べたいときは、`DataTemplate` で、1 件ごとの見た目を決めます。

```xml title="MainWindow.xaml（変更：ListBox の中身）"
<ListBox ItemsSource="{Binding Objects}"
         SelectedItem="{Binding Selected}"
         Background="Transparent" BorderThickness="0" Foreground="White">
    <ListBox.ItemTemplate>
        <DataTemplate>
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="{Binding Name}" FontWeight="Bold" />
                <TextBlock Text="{Binding X, StringFormat=X: {0:F1}}"
                           Foreground="Gray" Margin="8,0,0,0" />
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

大事なのは、`DataTemplate` の中では、`DataContext` が「リストの 1 要素」になることです。だから `{Binding Name}` は、各要素の `Name` を指します。ウィンドウ全体のビューモデルの `Name` ではありません。迷ったら、`DataTemplate` の中なら 1 要素、それ以外なら親から引き継いだもの、と考えれば追えます。

右のパネルで位置を書き換えて、フォーカスを外すと、左のリストの `X:` も変わります。`SceneObjectViewModel` が通知を出しているので、リストの 1 行ごとに、バインディングが生きているのです。

## 何も選ばれていないときは隠す

ここまでで `Selected` が `null` になる場面はありませんが、あとの章で選択の解除が入ります。そのとき右のパネルが空の入力欄だけで残ると不格好なので、先に表示と非表示を切り替えておきます。

```xml title="MainWindow.xaml（変更：リソースを足す）"
<Window.Resources>
    <BooleanToVisibilityConverter x:Key="BoolToVisibility" />
</Window.Resources>
```

```xml title="MainWindow.xaml（変更：右のパネルの StackPanel）"
<StackPanel Visibility="{Binding HasSelection, Converter={StaticResource BoolToVisibility}}">
    <!-- 中身は前のとおり -->
</StackPanel>
```

`HasSelection` は `bool` ですが、`Visibility` に入れられるのは `Visible`、`Hidden`、`Collapsed` の 3 つのどれかです。型が違う 2 つをつなぐのが、`Converter` です。WPF には、`bool` と `Visibility` を変換する `BooleanToVisibilityConverter` が、最初から入っています。

### 深掘り：値の変換（IValueConverter）

標準の変換では足りないときは、自分で書きます。中身の仕組みを見るために、同じ変換を書いてみます。この `BoolToVisibilityConverter` は、仕組みを知るための実験で、`Editor` には入れません。

```csharp title="実験：IValueConverter の中身（Editor には入れない）"
using System.Globalization;
using System.Windows.Data;

public class BoolToVisibilityConverter : IValueConverter
{
    public object Convert(object value, Type targetType, object parameter, CultureInfo culture)
        => value is true ? Visibility.Visible : Visibility.Collapsed;

    public object ConvertBack(object value, Type targetType, object parameter, CultureInfo culture)
        => value is Visibility.Visible;
}
```

`Convert` がデータから画面へ、`ConvertBack` が画面からデータへの変換です。リソースに登録して名前で呼ぶ形は、標準のものと同じです。

`Visibility` の 3 つの値は、`Visible` が見える、`Hidden` が見えないが場所は残る、`Collapsed` が見えず場所も詰まる、です。パネルを丸ごと隠すときは、レイアウトが空かないように `Collapsed` を使います。

## MVVM という考え方

ここまでに作ったものを、役割で整理します。

| 役割 | 呼び方 | この教材では |
| --- | --- | --- |
| データとその操作 | ViewModel（ビューモデル） | `MainWindowViewModel`、`SceneObjectViewModel` |
| 画面 | View（ビュー） | `MainWindow.xaml` |
| 本来のデータ・ロジック | Model（モデル） | エンジン側、あとで作る `SceneDocument` など |

ビューは、ビューモデルのプロパティを見るだけです。ビューモデルは、ビューを知りません。この一方通行のおかげで、画面を作り替えてもロジックは壊れず、ビューモデルを画面なしでテストすることもできます。

```text
View（MainWindow.xaml）            ViewModel（C#）
  TextBox.Text  ────Binding────▶   SceneObjectViewModel.X  （INotifyPropertyChanged）
  Button.Command ───Binding────▶   ResetCommand            （ICommand）
  ListBox.ItemsSource ─────────▶   Objects                 （ObservableCollection）
                                    │ 使う
                                    ▼
                                  Model（エンジン、ドキュメント）
```

今の `SceneObjectViewModel` は、データそのものも持っています。まだエンジンにつながっていないので、ビューモデルがモデルを兼ねていますが、第 40 章でエンジンのシーンとつなぐときに、データ側を切り出します。

「このコードはどこに書けばよいか」で迷ったときの目安も、書いておきます。

| こういう処理は | ここに書く |
| --- | --- |
| 画面に見せる値、入力された値の検証 | ビューモデル |
| ボタンを押したときの処理 | ビューモデル（コマンド） |
| ファイルやエンジンの呼び出し | ビューモデルから、サービス（インターフェース）を通して |
| 見た目だけの話（アニメーション、部品の配置の微調整） | XAML か、ビューのコードビハインド |
| ウィンドウや部品そのものを触る処理（`HwndHost` のイベントを受けるなど） | ビューのコードビハインド（ビューモデルに橋渡しするだけにする） |
| `MessageBox`、ファイル ダイアログ | サービスに包んで、ビューモデルから呼ぶ（第 24 章） |

コードビハインドを絶対に使ってはいけない、という決まりではありません。画面の部品そのものを相手にする処理は、ビューのコードビハインドに書いたほうが素直です。ただしロジックは書かず、ビューモデルへ橋渡しするだけにとどめます。

## 動かして確かめる

`F5` で実行して、次を確かめてください。

- 左に `Camera`、`Cube`、`Light` が並び、`Cube` が選ばれている。
- 別の行を選ぶと、右のパネルの名前と位置が切り替わる。
- 名前を打つと、打つたびに左のリストの名前が変わる。
- 位置を書き換えてフォーカスを外すと、リストの `X:` の数字が変わる。
- 位置がすべて 0 のとき、「位置をリセット」が灰色になる。
- 「オブジェクトを追加」で行が増え、増えた行が選ばれる。

??? failure "右のパネルが空のまま、何も出ない"
    `MainWindow.xaml` に `AutoWireViewModel="True"` が書いてあるか（第 12 章）、「出力」ウィンドウに `BindingExpression path error` が出ていないかを確かめます。`MainWindowViewModel` の `Selected` が `public` のプロパティになっているかも見てください。

??? failure "位置を書き換えても、左のリストの数字が変わらない"
    `SceneObjectViewModel` が `BindableBase` を継承して、`SetProperty` を使っているかを確かめます。フォーカスが外れるまで反映されないのは、故障ではなく `TextBox` の既定の動きです。

??? failure "リセットを押しても、ボタンの状態が戻らない"
    `ResetCommand` に、`.ObservesProperty(() => X)` などが付いているかを確かめます。

## ここまでの Editor

```text
Editor/
├─ Scene/
│   └─ SceneObjectViewModel.cs   1 オブジェクト（名前、位置、リセット）。BindableBase
├─ MainWindowViewModel.cs        一覧と選択。BindableBase、DelegateCommand
└─ MainWindow.xaml               左：シーン ツリー、右：プロパティ
```

## ここまでのまとめ

- `DataContext` に入れたオブジェクトを、`{Binding プロパティ名}` が見に行く。
- 画面が追従するには、`INotifyPropertyChanged`（プロパティ）と `ObservableCollection`（コレクション）で変更を知らせる。プロパティは Prism の `BindableBase` と `SetProperty` で書く。
- 操作は `ICommand`（Prism の `DelegateCommand`）、リストの 1 件の見た目は `DataTemplate`、型の違いは `Converter` でつなぐ。
- 画面で困ったら、「出力」ウィンドウの `BindingExpression path error` を見る。

## 関連する章

- [第 15 章 バインディングを掘り下げる](15-binding.md)：Mode と UpdateSourceTrigger の既定値、ElementName、RelativeSource、MultiBinding、入力検証、デバッグ
- [第 16 章 リストとデータ表示](16-lists.md)：ListBox / ListView / DataGrid / ComboBox の使い分けと選択
- [第 28 章 コードビハインドを減らす](28-behaviors.md)：Behaviors でイベントをコマンドに結ぶ
- [第 26 章 MVVM ライブラリを比べる](26-mvvm-libraries.md)：`BindableBase` と CommunityToolkit.Mvvm、ReactiveProperty の書き比べ

次の章では、バインディングの設定を細かく見ていきます。「更新されない」の原因の多くは、ここにあります。

[第 15 章 バインディングを掘り下げる](15-binding.md) へ進みます。

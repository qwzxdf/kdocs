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
    - [第 12 章 Prism の導入と起動の流れ](12-prism-bootstrap.md)（ViewModelLocator が、ビューモデルを `DataContext` に入れる流れ。NuGet の入れ方も同じ）
    - [第 6 章 WPF プロジェクトと XAML](06-wpf-xaml.md)（この章は、そこで作った `MainWindow.xaml` を書き換えていく）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Scene/SceneObjectViewModel.cs`（新規） | シーンの 1 オブジェクト（名前と位置） |
    | `MainWindowViewModel.cs`（変更） | オブジェクトの一覧と、選択中のオブジェクト |
    | `MainWindow.xaml`（変更） | 左にシーン ツリー、右にプロパティ パネルを作る |

    値の変化を画面に知らせる仕組みと、ボタンの処理には、NuGet の ReactiveProperty を使います。自分では書きません。そのかわり、中でどんなことが起きているのかは、「深掘り」の節で見ます。

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

### ReactiveProperty で包む

とはいえ、プロパティごとにこの 10 行を書くのは大変です。オブジェクトの名前と位置だけで 4 つ、これから増えていく他のビューモデルを含めると、数十個になります。

定番の逃げ道は 2 つあります。共通の部分を基底クラスに移す方法と（Prism の `BindableBase`、CommunityToolkit.Mvvm の `ObservableObject`）、プロパティそのものを「値を包んだ部品」に替える方法です。この教材は、後者の ReactiveProperty を基本にします。理由は 3 つあります。

1 つ目は、通知の定型コードが、書く場所ごとなくなることです。`SetProperty` も、フィールドも、`set` の中身もありません。

2 つ目は、別のプロパティから計算するプロパティを、「何から作られるか」の宣言で書けることです。「選択があるか」や「リセットを押せるか」は、この章の後半で出てきます。基底クラスの方式だと、元のプロパティの `set` に通知を足して回ることになり、足し忘れが起きます。

3 つ目は、ビューモデルに基底クラスがいらないことです。Prism の機能（ViewModelLocator、リージョン、ダイアログ）と、そのまま組み合わせられます。

そのかわり、XAML のバインディングに `.Value` が付きます。これは第 26 章で、他のやり方と並べて比べます。

NuGet で `ReactiveProperty` を入れます（第 12 章の Prism と同じ手順です）。安定版の 9.x を選んでください。

```csharp title="Scene/SceneObjectViewModel.cs（変更：全体）"
using Reactive.Bindings;

namespace Editor.Scene;

public class SceneObjectViewModel
{
    public SceneObjectViewModel(string name, float x = 0, float y = 0, float z = 0)
    {
        Name = new ReactivePropertySlim<string>(name);
        X = new ReactivePropertySlim<float>(x);
        Y = new ReactivePropertySlim<float>(y);
        Z = new ReactivePropertySlim<float>(z);
    }

    public ReactivePropertySlim<string> Name { get; }
    public ReactivePropertySlim<float> X { get; }
    public ReactivePropertySlim<float> Y { get; }
    public ReactivePropertySlim<float> Z { get; }

    public void Reset()
    {
        X.Value = 0;
        Y.Value = 0;
        Z.Value = 0;
    }
}
```

`ReactivePropertySlim<float>` は、`float` の値を 1 つ持つ小さなオブジェクトです。プロパティは `{ get; }` だけで、あとから差し替えません。値が変わるのは、`ReactivePropertySlim` の中身のほうです。値の読み書きは `.Value` で行います。

```csharp
X.Value = 5;           // 書く。変わったときだけ、画面へ知らせる
float x = X.Value;     // 読む
```

`.Value` に代入すると、前の値と比べて、違うときだけ通知が出ます。さきほど手で書いた `if (_x == value) return;` から `OnPropertyChanged()` までを、`ReactivePropertySlim` が自分の中でやっています。

中身は、次のような形です。実物はもう少し細かいのですが、働きは同じです。

```csharp title="ReactivePropertySlim の中身（イメージ。Editor には入れない）"
public class ReactivePropertySlim<T> : INotifyPropertyChanged, IObservable<T>
{
    private T _value;
    public event PropertyChangedEventHandler? PropertyChanged;

    public T Value
    {
        get => _value;
        set
        {
            if (EqualityComparer<T>.Default.Equals(_value, value)) return;
            _value = value;
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(nameof(Value)));
            // 購読している人にも、新しい値を流す（あとで出てきます）
        }
    }
}
```

`INotifyPropertyChanged` を実装しているのは、ビューモデルではなく、値を包んだ側です。通知される名前は、いつも `Value` です。だから XAML は、`X` ではなく `X.Value` を読みます。

画面の側も、`.Value` を付けて書き直します。

```xml title="MainWindow.xaml（変更：右のパネル）"
<TextBlock Text="名前" Foreground="Gray" Margin="0,8,0,0" />
<TextBox Text="{Binding Selected.Name.Value}" />

<TextBlock Text="位置" Foreground="Gray" Margin="0,8,0,0" />
<TextBox Text="{Binding Selected.X.Value}" />
<TextBox Text="{Binding Selected.Y.Value}" Margin="0,4,0,0" />
<TextBox Text="{Binding Selected.Z.Value}" Margin="0,4,0,0" />
```

`{Binding Selected.X.Value}` は、`DataContext` の `Selected` の、`X` の、`Value`、とたどります。`.Value` を書き忘れても、エラーにはなりません。`TextBox` には `ReactivePropertySlim` という型名の文字が出ます。バインディングは、パスの最後のプロパティを読むだけだからです。

`MainWindowViewModel` の `Selected` も、同じように包みます。ここは、次の節（コマンド）のあとで、まとめて直します。

もう一度実行して「位置をリセット」を押すと、入力欄が 0 になります。

### 深掘り：ReactivePropertySlim と ReactiveProperty

ReactiveProperty には、似た型が 2 つあります。

`ReactivePropertySlim<T>` は軽いほうで、この章ではこちらを使います。値と変更通知と、値の流れ（`IObservable<T>`）だけを持ちます。値を別のスレッドから変えると、そのスレッドで通知を出します。

`ReactiveProperty<T>` は、入力の検証と、UI スレッドへの自動の切り替えが付いたほうです。第 15 章で、検証の必要な入力欄に使います。

迷ったら `ReactivePropertySlim<T>` から始めて、検証が要るプロパティだけ替えます。

### 深掘り：「流れ」としての値

ReactiveProperty の値は、`IObservable<T>`、つまり「値が変わるたびに流れてくる列」としても読めます。

```csharp
X.Subscribe(v => System.Diagnostics.Debug.WriteLine($"X が {v} に変わった"));
```

`Subscribe` は、値が変わるたびに呼ばれる関数を登録します。登録した時点の現在の値でも、すぐ 1 回呼ばれます。これは「最初の表示を整える処理を、別に書かなくてよい」ための動きです。変わったときだけ呼ばれると思っていると、起動直後に動いて驚くので、覚えておいてください。

「流れ」は、`Select` で形を変えたり、`CombineLatest` で複数をまとめたりできます。この章の後半で、「押せる条件」や「選択があるか」を作るのに使います。

### 画面が古いままのときのチェックリスト

バインディングは、間違えても例外が出ません。静かに何も表示されないだけです。症状別に、確認する順番を決めておくと便利です。

画面に何も出ないとき。

1. `{Binding ...}` のプロパティ名のつづりを確かめる。`Massage` と `Message` のような 1 文字違いが定番です。
2. そのプロパティが `public` で、フィールドではなく `{ get; set; }` のプロパティになっているか。WPF のバインディングは、フィールドを見ません。
3. `DataContext` が設定されているか。設定した対象は、その部品の親の位置か。
4. Visual Studio の「出力」ウィンドウに `BindingExpression path error` が出ていないか。バインディングの失敗はここにだけ書かれます。

値は出るのに、変えても画面が追従しないとき。

1. プロパティが、`INotifyPropertyChanged` を実装した型か（ReactiveProperty なら、`ReactivePropertySlim<T>` になっているか）。
2. ReactiveProperty のとき、XAML が `.Value` まで書かれているか。値を書き換えるコードも、`X = 0` ではなく `X.Value = 0` になっているか。
3. 手で書いたプロパティなら、`set` の中で `PropertyChanged` を起こしているか。名前は合っているか。
4. コレクションなら、`List<T>` ではなく `ObservableCollection<T>` か（あとで使います）。

入力しても、すぐにデータへ反映されないとき。

- `TextBox` の `Text` は、入力欄からフォーカスが外れたときに初めてデータへ反映されます。次の節で扱います。

## 入力のたびに反映する

名前の `TextBox` に文字を打っても、フォーカスを外すまでは `Name` が変わりません。あとで、シーン ツリーに名前を出すようにすると、打っている最中に反映されたほうが気持ちがよいので、設定を足します。

```xml title="MainWindow.xaml（変更：名前の入力欄）"
<TextBox Text="{Binding Selected.Name.Value, UpdateSourceTrigger=PropertyChanged}" />
```

位置の入力欄は、このままにします。理由は、深掘りで説明します。

### 深掘り：`{Binding}` の設定

`{Binding}` には、いくつかの設定を足せます。

```xml
<TextBox Text="{Binding Selected.Name.Value, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}" />
<TextBlock Text="{Binding Selected.X.Value, StringFormat=X: {0:F2}}" />
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

コマンドを作る部品は、ReactiveProperty の `ReactiveCommand` を使います。「押してよいか」を、`bool` の流れで渡して作ります。

使うのは `SceneObjectViewModel` です。リセットは、すでに原点にいるときは押せなくしたいので、`X`、`Y`、`Z` をまとめた「どれかが 0 以外か」の流れを作ります。

```csharp title="Scene/SceneObjectViewModel.cs（変更）"
using System.Reactive.Linq;
using Reactive.Bindings;

public SceneObjectViewModel(string name, float x = 0, float y = 0, float z = 0)
{
    Name = new ReactivePropertySlim<string>(name);
    X = new ReactivePropertySlim<float>(x);
    Y = new ReactivePropertySlim<float>(y);
    Z = new ReactivePropertySlim<float>(z);

    // X、Y、Z のどれかが変わるたびに、「どれかが 0 以外か」を流す
    ResetCommand = X.CombineLatest(Y, Z, (px, py, pz) => px != 0 || py != 0 || pz != 0)
        .ToReactiveCommand()
        .WithSubscribe(Reset);
}

public ReactiveCommand ResetCommand { get; }

private void Reset()
{
    X.Value = 0;
    Y.Value = 0;
    Z.Value = 0;
}
```

`CombineLatest` は、3 つの流れのどれかに新しい値が来るたびに、そのときの最新の 3 つの値で、関数を呼び直します。ここでは、どれかが 0 以外なら `true` を流します。

`ToReactiveCommand()` は、その `bool` の流れを「押してよいか」として使う、コマンドを作ります。流れに `true` が来ればボタンが有効に、`false` が来れば無効になります。Prism の `DelegateCommand` では、`ObservesProperty(() => X)` を 3 回書いて、プロパティごとに見張りを付けていました。ReactiveProperty では、「何から押せるかが決まるか」を、1 本の式で書きます。

`WithSubscribe(Reset)` は、ボタンが押されたときの処理を登録して、コマンドそのものを返します。`ResetCommand` に代入するのは、そのコマンドです。

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

`CanExecuteChanged` は、「実行してよいかどうかが変わったかもしれないので、もう一度聞き直してください」という合図です。プロパティの `PropertyChanged` と同じ役割で、これが起きないと、ボタンの状態が更新されません。手で書く方式では、この合図を出す関数（Prism の `DelegateCommand` なら `RaiseCanExecuteChanged()`）を、自分で呼びます。呼び忘れるとボタンの状態が古いままになります。`ReactiveCommand` は、`bool` の流れに新しい値が来るたびに、この合図を自分で出します。

`ReactiveCommand` は、`ICommand` を実装していて、`Execute` で登録された処理を呼び、`CanExecute` で最新の `bool` を返します。自分で `ICommand` を実装するときも、コンストラクターで受け取った関数を `Execute` と `CanExecute` から呼ぶだけの形になります。ボタンの有効、無効は、UI スレッドで更新されます。

## シーン ツリーを作る

右のパネルが動いたので、左のシーン ツリーに、オブジェクトを並べます。複数のオブジェクトを持つ `MainWindowViewModel` に書き直します。

```csharp title="MainWindowViewModel.cs（変更：全体）"
using System.Collections.ObjectModel;
using System.Reactive.Linq;
using Reactive.Bindings;
using Editor.Scene;

namespace Editor;

public class MainWindowViewModel
{
    public MainWindowViewModel()
    {
        Objects = new ObservableCollection<SceneObjectViewModel>
        {
            new("Camera", 0, 2, -5),
            new("Cube", 1, 0, 2),
            new("Light", 3, 5, 0),
        };
        Selected = new ReactivePropertySlim<SceneObjectViewModel?>(Objects[1]);

        // 選択があるかどうか。Selected が変わるたびに、作り直される
        HasSelection = Selected.Select(s => s is not null)
            .ToReadOnlyReactivePropertySlim();

        AddCommand = new ReactiveCommand().WithSubscribe(Add);
    }

    public string Title => "MiniEngine Editor";

    public ObservableCollection<SceneObjectViewModel> Objects { get; }

    public ReactivePropertySlim<SceneObjectViewModel?> Selected { get; }

    public ReadOnlyReactivePropertySlim<bool> HasSelection { get; }

    public ReactiveCommand AddCommand { get; }

    private void Add()
    {
        var obj = new SceneObjectViewModel($"Object {Objects.Count}");
        Objects.Add(obj);
        Selected.Value = obj;
    }
}
```

`Selected` は、選択が外れたときに `null` になるので、型を `SceneObjectViewModel?` にしました。それを `ReactivePropertySlim` で包んでいるので、`Selected.Value` が選ばれているオブジェクトです。

`HasSelection` は、このあと画面の表示と非表示の切り替えに使います。`Selected.Select(s => s is not null)` は、`Selected` が変わるたびに、「選ばれているか」の `bool` を流します。`ToReadOnlyReactivePropertySlim()` は、その流れを、読み取り専用のプロパティに変えます。画面には、`HasSelection.Value` で出ます。

`Selected` を包んだので、右のパネルのバインディングも、`Selected` のあとに `.Value` を足して、選ばれているオブジェクトまでたどります。

```xml title="MainWindow.xaml（変更：右のパネル）"
<TextBox Text="{Binding Selected.Value.Name.Value, UpdateSourceTrigger=PropertyChanged}" />
<TextBox Text="{Binding Selected.Value.X.Value}" />
<TextBox Text="{Binding Selected.Value.Y.Value}" Margin="0,4,0,0" />
<TextBox Text="{Binding Selected.Value.Z.Value}" Margin="0,4,0,0" />
<Button Content="位置をリセット" Margin="0,12,0,0"
        Command="{Binding Selected.Value.ResetCommand}" />
```

`Value` が 2 回出てくるのは、1 回目が「選ばれているオブジェクトを取り出す」、2 回目が「そのオブジェクトの `Name` の値を取り出す」だからです。読みにくいと感じるのは自然です。`Value` が付く段数は、包んだ部品が入れ子になった数だけ増えます。

`HasSelection` に、`set` も `RaisePropertyChanged` もありません。「何から作られるか」だけが書いてあって、`Selected` が変わったら自動で変わります。基底クラスの方式では、`Selected` の `set` の中に `RaisePropertyChanged(nameof(HasSelection))` を書き足すことになり、足し忘れがバグになります。

`Title` は、最初から最後まで変わらない値なので、包まずに普通のプロパティのままにしました。変わらない値は、通知がいりません。

画面は、第 6 章で「シーン ツリー」という文字だけを置いた、左のパネルを差し替えます。

```xml title="MainWindow.xaml（変更：左のパネル）"
<DockPanel Grid.Column="0" Background="#FF252526">
    <Button DockPanel.Dock="Bottom" Content="オブジェクトを追加" Margin="8"
            Command="{Binding AddCommand}" />
    <ListBox ItemsSource="{Binding Objects}"
             SelectedItem="{Binding Selected.Value}"
             Background="Transparent" BorderThickness="0" Foreground="White"
             DisplayMemberPath="Name.Value" />
</DockPanel>
```

実行すると、`Camera`、`Cube`、`Light` が並びます。クリックすると、右のパネルの中身が選んだオブジェクトに切り替わります。名前の入力欄に文字を打つと、左のリストの名前も同時に変わります。「オブジェクトを追加」を押すと、行が増えて、その行が選ばれます。

### 深掘り：ObservableCollection

リストに要素を足したり消したりしたときも、画面へ知らせる必要があります。`List<T>` は何も知らせないので、`ObservableCollection<T>` を使います。要素の追加と削除が、そのまま画面に反映されます。

ひとつ注意があります。`Objects = new ObservableCollection<...>(...)` のように、入れ物ごと差し替えると、`ObservableCollection` の通知では足りません。そのプロパティ自体の `PropertyChanged` が必要です。普段は入れ物を作り替えず、`Clear()` と `Add()` で中身を変えるほうが安全です。上の `Objects` が、`{ get; }` だけで `set` を持たないのは、そのためです。

`ItemsSource` は、リスト系の部品に「要素の集まり」を渡すプロパティです。`SelectedItem` は、選んでいる 1 件で、`ListBox` の側で選び直すと `Selected.Value` に書き戻されます。第 16 章で詳しく扱います。

### 深掘り：項目の見た目（DataTemplate）

`DisplayMemberPath="Name"` は、「各要素の `Name` を文字で出す」だけの簡単な指定です。名前と位置を並べたいときは、`DataTemplate` で、1 件ごとの見た目を決めます。

```xml title="MainWindow.xaml（変更：ListBox の中身）"
<ListBox ItemsSource="{Binding Objects}"
         SelectedItem="{Binding Selected.Value}"
         Background="Transparent" BorderThickness="0" Foreground="White">
    <ListBox.ItemTemplate>
        <DataTemplate>
            <StackPanel Orientation="Horizontal">
                <TextBlock Text="{Binding Name.Value}" FontWeight="Bold" />
                <TextBlock Text="{Binding X.Value, StringFormat=X: {0:F1}}"
                           Foreground="Gray" Margin="8,0,0,0" />
            </StackPanel>
        </DataTemplate>
    </ListBox.ItemTemplate>
</ListBox>
```

大事なのは、`DataTemplate` の中では、`DataContext` が「リストの 1 要素」になることです。だから `{Binding Name.Value}` は、各要素の `Name` の値を指します。ウィンドウ全体のビューモデルの `Name` ではありません。迷ったら、`DataTemplate` の中なら 1 要素、それ以外なら親から引き継いだもの、と考えれば追えます。

右のパネルで位置を書き換えて、フォーカスを外すと、左のリストの `X:` も変わります。`X` が通知を出しているので、リストの 1 行ごとに、バインディングが生きているのです。

## 何も選ばれていないときは隠す

ここまでで `Selected` が `null` になる場面はありませんが、あとの章で選択の解除が入ります。そのとき右のパネルが空の入力欄だけで残ると不格好なので、先に表示と非表示を切り替えておきます。

```xml title="MainWindow.xaml（変更：リソースを足す）"
<Window.Resources>
    <BooleanToVisibilityConverter x:Key="BoolToVisibility" />
</Window.Resources>
```

```xml title="MainWindow.xaml（変更：右のパネルの StackPanel）"
<StackPanel Visibility="{Binding HasSelection.Value, Converter={StaticResource BoolToVisibility}}">
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
  TextBox.Text  ────Binding────▶   SceneObjectViewModel.X.Value  （ReactivePropertySlim）
  Button.Command ───Binding────▶   ResetCommand            （ReactiveCommand）
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
    `X` が `ReactivePropertySlim<float>` になっていて、XAML が `X.Value` を読んでいるかを確かめます。フォーカスが外れるまで反映されないのは、故障ではなく `TextBox` の既定の動きです。

??? failure "テキスト ボックスに `Reactive.Bindings.ReactivePropertySlim`1[...]` という文字が出る"
    XAML が `{Binding Selected.X}` のように、`.Value` を書いていません。`{Binding Selected.X.Value}` にします。

??? failure "リセットを押しても、ボタンの状態が戻らない"
    `ResetCommand` の元になる `CombineLatest` に、`X`、`Y`、`Z` の 3 つとも入っているかを確かめます。

## ここまでの Editor

```text
Editor/
├─ Scene/
│   └─ SceneObjectViewModel.cs   1 オブジェクト（名前、位置、リセット）。ReactivePropertySlim、ReactiveCommand
├─ MainWindowViewModel.cs        一覧と選択。ReactivePropertySlim、ReactiveCommand
└─ MainWindow.xaml               左：シーン ツリー、右：プロパティ
```

## ここまでのまとめ

- `DataContext` に入れたオブジェクトを、`{Binding プロパティ名}` が見に行く。
- 画面が追従するには、`INotifyPropertyChanged`（プロパティ）と `ObservableCollection`（コレクション）で変更を知らせる。プロパティは ReactiveProperty の `ReactivePropertySlim<T>` で包んで書き、XAML は `.Value` まで読む。
- 別のプロパティから計算する値は、`Select` や `CombineLatest` で「何から作られるか」を宣言して、`ToReadOnlyReactivePropertySlim()` で包む。
- 操作は `ICommand`（`ReactiveCommand`）、リストの 1 件の見た目は `DataTemplate`、型の違いは `Converter` でつなぐ。
- 画面で困ったら、「出力」ウィンドウの `BindingExpression path error` を見る。

## 関連する章

- [第 15 章 バインディングを掘り下げる](15-binding.md)：Mode と UpdateSourceTrigger の既定値、ElementName、RelativeSource、MultiBinding、入力検証、デバッグ
- [第 16 章 リストとデータ表示](16-lists.md)：ListBox / ListView / DataGrid / ComboBox の使い分けと選択
- [第 28 章 コードビハインドを減らす](28-behaviors.md)：Behaviors でイベントをコマンドに結ぶ
- [第 26 章 MVVM ライブラリを比べる](26-mvvm-libraries.md)：ReactiveProperty と、Prism の `BindableBase`、CommunityToolkit.Mvvm の書き比べ

次の章では、バインディングの設定を細かく見ていきます。「更新されない」の原因の多くは、ここにあります。

[第 15 章 バインディングを掘り下げる](15-binding.md) へ進みます。

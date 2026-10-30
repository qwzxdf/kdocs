---
title: 第 26 章 MVVM ライブラリを比べる
tags:
  - C#連携
---

# 第 26 章 MVVM ライブラリを比べる

この教材では、ビューモデルの書き方に ReactiveProperty（`ReactivePropertySlim<T>` と `ReactiveCommand`）を使っています（第 14 章）。アプリの構造には Prism を使います。ただ、WPF の解説記事を探すと、Prism の `BindableBase`、CommunityToolkit.Mvvm、Livet など、別のライブラリを使った記事のほうがたくさん見つかります。「自分はどれを使えばいいのか」「他の記事のコードを ReactiveProperty に読み替えるにはどうするのか」がすぐ分かるように、この章で並べて比べます。

!!! info "このページを読む前に"
    - [第 25 章 Prism を掘り下げる](25-prism-deep.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章での Editor"
    この章では、Editor にファイルを足しません。Editor の `SceneObjectViewModel`（名前と位置 X、リセット ボタン）を題材にして、3 つの書き方を比べます。

## 何を提供するライブラリなのか

先に整理しておくと、MVVM を支えるライブラリは、2 種類の仕事に分かれます。

| 仕事 | 内容 | 代表 |
| --- | --- | --- |
| ① ビューモデルを書きやすくする | `INotifyPropertyChanged` の実装、コマンド、検証、メッセージ | CommunityToolkit.Mvvm、Prism（`BindableBase`）、ReactiveProperty、Livet |
| ② アプリの構造を作る | 画面の枠（リージョン）、モジュール、ナビゲーション、ダイアログ、DI | Prism |

Prism は①と②の両方を持っています。CommunityToolkit.Mvvm は①だけです。アプリの構造（②）が要るなら、Prism か、別の DI ライブラリ（`Microsoft.Extensions.DependencyInjection` など）と組み合わせた自作になります。

## 同じ画面を 3 通りで書く

第 14〜17 章で作った `SceneObjectViewModel` の、名前と位置 X、リセット コマンドだけを取り出して、3 つの書き方で並べます。この教材の書き方（ReactiveProperty）は、このあとの「ReactiveProperty を詳しく」でまとめて説明します。先に、他の 2 つを見ます。

### Prism の BindableBase

```csharp title="実験：Prism の BindableBase で書くと（Editor には入れない）"
public class SceneObjectViewModel : BindableBase
{
    private string _name = "";
    private float _x;

    public string Name
    {
        get => _name;
        set => SetProperty(ref _name, value);
    }

    public float X
    {
        get => _x;
        set => SetProperty(ref _x, value);
    }

    public DelegateCommand ResetCommand { get; }

    public SceneObjectViewModel()
    {
        ResetCommand = new DelegateCommand(() => X = 0, () => X != 0)
            .ObservesProperty(() => X);
    }
}
```

### CommunityToolkit.Mvvm

```csharp title="実験：CommunityToolkit.Mvvm で書くと（Editor には入れない）"
public partial class SceneObjectViewModel : ObservableObject
{
    [ObservableProperty]
    private string _name = "";

    [ObservableProperty]
    [NotifyCanExecuteChangedFor(nameof(ResetCommand))]
    private float _x;

    [RelayCommand(CanExecute = nameof(CanReset))]
    private void Reset() => X = 0;

    private bool CanReset() => X != 0;
}
```

こちらは、ソース ジェネレーターという仕組みで、`[ObservableProperty]` を付けたフィールドから、`Name` というプロパティと変更通知のコードをコンパイル時に自動で生成します。`[RelayCommand]` は、メソッドから `HealCommand` を生成します。ルールは次のとおりです。

- クラスに `partial` を付ける。付けないと、ジェネレーターがエラーを出す。
- フィールド名は `_name`、`name`、`m_name` のように書くと、`Name` というプロパティが生成される。
- `[RelayCommand]` のメソッド名の末尾に `Command` が付いた名前で、コマンドが生成される（`Heal` → `HealCommand`）。`OnXxx` という名前なら、`On` が取れる。
- 非同期のメソッド（`async Task`）に付けると、`AsyncRelayCommand` が生成される。

書く量は、確かにかなり減ります。一方で、生成されたコードは見えないので、動作を追いにくいと感じる人もいます（Visual Studio の「解決策エクスプローラー → 依存関係 → アナライザー」で、生成コードを開けます）。

### ReactiveProperty（この教材の書き方）

```csharp title="Editor の書き方（第 14 章）"
public class SceneObjectViewModel
{
    public ReactivePropertySlim<string> Name { get; } = new("");
    public ReactivePropertySlim<float> X { get; } = new(0);
    public ReactiveCommand ResetCommand { get; }

    public SceneObjectViewModel()
    {
        ResetCommand = X.Select(x => x != 0)
            .ToReactiveCommand()
            .WithSubscribe(() => X.Value = 0);
    }
}
```

値を `ReactiveProperty<T>` で包み、Rx（Reactive Extensions）の演算子で組み合わせる書き方です。値の変化を「流れ」として扱えるので、「入力が変わったら 300 ミリ秒待って、検索する」のような処理を宣言的に書けます。ただし、Rx の考え方を学ぶ必要があります。

## どれを選ぶか

| 状況 | 目安 |
| --- | --- |
| 画面が少なく、MVVM の補助だけがほしい | CommunityToolkit.Mvvm（軽くて、情報が多い）か、ReactiveProperty |
| 画面が増え、リージョンやモジュールで部品に分けたい | Prism |
| 非同期の流れや、入力の連動を宣言的に書きたい | ReactiveProperty（+ 他と併用） |
| 小規模で、とにかく依存を増やしたくない | ライブラリなし（`INotifyPropertyChanged` と自作の `RelayCommand`） |

この教材は、リージョンとモジュールを使う前提なので、構造には Prism を選んでいます。ビューモデルの書き方は ReactiveProperty です。ReactiveProperty は基底クラスを要求しないので、Prism の ViewModelLocator やダイアログと、そのまま組み合わせられます。Prism は MVVM の補助部分を別のライブラリに替えられる設計です。`BindableBase` の代わりに CommunityToolkit.Mvvm の `ObservableObject` を使う、という組み合わせもできます。

## 書き換えの対応表

他のライブラリで書かれた記事を読むときの、対応表です。

| やりたいこと | ReactiveProperty（この教材） | Prism | CommunityToolkit.Mvvm |
| --- | --- | --- | --- |
| 通知付きプロパティ | `ReactivePropertySlim<T>`（`.Value`） | `SetProperty(ref _x, value)` | `[ObservableProperty]` または `SetProperty(ref _x, value)` |
| 基底クラス | なし | `BindableBase` | `ObservableObject` |
| コマンド | `ReactiveCommand` | `DelegateCommand` | `RelayCommand`（`[RelayCommand]`） |
| 非同期コマンド | `AsyncReactiveCommand` | なし（自作する） | `AsyncRelayCommand` |
| 条件が変わったら再判定 | 条件の `IObservable<bool>` から `ToReactiveCommand()` | `.ObservesProperty(() => X)` | `[NotifyCanExecuteChangedFor(...)]` |
| 値が変わったときの処理 | `X.Subscribe(...)` | `SetProperty(ref _x, value, OnChanged)` | `partial void OnXxxChanged(T value)` |
| 別の値から計算する値 | `Select` と `ToReadOnlyReactivePropertySlim()` | `RaisePropertyChanged(nameof(...))` を元の `set` に足す | `[NotifyPropertyChangedFor(...)]` |
| メッセージの送受信 | `IEventAggregator`（Prism） | `IEventAggregator` | `WeakReferenceMessenger`（`ObservableRecipient`） |
| 入力の検証 | `ReactiveProperty<T>` の `SetValidateNotifyError` | `ErrorsContainer<T>` | `ObservableValidator`（`[Required]`、`[Range]` など） |

`WeakReferenceMessenger` の「Weak（弱い）」は、弱参照のことです。ふつうの参照は、持っている間は相手を GC に片付けさせません。メッセージの受け手を強い参照で登録すると、画面を閉じても登録が残って、受け手が解放されません（C++ で `shared_ptr` を持ち合って解放されないのと同じ種類の問題です）。弱参照は、持っていても GC を止めない参照なので、受け手が消えたら登録も自然に無効になります。

### 入力の検証を属性で書く（ObservableValidator）

```csharp title="実験：属性で検証する（Editor には入れない）"
public partial class SceneObjectViewModel : ObservableValidator
{
    [ObservableProperty]
    [NotifyDataErrorInfo]
    [Required(ErrorMessage = "名前を入力してください")]
    private string _name = "";
}
```

`INotifyDataErrorInfo`（第 15 章）を実装済みで、`System.ComponentModel.DataAnnotations` の属性で検証規則を書けます。第 15 章で、`Name` の `set` に手で書いた「空なら `SetError`」が、属性 1 行になります。入力検証を多用する画面を作るなら、これは魅力的です。

## ReactiveProperty を詳しく

ここまでの 2 つ（Prism、CommunityToolkit.Mvvm）は、「プロパティを普通に書いて、通知の定型コードを減らす」方向でした。ReactiveProperty は発想が違います。プロパティそのものを、値を包んだ部品に替えます。`SetProperty` を書く場所がなくなるのは、そのためです。そのかわり、XAML の書き方もコマンドの作り方も変わります。何が変わるかを順に見ていきます。

### 値を包む

```csharp title="実験：ReactiveProperty のプロパティ（Editor には入れない）"
using Reactive.Bindings;

public class SceneObjectViewModel
{
    public ReactivePropertySlim<string> Name { get; } = new("");
    public ReactivePropertySlim<float> X { get; } = new(0f);
}
```

`ReactivePropertySlim<float>` は、`float` の値を 1 つ持つ小さなオブジェクトです。値の読み書きは `.Value` で行います。変更通知（`INotifyPropertyChanged`）と、変化を流す `IObservable<T>` を、この部品が自分で実装しています。ビューモデルの側に基底クラスも `SetProperty` も要らないのは、そのためです。プロパティは `{ get; }` だけで、あとから差し替えません。値が変わるのは、`ReactivePropertySlim` の中身です。

XAML は、`.Value` まで書きます。

```xml
<TextBox Text="{Binding Selected.X.Value}" />
```

`{Binding Selected.X}` と書くと、`TextBox` に出るのは `ReactivePropertySlim` という型名の文字です。エラーにならず、黙っておかしな表示になります。バインディングは、パスをたどって最後のプロパティを読むだけだからです。ここで間違えやすいので、後ろの「つまずき」にも書いておきます。

### 2 種類とパッケージ

ReactiveProperty には、よく使う型が 2 つあります。

`ReactivePropertySlim<T>` は軽いほうです。値、変更通知、`IObservable<T>`、それだけを持ちます。スレッドの切り替えや検証の機能はありません。

`ReactiveProperty<T>` は、検証の機能が付いた重いほうです。`SetValidateNotifyError` や `SetValidateAttribute` で入力を検証できて、エラーを `INotifyDataErrorInfo` として画面に出します。

迷ったら、`ReactivePropertySlim<T>` から始めます。検証が要るプロパティだけ `ReactiveProperty<T>` にします。

NuGet のパッケージも分かれています。`ReactiveProperty` は全部入りで、Rx（`System.Reactive`）に依存します。`ReactiveProperty.Core` は `ReactivePropertySlim<T>` と `ReadOnlyReactivePropertySlim<T>` だけの最小版で、`System.Reactive` に依存しません。Rx の演算子（`Select` や `Delay`）を使わず、プロパティの通知だけがほしいなら、Core で足ります。演算子を使うなら、全部入りです。

### 値が変わったときの処理

```csharp
X.Subscribe(v => Console.WriteLine($"X が {v} に変わった"));
```

`Subscribe` は、値が変わるたびに呼ばれる関数を登録します。Prism なら `SetProperty(ref _x, value, OnChanged)` の `OnChanged` にあたります。ただし、`Subscribe` は登録した時点で、現在の値で 1 回呼ばれます。これは `ReactiveProperty` の既定の動作（`RaiseLatestValueOnSubscribe`）で、「最初の表示を整える処理を別に書かなくてよい」という便利さでもあります。「変わったときだけ呼ばれる」と思って書くと、起動直後に動いてしまいます。

同じ値を代入したときは、呼ばれません（`DistinctUntilChanged`）。`ReactiveProperty<T>` では、コンストラクターの `mode` を `ReactivePropertyMode.None` にすると、この 2 つの動作を切れます。

### 別のプロパティから計算する

```csharp
public ReadOnlyReactivePropertySlim<string> Label { get; }

public SceneObjectViewModel()
{
    // Name か X が変わるたびに、文字を作り直す
    Label = Name.CombineLatest(X, (n, x) => $"{n} ({x:F1})")
                .ToReadOnlyReactivePropertySlim()!;
}
```

`CombineLatest` は、2 つの流れのどちらかが変わるたびに、最新の 2 つの値で計算し直します。`ToReadOnlyReactivePropertySlim()` で、その結果を「読み取り専用のプロパティ」に変えます。画面は `{Binding Label.Value}` で読みます。

CommunityToolkit.Mvvm なら、`Name` と `X` の両方に `[NotifyPropertyChangedFor(nameof(Label))]` を付けて回ります。ReactiveProperty では、`Label` の側に「何から作られるか」を 1 か所に書けます。依存元を増やしたときの付け忘れが起きにくい、という違いです。

### コマンド

```csharp
public ReactiveCommand ResetCommand { get; }

public SceneObjectViewModel()
{
    // X が 0 でないときだけ押せるボタン
    ResetCommand = X.Select(x => x != 0f)
                    .ToReactiveCommand()
                    .WithSubscribe(() => X.Value = 0f);
}
```

`Select` で「押せる条件」の流れを作り、`ToReactiveCommand()` でコマンドにします。条件が変わるたびに、ボタンの有効、無効が自動で切り替わります。`WithSubscribe` は、押されたときの処理を登録して、コマンド自身を返します。XAML は、普通のコマンドと同じです。

```xml
<Button Command="{Binding Selected.ResetCommand}" Content="位置をリセット" />
```

Prism の `DelegateCommand` の `ObservesProperty(() => X)` は、使えません。`X` が `ReactivePropertySlim<float>` に替わって、`ObservesProperty` に渡す式の形（プロパティ 1 つ）と合わなくなるからです。ReactiveProperty を使うなら、コマンドも `ReactiveCommand` にそろえるのが素直です。どうしても `DelegateCommand` を残すなら、`X.Subscribe(_ => cmd.RaiseCanExecuteChanged())` で再判定を自分でつなぎます。

### 入力の検証

```csharp
public ReactiveProperty<string> Name { get; }

public SceneObjectViewModel()
{
    Name = new ReactiveProperty<string>("Cube")
        .SetValidateNotifyError(x => string.IsNullOrWhiteSpace(x) ? "名前を入力してください" : null);
}
```

検証の関数は、正しければ `null`、間違っていればエラーのメッセージを返します。第 15 章で `ErrorsContainer` に手で書いた「空なら `SetError`」が、1 行になります。属性で書くなら `SetValidateAttribute(() => Name)` で、`[Required]` などが使えます。

エラーがあるかどうかは、`HasErrors`（現在の値）と `ObserveHasErrors`（流れ）で読めます。複数の入力欄がすべて正しいときだけ押せる保存ボタンは、`ObserveHasErrors` を組み合わせて作ります。

```csharp
SaveCommand = Name.ObserveHasErrors
    .CombineLatest(Path.ObserveHasErrors, (a, b) => !a && !b)
    .ToReactiveCommand();
```

注意が 1 つあります。`ReactiveProperty<T>` は、初期値の検証もすぐ行うので、画面を開いた時点で赤い枠が出ることがあります。初期値のエラーを出したくないときは、コンストラクターの `mode` に `IgnoreInitialValidationError` を足します。

### 後始末

`Subscribe` で登録した関数は、ビューモデルが消えたあとも残ることがあります。登録の戻り値（`IDisposable`）を `CompositeDisposable` に溜めておき、ビューモデルの `Dispose` でまとめて破棄します。

```csharp
private readonly CompositeDisposable _disposables = new();

public SceneObjectViewModel()
{
    X.Subscribe(OnXChanged).AddTo(_disposables);   // 溜める
}

public void Dispose() => _disposables.Dispose();     // まとめて破棄
```

`ReactiveProperty` そのものも `IDisposable` です。画面を開いたり閉じたりするビューモデルは、`Dispose` を呼ぶ仕組みを用意してください（第 51 章の `SubscriptionBag` と同じ考え方です）。

### BindableBase と併用する

ReactiveProperty は基底クラスを要求しないので、`BindableBase` を継承したままでも使えます。ViewModelLocator、リージョン、ダイアログも、これまでと同じです。

ただし、同じクラスの中に、`SetProperty` で書いたプロパティと `ReactivePropertySlim` のプロパティが混ざると、XAML のバインディングが `X` と `X.Value` で不ぞろいになります。1 つのビューモデルの中では、どちらかにそろえるのを勧めます。

### つまずき

??? failure "テキスト ボックスに `ReactivePropertySlim`1[...]` という文字が出る"
    `{Binding X}` と書いています。`{Binding X.Value}` にします。

??? failure "画面を開いた直後に、変更時の処理が動いてしまう"
    `Subscribe` は、登録した時点の現在の値で、すぐ 1 回呼ばれます。初期表示の処理が要らないなら、`.Skip(1)` で最初の 1 回を読み飛ばします。

??? failure "別のスレッドで値を変えたら、画面が更新されない"
    `ReactivePropertySlim` は、値を変えたスレッドで通知を出します。ワーカー スレッドから変えるなら、`ObserveOnDispatcher()` を通した流れを `ToReadOnlyReactivePropertySlim()` にするか、Dispatcher に戻してから代入します（第 17 章）。

### R3 という後継

ReactiveProperty の README は、これから作るアプリには、同じ作者が作り直した **R3** を勧めています。R3 は Rx を軽く作り直したもので、`ReactiveProperty` の考え方を受け継いでいます。今ある資料と事例は ReactiveProperty のほうが多いので、この教材では ReactiveProperty を説明しました。新しく始めるなら、R3 の資料も一度見ておくと安心です。

### Editor に入れるなら

Editor に入れるときは、変更が及ぶ範囲を先に見積もってください。

- `SceneObjectViewModel` のプロパティを `ReactivePropertySlim` にする。
- 画面のバインディングを、すべて `.Value` 付きにする（第 14〜17 章、第 41〜46 章の XAML が対象）。
- `DelegateCommand.ObservesProperty` を、`ReactiveCommand` に替える。
- 第 15 章の `ValidatableViewModelBase` を、`ReactiveProperty<T>` の検証に替える。
- `Subscribe` の後始末（`Dispose`）の置き場所を決める。

変更は広いので、小さなビューモデル 1 つで試してから広げてください。教材は Prism の `BindableBase` のまま進めます。

## Prism と組み合わせる

Prism の DI やリージョンを使いつつ、MVVM の補助部分だけを CommunityToolkit.Mvvm にしたいときは、次のとおりです。

1. `CommunityToolkit.Mvvm` を NuGet で入れる。
2. ビューモデルの基底クラスに `ObservableObject` を使う（`BindableBase` の代わり）。
3. ViewModelLocator（`AutoWireViewModel`）、リージョン、ダイアログ サービスは、そのまま Prism を使う。`INavigationAware` などを実装するのも、これまでと同じ。

基底クラスが違っても、Prism の ViewModelLocator は「`DataContext` に入れる」だけなので、衝突はしません。

## この章のまとめ

- ライブラリは「ビューモデルを書きやすくする」ものと、「アプリの構造を作る」ものに分かれる。Prism は両方、CommunityToolkit.Mvvm は前者だけ。
- CommunityToolkit.Mvvm は、ソース ジェネレーターで書く量を減らす。`partial` を付けるのを忘れない。
- ReactiveProperty は、プロパティを `ReactivePropertySlim<T>` で包む。`SetProperty` は要らないが、XAML は `.Value` 付きになり、コマンドは `ReactiveCommand` にそろえる。
- 他のライブラリの記事を読むときは、対応表で読み替える。
- この教材は、構造は Prism、ビューモデルの書き方は ReactiveProperty。
- 構造（リージョン、モジュール）が要るなら Prism。補助だけなら、CommunityToolkit.Mvvm で十分。

次の章では、部品を使い回すための `UserControl` と、カスタム コントロールの作り方を説明します。

[第 27 章 UserControl とカスタム コントロール](27-custom-controls.md) へ進みます。

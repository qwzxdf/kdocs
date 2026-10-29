---
title: 第 25 章 MVVM ライブラリを比べる
tags:
  - C#連携
---

# 第 25 章 MVVM ライブラリを比べる

この教材では Prism の `BindableBase` と `DelegateCommand` を使っています。ただ、WPF の解説記事を探すと、CommunityToolkit.Mvvm、ReactiveProperty、Livet など、別のライブラリを使った記事のほうがたくさん見つかります。「自分はどれを使えばいいのか」「他の記事のコードを Prism に読み替えるにはどうするのか」がすぐ分かるように、この章で並べて比べます。

!!! info "このページを読む前に"
    - [第 24 章 Prism を掘り下げる](24-prism-deep.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章での Editor"
    この章では、Editor にファイルを足しません。Editor の `SceneObjectViewModel`（名前と位置 X、リセット ボタン）を題材にして、3 つのライブラリでの書き方を比べます。

## 何を提供するライブラリなのか

先に整理しておくと、MVVM を支えるライブラリは、2 種類の仕事に分かれます。

| 仕事 | 内容 | 代表 |
| --- | --- | --- |
| ① ビューモデルを書きやすくする | `INotifyPropertyChanged` の実装、コマンド、検証、メッセージ | CommunityToolkit.Mvvm、Prism（`BindableBase`）、ReactiveProperty、Livet |
| ② アプリの構造を作る | 画面の枠（リージョン）、モジュール、ナビゲーション、ダイアログ、DI | Prism |

Prism は①と②の両方を持っています。CommunityToolkit.Mvvm は①だけです。アプリの構造（②）が要るなら、Prism か、別の DI ライブラリ（`Microsoft.Extensions.DependencyInjection` など）と組み合わせた自作になります。

## 同じ画面を 3 通りで書く

第 13〜16 章で作った `SceneObjectViewModel` の、名前と位置 X、リセット コマンドだけを取り出して、3 つの書き方で並べます。

### Prism

```csharp title="Editor の書き方（第 12 章）"
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

### ReactiveProperty

```csharp title="実験：ReactiveProperty で書くと（Editor には入れない）"
public class SceneObjectViewModel
{
    public ReactiveProperty<string> Name { get; } = new("");
    public ReactiveProperty<float> X { get; } = new(0);
    public ReactiveCommand ResetCommand { get; }

    public SceneObjectViewModel()
    {
        ResetCommand = X.Select(x => x != 0).ToReactiveCommand();
        ResetCommand.Subscribe(() => X.Value = 0);
    }
}
```

値を `ReactiveProperty<T>` で包み、Rx（Reactive Extensions）の演算子で組み合わせる書き方です。値の変化を「流れ」として扱えるので、「入力が変わったら 300 ミリ秒待って、検索する」のような処理を宣言的に書けます。ただし、Rx の考え方を学ぶ必要があります。

## どれを選ぶか

| 状況 | 目安 |
| --- | --- |
| 画面が少なく、MVVM の補助だけがほしい | CommunityToolkit.Mvvm（軽くて、情報が多い） |
| 画面が増え、リージョンやモジュールで部品に分けたい | Prism |
| 非同期の流れや、入力の連動を宣言的に書きたい | ReactiveProperty（+ 他と併用） |
| 小規模で、とにかく依存を増やしたくない | ライブラリなし（`INotifyPropertyChanged` と自作の `RelayCommand`） |

この教材は、リージョンとモジュールを使う前提なので、Prism を選んでいます。ただし、`BindableBase` の代わりに CommunityToolkit.Mvvm の `ObservableObject` を使う、という組み合わせもできます。Prism は MVVM の補助部分を別のライブラリに替えられる設計です。

## 書き換えの対応表

他のライブラリで書かれた記事を読むときの、対応表です。

| やりたいこと | Prism | CommunityToolkit.Mvvm |
| --- | --- | --- |
| 通知付きプロパティ | `SetProperty(ref _x, value)` | `[ObservableProperty]` または `SetProperty(ref _x, value)` |
| 基底クラス | `BindableBase` | `ObservableObject` |
| コマンド | `DelegateCommand` | `RelayCommand`（`[RelayCommand]`） |
| 非同期コマンド | なし（第 16 章の `AsyncCommand` のように自作する） | `AsyncRelayCommand` |
| 条件が変わったら再判定 | `.ObservesProperty(() => X)` | `[NotifyCanExecuteChangedFor(...)]` |
| 値が変わったときの処理 | `SetProperty(ref _x, value, OnChanged)` | `partial void OnXxxChanged(T value)` |
| メッセージの送受信 | `IEventAggregator` | `WeakReferenceMessenger`（`ObservableRecipient`） |
| 入力の検証 | `ErrorsContainer<T>`（第 14 章で Editor に入れた） | `ObservableValidator`（`[Required]`、`[Range]` など） |

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

`INotifyDataErrorInfo`（第 14 章）を実装済みで、`System.ComponentModel.DataAnnotations` の属性で検証規則を書けます。第 14 章で、`Name` の `set` に手で書いた「空なら `SetError`」が、属性 1 行になります。入力検証を多用する画面を作るなら、これは魅力的です。

## Prism と組み合わせる

Prism の DI やリージョンを使いつつ、MVVM の補助部分だけを CommunityToolkit.Mvvm にしたいときは、次のとおりです。

1. `CommunityToolkit.Mvvm` を NuGet で入れる。
2. ビューモデルの基底クラスに `ObservableObject` を使う（`BindableBase` の代わり）。
3. ViewModelLocator（`AutoWireViewModel`）、リージョン、ダイアログ サービスは、そのまま Prism を使う。`INavigationAware` などを実装するのも、これまでと同じ。

基底クラスが違っても、Prism の ViewModelLocator は「`DataContext` に入れる」だけなので、衝突はしません。

## この章のまとめ

- ライブラリは「ビューモデルを書きやすくする」ものと、「アプリの構造を作る」ものに分かれる。Prism は両方、CommunityToolkit.Mvvm は前者だけ。
- CommunityToolkit.Mvvm は、ソース ジェネレーターで書く量を減らす。`partial` を付けるのを忘れない。
- 他のライブラリの記事を読むときは、対応表で読み替える。
- 構造（リージョン、モジュール）が要るなら Prism。補助だけなら、CommunityToolkit.Mvvm で十分。

次の章では、部品を使い回すための `UserControl` と、カスタム コントロールの作り方を説明します。

[第 26 章 UserControl とカスタム コントロール](26-custom-controls.md) へ進みます。

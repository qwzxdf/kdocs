---
title: 第 15 章 非同期処理と UI スレッド
tags:
  - C#連携
---

# 第 15 章 非同期処理と UI スレッド

「ボタンを押したら、画面が固まった」。WPF を作っていて、いちばん早くぶつかる問題の 1 つです。原因はほとんど決まっていて、重い処理を UI スレッドでやってしまったからです。この章では、UI スレッドとは何か、どう逃がすか、よくある落とし穴を説明します。

## UI スレッドは 1 本だけ

WPF の画面の部品は、作ったスレッドからしか触れません。通常のアプリでは、画面を作るのは「UI スレッド」という 1 本のスレッドです。ボタンのクリックも、文字の入力も、再描画も、すべてこの 1 本が順番に処理しています。

そこで 3 秒かかる処理を直接実行すると、その間 UI スレッドが埋まって、クリックにも再描画にも応えられなくなり、画面が固まって見えます。

```csharp
private void OnLoadClicked()
{
    var text = File.ReadAllText(bigFile);    // 3 秒かかる → その間、画面が固まる
    Content = text;
}
```

## 解決の基本：async / await

重い処理や待ち時間のある処理は、`async` と `await` で書きます。

```csharp
private async Task LoadAsync()
{
    var text = await File.ReadAllTextAsync(bigFile);   // 待っている間、UI スレッドは自由
    Content = text;                                      // 終わったら、UI スレッドに戻ってくる
}
```

`await` の地点で、関数はいったん中断して UI スレッドに制御を返します。ファイルの読み込み自体は別のところで進み、終わったら、続きが UI スレッドで再開します。だから `await` の後ろで、画面のプロパティやコレクションを触っても大丈夫です。

CPU を使う計算のように、「待つ」のではなく「走らせ続ける」処理は、`Task.Run` で別のスレッドに逃がします。

```csharp
var result = await Task.Run(() => HeavyCalculation(data));   // 別のスレッドで走る
Result = result;                                              // 戻ってきたら UI スレッド
```

`Task.Run` の中のラムダでは、画面の部品や `ObservableCollection` を触ってはいけません（別のスレッドだからです）。結果を `await` で受け取ってから、UI スレッドで反映します。

## ボタンから非同期処理を呼ぶ

`DelegateCommand` には、非同期の処理を渡せる `FromAsync` があります。

```csharp
LoadCommand = DelegateCommand.FromAsync(LoadAsync);
```

```csharp
private async Task LoadAsync()
{
    IsBusy = true;
    try
    {
        Items = await _service.LoadAsync();
    }
    catch (Exception e)
    {
        _log.Error($"読み込みに失敗: {e.Message}");
    }
    finally
    {
        IsBusy = false;
    }
}
```

`async void` は、イベント ハンドラー以外では使わないでください。`async void` の関数で起きた例外は、呼び出し元で捕まえられず、アプリが落ちることがあります。`Task` を返す形にして、呼び出し側で `await` します。`FromAsync` は、それを正しくやってくれる便利な口です。実行中は、`CanExecute` が自動で `false` になるので、二重実行も防げます。

CommunityToolkit.Mvvm なら `AsyncRelayCommand` が同じ役目を果たします（第 20 章）。

## 進み具合を画面に出す（IProgress）

長い処理の途中経過を、画面のプログレスバーに出したいときは、`IProgress<T>` を使います。

```csharp
public async Task ScanAsync(IProgress<double> progress, CancellationToken token)
{
    var files = Directory.GetFiles(root, "*", SearchOption.AllDirectories);
    for (int i = 0; i < files.Length; ++i)
    {
        token.ThrowIfCancellationRequested();
        await Task.Run(() => Process(files[i]), token);
        progress.Report((i + 1) / (double)files.Length);     // 進み具合を知らせる
    }
}
```

```csharp
var progress = new Progress<double>(p => ProgressValue = p);    // UI スレッドで作る
await ScanAsync(progress, _cts.Token);
```

`Progress<T>` は、作ったスレッド（ここでは UI スレッド）に、自動で結果を戻してくれます。バックグラウンドの処理から `Report` を呼ぶだけで、UI スレッドへの切り替えを自分で書かなくて済みます。

## キャンセルできるようにする

長い処理には、キャンセルの手段を用意しておくと親切です。`CancellationTokenSource` を作り、`Token` を処理に渡し、キャンセルするときに `Cancel()` を呼びます。

```csharp
private CancellationTokenSource? _cts;

private async Task StartAsync()
{
    _cts = new CancellationTokenSource();
    try
    {
        await ScanAsync(progress, _cts.Token);
    }
    catch (OperationCanceledException)
    {
        _log.Info("キャンセルしました");
    }
}

private void Cancel() => _cts?.Cancel();
```

処理の側は、ところどころで `token.ThrowIfCancellationRequested()` を呼んで、キャンセルされたら `OperationCanceledException` で抜けます。この例外は「異常」ではなく、キャンセルの合図です。

## 別のスレッドから UI を更新したい

イベントやコールバックが別のスレッドから呼ばれるとき（エンジンのログなど）は、UI スレッドに仕事を頼みます。

```csharp
Application.Current.Dispatcher.BeginInvoke(() => Entries.Add(entry));   // 頼んだら待たずに戻る
await Application.Current.Dispatcher.InvokeAsync(() => Entries.Add(entry));   // 終わるまで await
```

`Invoke`（同期的に待つ）は、UI スレッドが別の用事で待っていると、お互いに待ち合ってデッドロックする危険があります。基本は `BeginInvoke` か `InvokeAsync` を使います。

### コレクションを別のスレッドから触りたいとき

`ObservableCollection` を別のスレッドで直接変更すると、例外になります。次のどちらかで逃げます。

1. 変更を、`Dispatcher.BeginInvoke` で UI スレッドに回す（第 18 章のログ サービスはこの方法）。
2. `BindingOperations.EnableCollectionSynchronization(collection, lockObject)` を呼んで、WPF にロックの仕組みを教える。

```csharp
private readonly object _lock = new();
BindingOperations.EnableCollectionSynchronization(Entries, _lock);

// 別のスレッドから
lock (_lock) { Entries.Add(entry); }
```

2 のほうは、UI スレッドで作ったコレクションを呼ぶ前に設定する必要があります。迷ったら 1 のほうが単純です。

## 固まる原因の定番

| 症状 | 原因 |
| --- | --- |
| ボタンを押すと画面が固まる | 重い処理を UI スレッドで直接実行している |
| `async` にしたのに固まる | `.Result` や `.Wait()` で結果を同期的に待っている（デッドロック） |
| 勝手にアプリが落ちる | `async void` の中の例外が捕まっていない |
| 「別のスレッドが所有しているため…」の例外 | `Task.Run` の中や、別スレッドのコールバックで画面を触った |
| プログレスバーが動かない | 処理が UI スレッドで走っていて、描画が回らない |

`.Result` と `.Wait()` は、非同期の関数を同期的に待つ書き方ですが、UI スレッドで使うと、「UI スレッドの再開を待つ処理」を「UI スレッドが待つ」というデッドロックになりやすいです。非同期の呼び出しは、最後まで `await` でつなぐのが原則です。

## ConfigureAwait

ライブラリを書くときによく見る `await x.ConfigureAwait(false)` は、「`await` の後は、元のスレッドに戻らなくてよい」という指定です。画面を触らない低レベルの関数では、少し速くなりますが、画面を触る関数の中で付けてはいけません。アプリの画面側のコードでは、付けない（既定のまま）で構いません。

## この章のまとめ

- 重い処理は UI スレッドの外へ。待つ処理は `async` / `await`、計算は `Task.Run`。
- `await` の後は UI スレッドに戻るので、画面を触ってよい。`Task.Run` の中では触らない。
- `async void` はイベント ハンドラー以外では使わない。コマンドは `DelegateCommand.FromAsync`。
- 経過は `Progress<T>`、中断は `CancellationToken`。
- 別のスレッドから UI を更新するときは、`Dispatcher.BeginInvoke`。`.Result` / `.Wait()` で待たない。

次の章では、Prism を導入して、定型文をライブラリに任せ、アプリの起動の流れを作り直します。

[第 16 章 Prism の導入と起動の流れ](16-prism-bootstrap.md) へ進みます。

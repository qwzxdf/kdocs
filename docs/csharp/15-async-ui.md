---
title: 第 15 章 非同期処理と UI スレッド
tags:
  - C#連携
---

# 第 15 章 非同期処理と UI スレッド

「ボタンを押したら、画面が固まった」。WPF を作っていて、いちばん早くぶつかる問題の 1 つです。原因はほとんど決まっていて、重い処理を UI スレッドでやってしまったからです。この章では、UI スレッドとは何か、どう逃がすか、よくある落とし穴を説明します。

!!! info "このページを読む前に"
    - [第 14 章 リストとデータ表示](14-lists.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


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

Prism の `DelegateCommand` は、同期のメソッドしか受け取れません。`new DelegateCommand(async () => await LoadAsync())` と書くことはできますが、中身は `async void` と同じになります。`async void` の関数で起きた例外は、呼び出し元で捕まえられず、アプリが落ちることがあります。実行中に二重で押される問題も、自分で防がなければなりません。

そこで、非同期の処理を渡せるコマンドを自分で 1 つ作っておきます。第 12 章で作った `RelayCommand` の仲間です。

```csharp title="Mvvm/AsyncCommand.cs"
using System.Windows.Input;

namespace Editor.Mvvm;

// 非同期の処理を実行するコマンド。実行中は押せなくなり、二重に実行されない。
public sealed class AsyncCommand : ICommand
{
    private readonly Func<Task> _execute;
    private readonly Func<bool>? _canExecute;
    private readonly Action<Exception>? _onError;
    private bool _isRunning;

    public AsyncCommand(Func<Task> execute, Func<bool>? canExecute = null, Action<Exception>? onError = null)
    {
        _execute = execute;
        _canExecute = canExecute;
        _onError = onError;
    }

    public event EventHandler? CanExecuteChanged;

    public bool CanExecute(object? parameter) => !_isRunning && (_canExecute?.Invoke() ?? true);

    // ICommand の Execute は戻り値が void なので、ここだけは async void になる。
    // 例外は自分で捕まえて、外へ漏らさない。
    public async void Execute(object? parameter)
    {
        if (!CanExecute(parameter)) return;

        _isRunning = true;
        RaiseCanExecuteChanged();
        try
        {
            await _execute();
        }
        catch (Exception e) when (_onError is not null)
        {
            _onError(e);
        }
        finally
        {
            _isRunning = false;
            RaiseCanExecuteChanged();
        }
    }

    public void RaiseCanExecuteChanged() => CanExecuteChanged?.Invoke(this, EventArgs.Empty);
}
```

`ICommand.Execute` が `void` を返す決まりなので、`async void` をなくすことはできません。そこで、`async void` を 1 か所に閉じ込めて、例外の処理と二重実行の防止をそこで済ませます。`onError` を渡さなかったときは、例外がそのまま UI スレッドの未処理例外になります（第 49 章でまとめて受け取ります）。

使う側は、次のように書きます。

```csharp
LoadCommand = new AsyncCommand(LoadAsync, onError: e => _log.Error($"読み込みに失敗: {e.Message}"));
```

```csharp
private async Task LoadAsync()
{
    IsBusy = true;
    try
    {
        Items = await _service.LoadAsync();
    }
    finally
    {
        IsBusy = false;
    }
}
```

実行中は `CanExecute` が `false` になるので、ボタンが自動で押せなくなります。`canExecute` を渡せば、「実行中でなく、かつ編集中のとき」のような条件も足せます。条件が変わったら、`RaiseCanExecuteChanged()` を呼びます。

CommunityToolkit.Mvvm なら `AsyncRelayCommand` が同じ役目を果たします（第 25 章）。

## 進み具合を画面に出す（IProgress）

長い処理の途中経過を画面のプログレスバーに出したいときは、`IProgress<T>` を使います。

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

`Progress<T>` は、作ったスレッド（ここでは UI スレッド）に自動で結果を戻してくれます。バックグラウンドの処理から `Report` を呼ぶだけで、UI スレッドへの切り替えを自分で書かなくて済みます。

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

1. 変更を `Dispatcher.BeginInvoke` で UI スレッドに回す（第 23 章のログ サービスはこの方法）。
2. `BindingOperations.EnableCollectionSynchronization(collection, lockObject)` を呼んで、WPF にロックの仕組みを教える。

```csharp
private readonly object _lock = new();
BindingOperations.EnableCollectionSynchronization(Entries, _lock);

// 別のスレッドから
lock (_lock) { Entries.Add(entry); }
```

`lock (_lock) { … }` は、同じ `_lock` を持つ `lock` の中に、同時に 1 つのスレッドしか入れないようにする文です。C++ の `std::lock_guard<std::mutex>` に当たり、`{}` を抜けると自動でロックが外れます。ロックに使うのは、このように専用の `object` にするのが決まりで、`this` や文字列は避けます。外から同じ物を `lock` されて、思わぬ待ちが起きるためです。

2 のほうの `EnableCollectionSynchronization` は、UI スレッドで呼びます。別のスレッドから `Add` を始める前に設定を済ませておいてください。迷ったら 1 のほうが単純です。

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

## C++ で考えると

UI スレッドは、ゲームのメイン スレッドのようなものです。画面に触れるのはここだけで、ここが長く止まると、ゲームのフレームが落ちるのと同じように、画面が固まります。`await` は、C++20 のコルーチンの `co_await` に近い考え方です。待っている間はスレッドを塞がず、結果が出たら続きを再開します。`std::async` や `std::future::get()` は、結果が出るまでスレッドを止めて待つので、UI スレッドで使うと固まります。`await` が別物なのは、そこです。

## この章のまとめ

- 重い処理は UI スレッドの外へ。待つ処理は `async` / `await`、計算は `Task.Run`。
- `await` の後は UI スレッドに戻るので、画面を触ってよい。`Task.Run` の中では触らない。
- `async void` はイベント ハンドラー以外では使わない。コマンドは、自作の `AsyncCommand`（または `AsyncRelayCommand`）。
- 経過は `Progress<T>`、中断は `CancellationToken`。
- 別のスレッドから UI を更新するときは、`Dispatcher.BeginInvoke`。`.Result` / `.Wait()` で待たない。

次の章では、Prism を導入して、定型文をライブラリに任せ、アプリの起動の流れを作り直します。

[第 16 章 Prism の導入と起動の流れ](16-prism-bootstrap.md) へ進みます。

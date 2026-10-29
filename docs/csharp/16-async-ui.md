---
title: 第 16 章 非同期処理と UI スレッド
tags:
  - C#連携
---

# 第 16 章 非同期処理と UI スレッド

「ボタンを押したら、画面が固まった」。WPF を作っていて、いちばん早くぶつかる問題の 1 つです。原因はほとんど決まっていて、重い処理を UI スレッドでやってしまったからです。

前の章で作ったアセット一覧は、ダミーのデータを並べているだけでした。この章では、本物のフォルダーを読み込むボタンを足します。ファイルが多いフォルダーを読むと、まず画面が固まります。そこから、固まらない書き方、進み具合の表示、キャンセルを、順に足していきます。

!!! info "このページを読む前に"
    - [第 15 章 リストとデータ表示](15-lists.md)（前の章。この章は、そこで作った「アセット」のタブに足していく）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Services/AssetScanner.cs`（新規） | フォルダーの中のファイルを読む（非同期） |
    | `App.xaml.cs`（変更） | 作るクラスをコンテナーに登録する |
    | `Mvvm/AsyncCommand.cs`（新規） | 非同期の処理を実行するコマンド |
    | `ViewModels/LogViewModel.cs`（変更） | 別のスレッドからでもログを足せるようにする |
    | `ViewModels/AssetBrowserViewModel.cs`（変更） | 読み込み、進み具合、キャンセル |
    | `MainWindowViewModel.cs`（変更） | `Log` と `AssetBrowser` を受け取る |
    | `MainWindow.xaml`（変更） | 「読み込み」「キャンセル」のボタンと進行バー |

## まず、普通に書いて固まらせる

「アセット」のタブに、読み込むボタンを足します。先に画面の側です。

```xml title="MainWindow.xaml（変更：アセットのタブの DockPanel の先頭に足す）"
<StackPanel DockPanel.Dock="Top" Orientation="Horizontal" Margin="4">
    <Button Content="読み込み" Padding="12,2" Command="{Binding LoadCommand}" />
</StackPanel>
```

`AssetBrowserViewModel` に、同期で書いた最初の版を足します。ファイルを 1 つずつ調べて、一覧に足すだけです。

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更：最初の版）"
using System.IO;       // WPF のプロジェクトでは、System.IO は自動では入らない
using Prism.Commands;

public DelegateCommand LoadCommand { get; }

// コンストラクターの中
LoadCommand = new DelegateCommand(Load);

private void Load()
{
    Entries.Clear();
    foreach (var path in Directory.GetFiles(AppContext.BaseDirectory, "*", SearchOption.AllDirectories))
    {
        var info = new FileInfo(path);
        Entries.Add(new FileEntry(info.Name, "other", info.Length));
        Thread.Sleep(20);        // ディスクが遅いふりをする（あとで消す）
    }
}
```

`AppContext.BaseDirectory` は、Editor を実行している場所のフォルダーです。今はつなぐ先のプロジェクトがないので、ここを読みます。`Thread.Sleep(20)` は、実際のフォルダーが大きくて遅いときの代わりです。

押すと、数秒のあいだウィンドウが固まります。ボタンもスクロールも効かず、ウィンドウのタイトル バーに「応答なし」と出ます。

### 深掘り：UI スレッドは 1 本だけ

WPF の画面の部品は、作ったスレッドからしか触れません。通常のアプリでは、画面を作るのは「UI スレッド」という 1 本のスレッドです。ボタンのクリックも、文字の入力も、再描画も、すべてこの 1 本が順番に処理しています。

そこへ 3 秒かかる処理を直接実行すると、その間 UI スレッドが埋まって、クリックにも再描画にも応えられなくなり、画面が固まって見えます。`Load` は、`Thread.Sleep` を挟んだ 1 本の長い処理なので、終わるまで次のクリックを受けられません。

C++ で考えると、UI スレッドはゲームのメイン スレッドのようなものです。画面に触れるのはここだけで、ここが長く止まると、ゲームのフレームが落ちるのと同じように、画面が固まります。

## 解決の基本：async / await

重い処理や待ち時間のある処理は、`async` と `await` で書きます。

```csharp
private async Task LoadAsync()
{
    var text = await File.ReadAllTextAsync(path);   // 待っている間、UI スレッドは自由
    Content = text;                                  // 終わったら、UI スレッドに戻ってくる
}
```

`await` の地点で、関数はいったん中断して UI スレッドに制御を返します。ファイルの読み込み自体は別のところで進み、終わったら、続きが UI スレッドで再開します。だから `await` の後ろで、画面のプロパティやコレクションを触っても大丈夫です。

CPU を使う計算のように、「待つ」のではなく「走らせ続ける」処理は、`Task.Run` で別のスレッドに逃がします。

```csharp
var result = await Task.Run(() => HeavyCalculation(data));   // 別のスレッドで走る
Result = result;                                              // 戻ってきたら UI スレッド
```

`Task.Run` の中のラムダでは、画面の部品や `ObservableCollection` を触ってはいけません（別のスレッドだからです）。結果を `await` で受け取ってから、UI スレッドで反映します。

`await` は、C++20 のコルーチンの `co_await` に近い考え方です。待っている間はスレッドを塞がず、結果が出たら続きを再開します。`std::async` や `std::future::get()` は、結果が出るまでスレッドを止めて待つので、UI スレッドで使うと固まります。`await` が別物なのは、そこです。

## フォルダーを読む処理を、別のクラスに出す

読み込みの本体を、ビューモデルから出して、非同期のクラスにします。

```csharp title="Services/AssetScanner.cs（新規）"
using System.IO;
using Editor.Models;

namespace Editor.Services;

public class AssetScanner
{
    public Task<IReadOnlyList<FileEntry>> ScanAsync(string root, Action<string>? log = null)
    {
        return Task.Run(() =>
        {
            var paths = Directory.GetFiles(root, "*", SearchOption.AllDirectories);
            log?.Invoke($"{paths.Length} 個のファイルを見つけました");   // 別のスレッドで動いている

            var result = new List<FileEntry>(paths.Length);
            foreach (var path in paths)
            {
                var info = new FileInfo(path);
                result.Add(new FileEntry(info.Name, KindOf(info.Extension), info.Length));
                Thread.Sleep(20);        // ディスクが遅いふりをする（あとで消す）
            }
            return (IReadOnlyList<FileEntry>)result;
        });
    }

    private static string KindOf(string extension) => extension.ToLowerInvariant() switch
    {
        ".scene" => "scene",
        ".png" or ".jpg" or ".dds" => "texture",
        ".mesh" or ".fbx" or ".obj" => "mesh",
        _ => "other",
    };
}
```

`Task.Run` の中は、別のスレッドで動きます。ここで画面の部品や `ObservableCollection` には触れていません。見つけたファイルを `List` に溜めて、最後に返しているだけです。`KindOf` の `switch` 式は、拡張子から種類を決める C# の書き方で、`or` は「どれか」を表します。

`log` は、ログを出したいときに外から渡してもらう関数です。ここでログを出すとどうなるのかは、少しあとで見ます。

ビューモデルを、この `ScanAsync` を使う形に書き換えます。

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更）"
private readonly AssetScanner _scanner = new();

private async Task LoadAsync()
{
    var files = await _scanner.ScanAsync(AppContext.BaseDirectory);   // 待っている間、UI は動く
    Entries.Clear();
    foreach (var file in files) Entries.Add(file);                     // 戻ってきたので、UI スレッド
}
```

`Load` を `LoadAsync` に置き換えます。`LoadCommand` は、ボタンに渡す形が要ります。次の節で作ります。

## ボタンから非同期処理を呼ぶ

ここまでの `DelegateCommand` は、同期のメソッドしか受け取れません。`new DelegateCommand(async () => await LoadAsync())` と書くことはできますが、中身は `async void` と同じになります。Prism には `DelegateCommand.FromAsyncHandler` もありますが、実行中の二重押しの防止は、自分で書かなければなりません。`async void` の関数で起きた例外は、呼び出し元で捕まえられず、アプリが落ちることがあります。実行中に二重で押される問題も、自分で防がなければなりません。

そこで、非同期の処理を渡せるコマンドを、もう 1 つ作ります。

```csharp title="Mvvm/AsyncCommand.cs（新規）"
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

実行中は `CanExecute` が `false` になるので、読み込み中はボタンが自動で押せなくなります。CommunityToolkit.Mvvm なら `AsyncRelayCommand` が同じ役目を果たします（第 25 章）。

`AssetBrowserViewModel` の `LoadCommand` を、これに差し替えます。

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更）"
public AsyncCommand LoadCommand { get; }

// コンストラクターの中
LoadCommand = new AsyncCommand(LoadAsync, onError: e => _log.Add(LogLevel.Error, $"読み込みに失敗: {e.Message}"));
```

`_log` は、次の節で用意する `LogViewModel` です。

実行して「読み込み」を押すと、読み込んでいる間もウィンドウが動きます。ボタンは灰色になり、終わると一覧が入れ替わります。

## 別のスレッドからログを出す

`AssetScanner` の `log` を使う場所を作ります。`AssetBrowserViewModel` が `LogViewModel` を受け取れるようにして、読み込みの経過をログに出します。まず、受け渡しです。

`LogViewModel` を受け取る部分は、このあとの「作る係と使う係を分ける」で書きます。先に、ログを出す側の `LoadAsync` を書き換えます。

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更）"
private async Task LoadAsync()
{
    var files = await _scanner.ScanAsync(AppContext.BaseDirectory, msg => _log.Add(LogLevel.Info, msg));
    Entries.Clear();
    foreach (var file in files) Entries.Add(file);
}
```

ここで `LogViewModel` に `Add` を作ります。何も考えずに書くと、こうなります。

```csharp title="実験：スレッドを考えない Add（Editor には入れない）"
public void Add(LogLevel level, string message)
{
    Entries.Add(new LogEntry(DateTime.Now, level, message));
}
```

読み込むと、`log` が呼ばれた瞬間に、次のような例外でアプリが落ちます。

```text
System.NotSupportedException:
  このタイプの CollectionView は、Dispatcher スレッドとは異なるスレッドからの SourceCollection への変更をサポートしていません。
```

`log` は `Task.Run` の中、つまり別のスレッドから呼ばれています。そのスレッドから、画面にバインドされた `ObservableCollection` を直接変更したからです。

### 深掘り：別のスレッドから UI を更新する

イベントやコールバックが別のスレッドから呼ばれるとき（エンジンのログなど）は、UI スレッドに仕事を頼みます。

```csharp
Application.Current.Dispatcher.InvokeAsync(() => Entries.Add(entry));   // 頼んだら待たずに戻る
await Application.Current.Dispatcher.InvokeAsync(() => Entries.Add(entry));   // 終わるまで await
```

`Invoke`（同期的に待つ）は、UI スレッドが別の用事で待っていると、お互いに待ち合ってデッドロックする危険があります。基本は `InvokeAsync`（または `BeginInvoke`）を使います。これで `Add` を直します。

```csharp title="ViewModels/LogViewModel.cs（変更）"
using System.Windows;

public void Add(LogLevel level, string message)
{
    var entry = new LogEntry(DateTime.Now, level, message);
    var dispatcher = Application.Current.Dispatcher;
    if (dispatcher.CheckAccess())
        Entries.Add(entry);                                  // もう UI スレッドなので、そのまま
    else
        dispatcher.InvokeAsync(() => Entries.Add(entry));    // UI スレッドに頼む
}
```

`CheckAccess()` は、今のスレッドが UI スレッドかを調べます。どのスレッドから呼んでも安全な `Add` になりました。エンジンからのコールバックでログを受け取る第 49 章でも、この `Add` をそのまま使います。

コレクションを別のスレッドから触りたいときの方法は、もう 1 つあります。`BindingOperations.EnableCollectionSynchronization(collection, lockObject)` を呼んで、WPF にロックの仕組みを教える方法です。

```csharp title="実験：EnableCollectionSynchronization（Editor には入れない）"
private readonly object _lock = new();
BindingOperations.EnableCollectionSynchronization(Entries, _lock);

// 別のスレッドから
lock (_lock) { Entries.Add(entry); }
```

`lock (_lock) { … }` は、同じ `_lock` を持つ `lock` の中に、同時に 1 つのスレッドしか入れないようにする文です。C++ の `std::lock_guard<std::mutex>` に当たり、`{}` を抜けると自動でロックが外れます。ロックに使うのは、このように専用の `object` にするのが決まりで、`this` や文字列は避けます。外から同じ物を `lock` されて、思わぬ待ちが起きるためです。`EnableCollectionSynchronization` は UI スレッドで呼び、別のスレッドから `Add` を始める前に済ませます。迷ったら、上の `Dispatcher` のほうが単純です。

## 作る係と使う係を分ける

`AssetBrowserViewModel` が `LogViewModel` と `AssetScanner` を必要とするようになりました。これまでの書き方なら、使う側の `MainWindowViewModel` が、両方を `new` して渡すことになります。

```csharp title="手で組み立てる書き方（この章では採らない）"
Log = new LogViewModel();
AssetBrowser = new AssetBrowserViewModel(Log, new AssetScanner());
```

`AssetBrowserViewModel` が必要とするものが増えるたびに、`MainWindowViewModel` の側も書き換えなければなりません。使うクラスが、使われるクラスの作り方まで知っているのは、不自然です。

そこで、必要なものはコンストラクターの引数に書いて、<strong>作って渡す係</strong>を、別に置きます。その係が、第 12 章から裏で働いていた DI コンテナーです。DI は Dependency Injection（依存性注入）の略で、「必要なものを自分で作らず、外から渡してもらう」という設計の考え方です。やることは 2 つです。

1 つ目は、コンテナーに、どのクラスを作れるかを教えておくことです。第 12 章で空のまま置いた `RegisterTypes` に書きます。

```csharp title="App.xaml.cs（変更）"
using Editor.Services;
using Editor.ViewModels;

protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterSingleton<AssetScanner>();
    containerRegistry.RegisterSingleton<LogViewModel>();
    containerRegistry.RegisterSingleton<AssetBrowserViewModel>();
}
```

`RegisterSingleton` は、「このクラスは、アプリの間ずっと 1 つだけ作って、みんなで使い回す」という登録です。ログの一覧のように、みんなが同じものを見たいクラスは、これにします。`Singleton` と、毎回作る `Transient` の違いは、第 19 章で説明します。

2 つ目は、欲しいものを、コンストラクターの引数に書くことです。

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更）"
private readonly LogViewModel _log;
private readonly AssetScanner _scanner;

public AssetBrowserViewModel(LogViewModel log, AssetScanner scanner)
{
    _log = log;
    _scanner = scanner;
    // 以下は前のとおり
}
```

`private readonly AssetScanner _scanner = new();` の行は、消します。`MainWindowViewModel` のほうも、同じように書き換えます。

```csharp title="MainWindowViewModel.cs（変更）"
public LogViewModel Log { get; }
public AssetBrowserViewModel AssetBrowser { get; }

public MainWindowViewModel(LogViewModel log, AssetBrowserViewModel assetBrowser)
{
    Log = log;
    AssetBrowser = assetBrowser;
    // 以下は前のとおり
}
```

`new MainWindowViewModel(...)` と書いている場所は、どこにもありません。ViewModelLocator がコンテナーに「`MainWindowViewModel` を作って」と頼み、コンテナーがコンストラクターの引数を見て、`LogViewModel` と `AssetBrowserViewModel` を作って渡しています。`AssetBrowserViewModel` に必要な `LogViewModel` と `AssetScanner` も、同じやり方で渡されます。

なぜ登録だけで作れるのか、いつ作られるのか、インターフェースを挟む理由は何かは、第 17 章から順に説明します。いまは「必要なものは引数に書いて、`RegisterTypes` に登録する」とだけ覚えてください。

## 進み具合を画面に出す

読み込みに数秒かかるようになったので、進み具合を見せます。長い処理の途中経過を画面に出すときは、`IProgress<T>` を使います。`AssetScanner` に、進み具合を報告する引数を足します。

```csharp title="Services/AssetScanner.cs（変更）"
public Task<IReadOnlyList<FileEntry>> ScanAsync(
    string root, IProgress<double>? progress = null, Action<string>? log = null)
{
    return Task.Run(() =>
    {
        // ... paths を取るところまでは前のとおり
        for (int i = 0; i < paths.Length; ++i)
        {
            var info = new FileInfo(paths[i]);
            result.Add(new FileEntry(info.Name, KindOf(info.Extension), info.Length));
            Thread.Sleep(20);
            progress?.Report((i + 1) / (double)paths.Length);      // 進み具合を知らせる
        }
        return (IReadOnlyList<FileEntry>)result;
    });
}
```

ビューモデルに、進み具合のプロパティと、`Progress<double>` を渡す処理を足します。

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更）"
private double _progressValue;
private bool _isBusy;

public double ProgressValue { get => _progressValue; private set => SetProperty(ref _progressValue, value); }
public bool IsBusy { get => _isBusy; private set => SetProperty(ref _isBusy, value); }

private async Task LoadAsync()
{
    IsBusy = true;
    ProgressValue = 0;
    try
    {
        var progress = new Progress<double>(p => ProgressValue = p);    // UI スレッドで作る
        var files = await _scanner.ScanAsync(AppContext.BaseDirectory, progress, msg => _log.Add(LogLevel.Info, msg));
        Entries.Clear();
        foreach (var file in files) Entries.Add(file);
    }
    finally
    {
        IsBusy = false;
    }
}
```

```xml title="MainWindow.xaml（変更：アセットのタブの DockPanel に足す）"
<ProgressBar DockPanel.Dock="Bottom" Height="6" Maximum="1"
             Value="{Binding ProgressValue, Mode=OneWay}"
             Visibility="{Binding IsBusy, Converter={StaticResource BoolToVisibility}}" />
```

読み込み中は、パネルの下に細い進行バーが出て、右へ伸びていきます。

`Progress<T>` は、作ったスレッド（ここでは UI スレッド）に自動で結果を戻してくれます。バックグラウンドの処理から `Report` を呼ぶだけで、UI スレッドへの切り替えを自分で書かなくて済みます。バーの `Value` が `Mode=OneWay` なのは、`ProgressBar.Value` が読み取り専用のように振る舞うためです。

## キャンセルできるようにする

長い処理には、キャンセルの手段を用意しておくと親切です。`CancellationTokenSource` を作り、`Token` を処理に渡し、キャンセルするときに `Cancel()` を呼びます。

```csharp title="Services/AssetScanner.cs（変更）"
public Task<IReadOnlyList<FileEntry>> ScanAsync(
    string root, IProgress<double>? progress = null, Action<string>? log = null,
    CancellationToken token = default)
{
    return Task.Run(() =>
    {
        // ...
        for (int i = 0; i < paths.Length; ++i)
        {
            token.ThrowIfCancellationRequested();       // キャンセルされていたら、ここで抜ける
            // ...
        }
        return (IReadOnlyList<FileEntry>)result;
    }, token);
}
```

```csharp title="ViewModels/AssetBrowserViewModel.cs（変更）"
private CancellationTokenSource? _cts;

public DelegateCommand CancelCommand { get; }

// コンストラクターの中
CancelCommand = new DelegateCommand(() => _cts?.Cancel(), () => IsBusy)
    .ObservesProperty(() => IsBusy);

private async Task LoadAsync()
{
    _cts = new CancellationTokenSource();
    IsBusy = true;
    ProgressValue = 0;
    try
    {
        var progress = new Progress<double>(p => ProgressValue = p);
        var files = await _scanner.ScanAsync(AppContext.BaseDirectory, progress,
            msg => _log.Add(LogLevel.Info, msg), _cts.Token);
        Entries.Clear();
        foreach (var file in files) Entries.Add(file);
    }
    catch (OperationCanceledException)
    {
        _log.Add(LogLevel.Info, "読み込みをキャンセルしました");
    }
    finally
    {
        IsBusy = false;
        _cts.Dispose();
        _cts = null;
    }
}
```

`IsBusy` が変わったとき、キャンセルボタンの状態も聞き直してもらう必要があります。それは `ObservesProperty(() => IsBusy)` が引き受けてくれるので、`IsBusy` の `set` には何も足しません。

最後に、画面にキャンセルのボタンを足します。

```xml title="MainWindow.xaml（変更：読み込みボタンのあとに足す）"
<Button Content="キャンセル" Padding="12,2" Margin="4,0,0,0" Command="{Binding CancelCommand}" />
```

処理の側は、ところどころで `token.ThrowIfCancellationRequested()` を呼んで、キャンセルされたら `OperationCanceledException` で抜けます。この例外は「異常」ではなく、キャンセルの合図なので、受け取る側で `catch` してログに残すだけにしています。

## 固まる原因の定番

| 症状 | 原因 |
| --- | --- |
| ボタンを押すと画面が固まる | 重い処理を UI スレッドで直接実行している |
| `async` にしたのに固まる | `.Result` や `.Wait()` で結果を同期的に待っている（デッドロック） |
| 勝手にアプリが落ちる | `async void` の中の例外が捕まっていない |
| 「別のスレッドが所有しているため…」の例外 | `Task.Run` の中や、別スレッドのコールバックで画面を触った |
| プログレスバーが動かない | 処理が UI スレッドで走っていて、描画が回らない |

`.Result` と `.Wait()` は、非同期の関数を同期的に待つ書き方ですが、UI スレッドで使うと、「UI スレッドの再開を待つ処理」を「UI スレッドが待つ」というデッドロックになりやすいです。非同期の呼び出しは、最後まで `await` でつなぐのが原則です。

### 深掘り：ConfigureAwait

ライブラリを書くときによく見る `await x.ConfigureAwait(false)` は、「`await` の後は、元のスレッドに戻らなくてよい」という指定です。画面を触らない低レベルの関数では、少し速くなりますが、画面を触る関数の中で付けてはいけません。アプリの画面側のコードでは、付けない（既定のまま）で構いません。

## 動かして確かめる

`F5` で実行して、次を確かめてください。

- 「アセット」のタブで「読み込み」を押すと、ボタンが灰色になり、下に進行バーが伸びる。その間、ウィンドウの移動やタブの切り替えができる。
- 終わると一覧が入れ替わり、`Editor.dll` などのファイルが並ぶ。「ログ」のタブに「N 個のファイルを見つけました」と出ている。
- 読み込み中に「キャンセル」を押すと止まり、一覧は元のままで、ログに「読み込みをキャンセルしました」と出る。
- 読み込み中は、「読み込み」のボタンが押せない（二重に始まらない）。

確かめ終わったら、`AssetScanner` の `Thread.Sleep(20)` の行を消してください。ディスクが遅いふりをするための行で、本番には要りません。

??? failure "ログに足した瞬間にアプリが落ちる"
    `LogViewModel.Add` の中で、`Dispatcher` を経由せず `Entries.Add` を直接呼んでいます。上の `CheckAccess` を使った版に直してください。

??? failure "キャンセルを押しても、止まらない"
    `ScanAsync` のループで `token.ThrowIfCancellationRequested()` を呼んでいるか、`ScanAsync` に `_cts.Token` を渡しているかを確かめます。

??? failure "キャンセルボタンがずっと灰色のまま"
    `CancelCommand` に、`.ObservesProperty(() => IsBusy)` が付いているかを確かめます。

## ここまでの Editor

```text
Editor/
├─ Models/                           （第 15 章のまま）
├─ Mvvm/
│   ├─ ValidatableViewModelBase.cs
│   └─ AsyncCommand.cs               非同期のコマンド（新規）
├─ Services/
│   └─ AssetScanner.cs               フォルダーを非同期で読む（新規）
├─ ViewModels/
│   ├─ SceneObjectViewModel.cs
│   ├─ AssetBrowserViewModel.cs      読み込み、進み具合、キャンセル
│   ├─ LogViewModel.cs               どのスレッドからでも Add できる
├─ MainWindowViewModel.cs            Log と AssetBrowser を受け取る
└─ MainWindow.xaml                   読み込み、キャンセル、進行バー
```

## この章のまとめ

- 重い処理は UI スレッドの外へ。待つ処理は `async` / `await`、計算は `Task.Run`。
- `await` の後は UI スレッドに戻るので、画面を触ってよい。`Task.Run` の中では触らない。
- `async void` はイベント ハンドラー以外では使わない。コマンドは、自作の `AsyncCommand`（または CommunityToolkit.Mvvm の `AsyncRelayCommand`）。
- 経過は `Progress<T>`、中断は `CancellationToken`。
- 別のスレッドから UI を更新するときは、`Dispatcher.InvokeAsync`。`.Result` / `.Wait()` で待たない。

次の章では、この章で使った DI を、「なぜ要るのか」から説明し直します。

[第 17 章 DI とは何か](17-di-basics.md) へ進みます。

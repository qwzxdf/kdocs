---
title: 第 17 章 非同期処理と UI スレッド
tags:
  - C#連携
---

# 第 17 章 非同期処理と UI スレッド

「ボタンを押したら画面が固まった」。WPF を作っていていちばん早くぶつかる問題の 1 つです。原因はほとんど決まっていて重い処理を UI スレッドでやってしまったからです。

前の章で作ったアセット一覧はダミーのデータを並べているだけでした。この章では本物のフォルダーを読み込むボタンを足します。ファイルが多いフォルダーを読むとまず画面が固まります。そこから固まらない書き方、進み具合の表示、キャンセルを順に足していきます。

!!! info "このページを読む前に"
    - [第 16 章 リストとデータ表示](16-lists.md)（前の章。この章はそこで作った「アセット」のタブに足していく）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）

!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Asset/AssetScanner.cs`（新規） | フォルダーの中のファイルを読む（非同期） |
    | `App.xaml.cs`（変更） | 作るクラスをコンテナーに登録する |
    | `Log/LogViewModel.cs`（変更） | 別のスレッドからでもログを足せるようにする |
    | `Asset/AssetViewModel.cs`（変更） | 読み込み進み具合、キャンセル |
    | `MainWindowViewModel.cs`（変更） | `Log` と `AssetBrowser` を受け取る |
    | `MainWindow.xaml`（変更） | 「読み込み」「キャンセル」のボタンと進行バー |

## まず普通に書いて固まらせる

「アセット」のタブに読み込むボタンを足します。先に画面の側です。

```xml title="MainWindow.xaml（変更：アセットのタブの DockPanel の先頭に足す）"
<StackPanel DockPanel.Dock="Top" Orientation="Horizontal" Margin="4">
    <Button Content="読み込み" Padding="12,2" Command="{Binding LoadCommand}" />
</StackPanel>
```

`AssetViewModel` に同期で書いた最初の版を足します。ファイルを 1 つずつ調べて、一覧に足すだけです。

```csharp title="Asset/AssetViewModel.cs（変更：最初の版）"
using System.IO;       // WPF のプロジェクトでは、System.IO は自動では入らない
using CommunityToolkit.Mvvm.Input;

[RelayCommand]
private void Load()               // LoadCommand が生成される
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

`AppContext.BaseDirectory` は Editor を実行している場所のフォルダーです。今はつなぐ先のプロジェクトがないので、ここを読みます。`Thread.Sleep(20)` は実際のフォルダーが大きくて遅いときの代わりです。

押すと数秒のあいだウィンドウが固まります。ボタンもスクロールも効かずウィンドウのタイトル バーに「応答なし」と出ます。

### 深掘り：UI スレッドは 1 本だけ

WPF の画面の部品は作ったスレッドからしか触れません。通常のアプリでは画面を作るのは「UI スレッド」という 1 本のスレッドです。ボタンのクリックも文字の入力も再描画もすべてこの 1 本が順番に処理しています。

そこへ 3 秒かかる処理を直接実行すると、その間 UI スレッドが埋まって、クリックにも再描画にも応えられなくなり画面が固まって見えます。`Load` は `Thread.Sleep` を挟んだ 1 本の長い処理なので、終わるまで次のクリックを受けられません。

C++ で考えると UI スレッドはゲームのメイン スレッドのようなものです。画面に触れるのはここだけでここが長く止まると、ゲームのフレームが落ちるのと同じように画面が固まります。

## 解決の基本：async / await

重い処理や待ち時間のある処理は `async` と `await` で書きます。

```csharp
private async Task LoadAsync()
{
    var text = await File.ReadAllTextAsync(path);   // 待っている間、UI スレッドは自由
    Content = text;                                  // 終わったら、UI スレッドに戻ってくる
}
```

`await` の地点で関数はいったん中断して UI スレッドに制御を返します。ファイルの読み込み自体は別のところで進み終わったら、続きが UI スレッドで再開します。だから `await` の後ろで画面のプロパティやコレクションを触っても大丈夫です。

CPU を使う計算のように「待つ」のではなく「走らせ続ける」処理は、`Task.Run` で別のスレッドに逃がします。

```csharp
var result = await Task.Run(() => HeavyCalculation(data));   // 別のスレッドで走る
Result = result;                                              // 戻ってきたら UI スレッド
```

`Task.Run` の中のラムダでは画面の部品や `ObservableCollection` を触ってはいけません（別のスレッドだからです）。結果を `await` で受け取ってから、UI スレッドで反映します。

`await` は C++20 のコルーチンの `co_await` に近い考え方です。待っている間はスレッドを塞がず結果が出たら続きを再開します。`std::async` や `std::future::get()` は結果が出るまでスレッドを止めて待つので、UI スレッドで使うと固まります。`await` が別物なのはそこです。

## フォルダーを読む処理を別のクラスに出す

読み込みの本体をビューモデルから出して、非同期のクラスにします。

```csharp title="Asset/AssetScanner.cs（新規）"
using System.IO;

namespace Editor.Asset;

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

`Task.Run` の中は別のスレッドで動きます。ここで画面の部品や `ObservableCollection` には触れていません。見つけたファイルを `List` に溜めて、最後に返しているだけです。`KindOf` の `switch` 式は拡張子から種類を決める C# の書き方で、`or` は「どれか」を表します。

`log` はログを出したいときに外から渡してもらう関数です。ここでログを出すとどうなるのかは少しあとで見ます。

ビューモデルをこの `ScanAsync` を使う形に書き換えます。

```csharp title="Asset/AssetViewModel.cs（変更）"
private readonly AssetScanner _scanner = new();

private async Task LoadAsync()
{
    var files = await _scanner.ScanAsync(AppContext.BaseDirectory);   // 待っている間、UI は動く
    Entries.Clear();
    foreach (var file in files) Entries.Add(file);                     // 戻ってきたので、UI スレッド
}
```

`Load` を `LoadAsync` に置き換えます。`LoadCommand` はボタンに渡す形が要ります。次の節で作ります。

## ボタンから非同期処理を呼ぶ

ここまでの `[RelayCommand]` は同期のメソッドに付けてきました。非同期のメソッドに付けるときは `async void` にしないでください。`async void` の関数で起きた例外は呼び出し元で捕まえられずアプリが落ちることがあります。実行中に二重で押される問題も自分で防がなければなりません。

非同期のメソッドは `Task` を返す `async` メソッドにして、`[RelayCommand]` を付けます。

```csharp title="Asset/AssetViewModel.cs（変更）"
[RelayCommand]
private async Task LoadAsync()          // LoadCommand が生成される（末尾の Async は取れる）
{
    // … 読み込み
}
```

`Task` を返すメソッドに付けると、ジェネレーターは `AsyncRelayCommand` を生成します。名前の規則はメソッド名の末尾の `Async` を取って、`Command` を足したものです（`LoadAsync` → `LoadCommand`）。

`AsyncRelayCommand` は実行中は自分を押せない状態（`CanExecute` が `false`）にします。読み込み中はボタンが自動で灰色になり二重に実行されません。自作の `ICommand` で書くと「実行中の印」と `CanExecuteChanged` の呼び出しを `try` と `finally` で囲んで書くことになりますが、それを `AsyncRelayCommand` が引き受けてくれます。

例外の扱いにも注意が要ります。`AsyncRelayCommand` は処理の中で起きた例外を既定では `ExecutionTask` というプロパティに持つだけで、画面にもログにも出しません。つまり、失敗しても黙って終わります。そこで、`LoadAsync` の中で `try` と `catch` を書き失敗したらログに出します（このあとの節で書きます）。

実行して「読み込み」を押すと読み込んでいる間もウィンドウが動きます。ボタンは灰色になり終わると一覧が入れ替わります。

## 別のスレッドからログを出す

`AssetScanner` の `log` を使う場所を作ります。`AssetViewModel` が `LogViewModel` を受け取れるようにして、読み込みの経過をログに出します。まず、受け渡しです。

`LogViewModel` を受け取る部分はこのあとの「作る係と使う係を分ける」で書きます。先にログを出す側の `LoadAsync` を書き換えます。

```csharp title="Asset/AssetViewModel.cs（変更）"
private async Task LoadAsync()
{
    var files = await _scanner.ScanAsync(AppContext.BaseDirectory, msg => _log.Add(LogLevel.Info, msg));
    Entries.Clear();
    foreach (var file in files) Entries.Add(file);
}
```

ここで `LogViewModel` に `Add` を作ります。何も考えずに書くとこうなります。

```csharp title="実験：スレッドを考えない Add（Editor には入れない）"
public void Add(LogLevel level, string message)
{
    Entries.Add(new LogEntry(DateTime.Now, level, message));
}
```

読み込むと `log` が呼ばれた瞬間に次のような例外でアプリが落ちます。

```text
System.NotSupportedException:
  このタイプの CollectionView は、Dispatcher スレッドとは異なるスレッドからの SourceCollection への変更をサポートしていません。
```

`log` は `Task.Run` の中、つまり別のスレッドから呼ばれています。そのスレッドから画面にバインドされた `ObservableCollection` を直接変更したからです。

### 深掘り：別のスレッドから UI を更新する

イベントやコールバックが別のスレッドから呼ばれるとき（エンジンのログなど）は、UI スレッドに仕事を頼みます。

```csharp
Application.Current.Dispatcher.InvokeAsync(() => Entries.Add(entry));   // 頼んだら待たずに戻る
await Application.Current.Dispatcher.InvokeAsync(() => Entries.Add(entry));   // 終わるまで await
```

`Invoke`（同期的に待つ）は UI スレッドが別の用事で待っていると、お互いに待ち合ってデッドロックする危険があります。基本は `InvokeAsync`（または `BeginInvoke`）を使います。これで `Add` を直します。

```csharp title="Log/LogViewModel.cs（変更）"
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

`CheckAccess()` は今のスレッドが UI スレッドかを調べます。どのスレッドから呼んでも安全な `Add` になりました。エンジンからのコールバックでログを受け取る第 50 章でもこの `Add` をそのまま使います。

コレクションを別のスレッドから触りたいときの方法は、もう 1 つあります。`BindingOperations.EnableCollectionSynchronization(collection, lockObject)` を呼んで WPF にロックの仕組みを教える方法です。

```csharp title="実験：EnableCollectionSynchronization（Editor には入れない）"
private readonly object _lock = new();
BindingOperations.EnableCollectionSynchronization(Entries, _lock);

// 別のスレッドから
lock (_lock) { Entries.Add(entry); }
```

`lock (_lock) { … }` は同じ `_lock` を持つ `lock` の中に同時に 1 つのスレッドしか入れないようにする文です。C++ の `std::lock_guard<std::mutex>` に当たり `{}` を抜けると自動でロックが外れます。ロックに使うのはこのように専用の `object` にするのが決まりで、`this` や文字列は避けます。外から同じ物を `lock` されて思わぬ待ちが起きるためです。`EnableCollectionSynchronization` は UI スレッドで呼び別のスレッドから `Add` を始める前に済ませます。迷ったら上の `Dispatcher` のほうが単純です。

## 作る係と使う係を分ける

`AssetViewModel` が `LogViewModel` と `AssetScanner` を必要とするようになりました。これまでの書き方なら使う側の `MainWindowViewModel` が、両方を `new` して渡すことになります。

```csharp title="手で組み立てる書き方（この章では採らない）"
Log = new LogViewModel();
AssetBrowser = new AssetViewModel(Log, new AssetScanner());
```

`AssetViewModel` が必要とするものが増えるたびに `MainWindowViewModel` の側も書き換えなければなりません。使うクラスが使われるクラスの作り方まで知っているのは、不自然です。

そこで、必要なものはコンストラクターの引数に書いて、<strong>作って渡す係</strong>を別に置きます。その係が第 12 章から裏で働いていた DI コンテナーです。DI は Dependency Injection（依存性注入）の略で、「必要なものを自分で作らず外から渡してもらう」という設計の考え方です。やることは 2 つです。

1 つ目はコンテナーにどのクラスを作れるかを教えておくことです。第 12 章で空のまま置いた `RegisterTypes` に書きます。

```csharp title="App.xaml.cs（変更）"
using Editor.Asset;
using Editor.Log;

protected override void RegisterTypes(IContainerRegistry containerRegistry)
{
    containerRegistry.RegisterSingleton<AssetScanner>();
    containerRegistry.RegisterSingleton<LogViewModel>();
    containerRegistry.RegisterSingleton<AssetViewModel>();
}
```

`RegisterSingleton` は「このクラスはアプリの間ずっと 1 つだけ作って、みんなで使い回す」という登録です。ログの一覧のようにみんなが同じものを見たいクラスは、これにします。`Singleton` と毎回作る `Transient` の違いは第 20 章で説明します。

2 つ目は欲しいものをコンストラクターの引数に書くことです。

```csharp title="Asset/AssetViewModel.cs（変更）"
private readonly LogViewModel _log;
private readonly AssetScanner _scanner;

public AssetViewModel(LogViewModel log, AssetScanner scanner)
{
    _log = log;
    _scanner = scanner;
    // 以下は前のとおり
}
```

`private readonly AssetScanner _scanner = new();` の行は消します。`MainWindowViewModel` のほうも同じように書き換えます。

```csharp title="MainWindowViewModel.cs（変更）"
public LogViewModel Log { get; }
public AssetViewModel AssetBrowser { get; }

public MainWindowViewModel(LogViewModel log, AssetViewModel assetBrowser)
{
    Log = log;
    AssetBrowser = assetBrowser;
    // 以下は前のとおり
}
```

`new MainWindowViewModel(...)` と書いている場所はどこにもありません。ViewModelLocator がコンテナーに「`MainWindowViewModel` を作って」と頼みコンテナーがコンストラクターの引数を見て、`LogViewModel` と `AssetViewModel` を作って渡しています。`AssetViewModel` に必要な `LogViewModel` と `AssetScanner` も同じやり方で渡されます。

なぜ登録だけで作れるのかいつ作られるのかインターフェースを挟む理由は何かは、第 18 章から順に説明します。いまは「必要なものは引数に書いて、`RegisterTypes` に登録する」とだけ覚えてください。

## 進み具合を画面に出す

読み込みに数秒かかるようになったので、進み具合を見せます。長い処理の途中経過を画面に出すときは、`IProgress<T>` を使います。`AssetScanner` に進み具合を報告する引数を足します。

```csharp title="Asset/AssetScanner.cs（変更）"
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

ビューモデルに進み具合のプロパティと `Progress<double>` を渡す処理を足します。

```csharp title="Asset/AssetViewModel.cs（変更）"
[ObservableProperty]
private double _progressValue;

[ObservableProperty]
private bool _isBusy;

[RelayCommand]
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
    catch (Exception e)
    {
        // コマンドの外へ例外を出さない
        _log.Add(LogLevel.Error, $"読み込みに失敗: {e.Message}");
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

読み込み中はパネルの下に細い進行バーが出て、右へ伸びていきます。

`Progress<T>` は作ったスレッド（ここでは UI スレッド）に自動で結果を戻してくれます。バックグラウンドの処理から `Report` を呼ぶだけで、UI スレッドへの切り替えを自分で書かなくて済みます。バーの `Value` が `Mode=OneWay` なのは `ProgressBar.Value` が読み取り専用のように振る舞うためです。

## キャンセルできるようにする

長い処理にはキャンセルの手段を用意しておくと親切です。`CancellationTokenSource` を作り `Token` を処理に渡しキャンセルするときに `Cancel()` を呼びます。

```csharp title="Asset/AssetScanner.cs（変更）"
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

```csharp title="Asset/AssetViewModel.cs（変更）"
private CancellationTokenSource? _cts;

// IsBusy が変わったら、キャンセルボタンの状態を聞き直す（IsBusy のフィールドに属性を足す）
[ObservableProperty]
[NotifyCanExecuteChangedFor(nameof(CancelCommand))]
private bool _isBusy;

[RelayCommand(CanExecute = nameof(IsBusy))]
private void Cancel() => _cts?.Cancel();

[RelayCommand]
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
    catch (Exception e)
    {
        _log.Add(LogLevel.Error, $"読み込みに失敗: {e.Message}");
    }
    finally
    {
        IsBusy = false;
        _cts.Dispose();
        _cts = null;
    }
}
```

`IsBusy` が変わったときキャンセルボタンの状態も聞き直してもらう必要があります。それは `[NotifyCanExecuteChangedFor(nameof(CancelCommand))]` が引き受けてくれます。`CanExecute = nameof(IsBusy)` は「`IsBusy` が `true` のときだけ押せる」という指定です。`bool` のプロパティの名前をそのまま渡せます。このとき、さきほどの `IsBusy` の定義はこの属性つきのものに置き換えます。

最後に、画面にキャンセルのボタンを足します。

```xml title="MainWindow.xaml（変更：読み込みボタンのあとに足す）"
<Button Content="キャンセル" Padding="12,2" Margin="4,0,0,0" Command="{Binding CancelCommand}" />
```

処理の側はところどころで `token.ThrowIfCancellationRequested()` を呼んで、キャンセルされたら `OperationCanceledException` で抜けます。この例外は「異常」ではなくキャンセルの合図なので、受け取る側で `catch` してログに残すだけにしています。

## 固まる原因の定番

- ボタンを押すと画面が固まる: 重い処理を UI スレッドで直接実行している
- `async` にしたのに固まる: `.Result` や `.Wait()` で結果を同期的に待っている（デッドロック）
- 勝手にアプリが落ちる: `async void` の中の例外が捕まっていない
- 「別のスレッドが所有しているため…」の例外: `Task.Run` の中や別スレッドのコールバックで画面を触った
- プログレスバーが動かない: 処理が UI スレッドで走っていて、描画が回らない

`.Result` と `.Wait()` は非同期の関数を同期的に待つ書き方ですが、UI スレッドで使うと「UI スレッドの再開を待つ処理」を「UI スレッドが待つ」というデッドロックになりやすいです。非同期の呼び出しは最後まで `await` でつなぐのが原則です。

### 深掘り：ConfigureAwait

ライブラリを書くときによく見る `await x.ConfigureAwait(false)` は、「`await` の後は元のスレッドに戻らなくてよい」という指定です。画面を触らない低レベルの関数では少し速くなりますが、画面を触る関数の中で付けてはいけません。アプリの画面側のコードでは付けない（既定のまま）で構いません。

## 動かして確かめる

`F5` で実行して次を確かめてください。

- 「アセット」のタブで「読み込み」を押すとボタンが灰色になり下に進行バーが伸びる。その間、ウィンドウの移動やタブの切り替えができる。
- 終わると一覧が入れ替わり `Editor.dll` などのファイルが並ぶ。「ログ」のタブに「N 個のファイルを見つけました」と出ている。
- 読み込み中に「キャンセル」を押すと止まり一覧は元のままで、ログに「読み込みをキャンセルしました」と出る。
- 読み込み中は「読み込み」のボタンが押せない（二重に始まらない）。

確かめ終わったら `AssetScanner` の `Thread.Sleep(20)` の行を消してください。ディスクが遅いふりをするための行で、本番には要りません。

??? failure "ログに足した瞬間にアプリが落ちる"
    `LogViewModel.Add` の中で `Dispatcher` を経由せず `Entries.Add` を直接呼んでいます。上の `CheckAccess` を使った版に直してください。

??? failure "キャンセルを押しても、止まらない"
    `ScanAsync` のループで `token.ThrowIfCancellationRequested()` を呼んでいるか `ScanAsync` に `_cts.Token` を渡しているかを確かめます。

??? failure "キャンセルボタンがずっと灰色のまま"
    `IsBusy` のフィールドに `[NotifyCanExecuteChangedFor(nameof(CancelCommand))]` が付いているかを確かめます。

## ここまでの Editor

```text
Editor/
├─ Asset/
│   ├─ AssetEntry.cs                 （第 16 章のまま）
│   ├─ AssetScanner.cs               フォルダーを非同期で読む（新規）
│   └─ AssetViewModel.cs             読み込み、進み具合、キャンセル
├─ Log/
│   ├─ LogEntry.cs
│   └─ LogViewModel.cs               どのスレッドからでも Add できる
├─ Scene/
│   └─ SceneObjectViewModel.cs
├─ MainWindowViewModel.cs            Log と AssetBrowser を受け取る
└─ MainWindow.xaml                   読み込み、キャンセル、進行バー
```

## この章のまとめ

- 重い処理は UI スレッドの外へ。待つ処理は `async` / `await`、計算は `Task.Run`。
- `await` の後は UI スレッドに戻るので、画面を触ってよい。`Task.Run` の中では触らない。
- `async void` はイベント ハンドラー以外では使わない。コマンドは `Task` を返すメソッドに `[RelayCommand]` を付ける（`AsyncRelayCommand` が生成され実行中は押せなくなる）。例外は処理の中で `catch` する。
- 経過は `Progress<T>`、中断は `CancellationToken`。
- 別のスレッドから UI を更新するときは `Dispatcher.InvokeAsync`。`.Result` / `.Wait()` で待たない。

次の章ではこの章で使った DI を「なぜ要るのか」から説明し直します。

[第 18 章 DI とは何か](18-di-basics.md) へ進みます。

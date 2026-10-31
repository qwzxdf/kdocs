---
title: 第 38 章 描画ループとスレッド
tags:
  - C#連携
---

# 第 38 章 描画ループとスレッド

第 37 章では、WPF の `CompositionTarget.Rendering` から `Tick` を呼びました。動きはしますが、エディタとして使うには問題があります。この章では、その問題を整理して、専用の描画スレッドでエンジンを動かす形に作り替えます。あわせて、「エンジンの関数をどのスレッドから呼んでよいのか」という、連携でいちばん事故の起きやすい約束事を決めます。

!!! info "このページを読む前に"
    - [第 37 章 HwndHost でビューポートを実装する](37-hwndhost.md)（前の章。ここまでの内容が前提になる）
    - [C# 連携](index.md)（このセクション全体の地図と、読む順番）


!!! abstract "この章で Editor に足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `Viewport/IRenderLoop.cs`（新規） | 描画ループの窓口（インターフェース） |
    | `Viewport/RenderLoop.cs`（新規） | 専用スレッドでエンジンを動かす描画ループ |


## UI スレッドで描くと困ること

WPF の画面を操作できるスレッドは、UI スレッド 1 本だけです。ボタンのクリックも、メニューも、ツリーの展開も、全部がこの 1 本で処理されます。そこで `Tick`（描画）も動かすと、次のような問題が起きます。

- 描画が重いと、UI が固まります。1 フレームの描画に 30 ミリ秒かかれば、その間、ボタンもメニューも反応しません。
- 逆に、UI が重いと、描画が止まります。ツリーに 1 万個の項目を追加している間、ビューポートが止まります。
- `Present` が垂直同期（VSync）を待つ間、UI スレッドも止まります。
- `CompositionTarget.Rendering` が呼ばれる頻度は、保証されていません。

そこで、描画専用のスレッドを作ります。UI スレッドと描画スレッドは別々に回るので、お互いを止めません。

```text
UI スレッド（WPF）            描画スレッド
  ボタン、メニュー、ツリー         while (動作中) {
  入力の受付                       キューの命令を実行
        │                          Tick(delta)       ← Present で VSync を待つ
        └─ 命令を積む ──▶ [キュー] ─▶ }
```

### エンジンを触るスレッドは、1 本だけにする

エンジン（`Engine`）は、複数のスレッドから同時に呼ぶことを想定していません。シーンを更新している最中に別のスレッドが描画すると、壊れます。そこで、次のルールを決めます。

- エンジンを触るのは、描画スレッドだけです。作成、`Tick`、`Resize`、シーンの編集、破棄。全部を同じスレッドから呼びます。
- UI スレッドは、エンジンを直接触りません。命令をキューに積みます（非同期）。結果が欲しいときは、描画スレッドに頼んで待ちます（同期）。
- 結果はコピーして UI に渡します。エンジンの内部のポインターを UI スレッドに渡しません。

この方針なら、エンジン側にロックを書く必要がありません。ロックの代わりに、スレッドを 1 本に決めてしまうのです。

## .NET のスレッドの道具

C++ の `std::thread` に当たるものを先に整理しておきます。

| C# | C++ で近いもの | 役目 |
| --- | --- | --- |
| `Thread` | `std::thread` | スレッド。`Start()` で開始、`Join()` で終了を待つ |
| `ManualResetEventSlim` | `std::condition_variable` とフラグ | 合図が来るまで待つ。`Set()` で合図、`Wait()` で待つ |
| `ConcurrentQueue<T>` | ロック付きの `std::queue` | 複数のスレッドから安全に出し入れできる待ち行列 |
| `CancellationTokenSource` | `std::stop_source` | 「止めて」という合図を渡す |
| `lock (obj) { ... }` | `std::lock_guard` | 同じ `obj` を持つ区画は、同時に 1 本しか入れない |
| `Interlocked` | `std::atomic` | 不可分な加算や交換 |

スレッドの作り方は、こうです。

```csharp
var thread = new Thread(() =>
{
    Console.WriteLine($"別のスレッド: {Environment.CurrentManagedThreadId}");
})
{
    Name = "Worker",
    IsBackground = true,
};
thread.Start();
thread.Join();
```

`IsBackground = true` のスレッドは、メイン スレッドが終わると強制的に終了させられます。`false`（既定）だと、そのスレッドが終わるまでプロセスが残ります。`Environment.CurrentManagedThreadId` は今のスレッドの番号で、どのスレッドで動いているかを確かめるのに便利です。

## IRenderLoop を作る

エンジンを動かす専用スレッドの窓口をインターフェースで定義します。

```csharp title="Viewport/IRenderLoop.cs（新規）"
using Editor.Engine;

namespace Editor.Viewport;

// エンジンを動かす専用スレッド。エンジンへの命令は、すべてここを通す。
public interface IRenderLoop : IDisposable
{
    bool IsRunning { get; }
    double FramesPerSecond { get; }

    // 描画スレッドを始める。engine の作成も、このスレッドで行う
    void Start(nint windowHandle, uint width, uint height);

    // 描画スレッドを止める。engine の破棄まで行ってから戻る
    void Stop();

    // 非同期：描画スレッドで実行するように頼み、待たずに戻る
    void Post(Action<IEngineService> command);

    // 同期：描画スレッドで実行し、結果を待つ（UI スレッドから、結果が要るときに使う）
    T Invoke<T>(Func<IEngineService, T> query);
}
```

実装は 3 つに分けて見ます。まず、状態とキューです。

```csharp title="Viewport/RenderLoop.cs（新規）"
using System.Collections.Concurrent;
using System.Diagnostics;
using Editor.Engine;
using Editor.Log;

namespace Editor.Viewport;

public sealed class RenderLoop : IRenderLoop
{
    private readonly IEngineService _engine;
    private readonly ILogService _log;
    private readonly ConcurrentQueue<Action> _commands = new();
    private readonly ManualResetEventSlim _wake = new(false);

    private Thread? _thread;
    private volatile bool _running;
    private double _fps;

    public RenderLoop(IEngineService engine, ILogService log)
    {
        _engine = engine;
        _log = log;
    }

    public bool IsRunning => _running;
    public double FramesPerSecond => Volatile.Read(ref _fps);
```

`ConcurrentQueue<Action>` は、複数のスレッドから安全に出し入れできる待ち行列で、`Enqueue` で追加し、`TryDequeue` で取り出します。`volatile bool _running` は、別のスレッドが変えた値がすぐ見えるようにする指定で、単純なフラグに向いています。`Volatile.Read(ref _fps)` は、別のスレッドが書いた `double` を安全に読むための関数です。

次は、開始と停止です。

```csharp
    public void Start(nint windowHandle, uint width, uint height)
    {
        if (_thread != null) throw new InvalidOperationException("すでに開始しています");

        _running = true;
        _thread = new Thread(() => Run(windowHandle, width, height))
        {
            Name = "Render",
            IsBackground = false,
        };
        _thread.Start();
    }

    public void Stop()
    {
        if (_thread == null) return;
        _running = false;
        _wake.Set();            // 待っていたら起こす
        _thread.Join();         // 描画スレッドがエンジンを破棄して終わるまで待つ
        _thread = null;
    }

    public void Dispose() => Stop();
```

`Join()` は、そのスレッドが終わるまで呼び出し側が待つ関数です。これで、`Stop()` から戻った時点で、エンジンが破棄済みだと保証できます。`IsBackground = false` にしているのは、GPU の後片付けが終わる前にプロセスが閉じないようにするためです。

そして、スレッドの本体です。

```csharp
    private void Run(nint windowHandle, uint width, uint height)
    {
        try
        {
            _engine.Initialize(windowHandle, width, height);       // 作るのも描画スレッドで
        }
        catch (Exception e)
        {
            _log.Error($"エンジンの初期化に失敗: {e.Message}");
            _running = false;
            return;
        }
        _log.Info($"エンジンを初期化しました（{width}x{height}）");

        var clock = Stopwatch.StartNew();
        TimeSpan previous = clock.Elapsed;
        TimeSpan fpsStart = previous;
        int fpsFrames = 0;

        while (_running)
        {
            // ① 溜まっている命令をすべて実行する
            while (_commands.TryDequeue(out var command))
            {
                try { command(); }
                catch (Exception e) { _log.Error($"命令の実行に失敗: {e.Message}"); }
            }

            // ② 経過時間を測って、1 フレーム進める
            TimeSpan now = clock.Elapsed;
            float delta = (float)Math.Min((now - previous).TotalSeconds, 0.1);   // 止まっていた後の巨大な値を防ぐ
            previous = now;

            try { _engine.Tick(delta); }
            catch (Exception e)
            {
                _log.Error($"Tick に失敗: {e.Message}");
                break;
            }

            // ③ FPS の計測（1 秒ごと）
            fpsFrames++;
            if ((now - fpsStart).TotalSeconds >= 1.0)
            {
                Volatile.Write(ref _fps, fpsFrames / (now - fpsStart).TotalSeconds);
                fpsFrames = 0;
                fpsStart = now;
            }
        }

        // ④ 残りの命令を捨て、エンジンを破棄する（描画スレッドで）
        while (_commands.TryDequeue(out _)) { }
        _engine.Dispose();
        _running = false;
        _log.Info("エンジンを破棄しました");
    }
```

1 周ごとに、溜まっている命令をすべて実行し、経過時間を測って `Tick` を呼びます。`delta` の上限を 0.1 秒にしているのは、デバッガーで止めたあとなどに、巨大な値が渡されるのを防ぐためです。作成から破棄まで、エンジンを触る処理が全部この 1 本のスレッドの中に収まっているのが、ポイントです。

最後に、命令を積む側です。

```csharp
    public void Post(Action<IEngineService> command)
    {
        _commands.Enqueue(() => command(_engine));
        _wake.Set();
    }

    public T Invoke<T>(Func<IEngineService, T> query)
    {
        if (Environment.CurrentManagedThreadId == _thread?.ManagedThreadId)
        {
            return query(_engine);               // すでに描画スレッドなら、そのまま実行
        }

        T result = default!;
        Exception? error = null;
        using var done = new ManualResetEventSlim(false);

        _commands.Enqueue(() =>
        {
            try { result = query(_engine); }
            catch (Exception e) { error = e; }
            finally { done.Set(); }
        });
        _wake.Set();

        done.Wait();                             // 描画スレッドが実行するまで待つ
        if (error != null) throw new InvalidOperationException("エンジンの命令に失敗しました", error);
        return result;
    }
}
```

`Post` は積んだらすぐ戻る非同期版で、編集のように結果が要らない命令に使います。`Invoke` は、積んで完了を待ち、結果を返す同期版です。名前の取得のように、結果が必要な呼び出しに使います。

`Invoke` の中のラムダ式は、外の変数（`result`、`error`）を捕まえて書き換えています（C++ の `[&]` と同じです）。`finally { done.Set(); }` が大事で、これを忘れると、例外が起きたときに永遠に待ちます。`default!` は、型の既定値を入れつつ、「`null` ではない」とコンパイラーに伝える書き方です。

!!! warning "Invoke でデッドロックしないために"
    描画スレッドが UI スレッドの結果を待っている最中に UI スレッドが `Invoke` で描画スレッドを待つと、お互いに待ち合って止まります。ルールは 1 つです。描画スレッドは、UI スレッドを待たない。描画スレッドから UI に知らせるときは、`Dispatcher.BeginInvoke`（待たない）か、イベント（第 24 章）を使います。

## ViewportViewModel を作り替える

`ViewportViewModel` を `IRenderLoop` を使う形にします。`IEngineService` を直接触るのは、`RenderLoop` だけになります。

```csharp
public class ViewportViewModel
{
    private readonly IRenderLoop _loop;

    public ViewportViewModel(IRenderLoop loop)
    {
        _loop = loop;
    }

    public void OnWindowReady(nint hwnd, uint width, uint height)
    {
        _loop.Start(hwnd, width, height);          // スレッドを作って、エンジンを作る
    }

    public void OnWindowResized(uint width, uint height)
    {
        _loop.Post(engine => engine.Resize(width, height));   // 描画スレッドで実行される
    }

    public void OnWindowDestroying()
    {
        _loop.Stop();                              // スレッドを止め、エンジンの破棄まで待つ
    }
}
```

`CompositionTarget.Rendering`、`Stopwatch`、`_previous` は要らなくなるので、削除します。`App.xaml.cs` の `RegisterTypes` に、登録を足します。

```csharp
containerRegistry.RegisterSingleton<IRenderLoop, RenderLoop>();
```

`engine => engine.Resize(width, height)` は、描画スレッドで実行される関数を渡しています。`width` と `height` はラムダが捕まえますが、`uint` は値型でコピーされるので、UI スレッドの値のコピーが描画スレッドに渡る形になり、安全です。

## FPS をステータス バーに出す

描画スレッドから UI を直接更新することはできません。ここでは、UI スレッドのタイマーで値を読みに行く（ポーリングする）形にします。

```csharp
using System.Windows.Threading;

private readonly DispatcherTimer _statusTimer;

public MainWindowViewModel(IRenderLoop loop /*, ほか */)
{
    _statusTimer = new DispatcherTimer { Interval = TimeSpan.FromMilliseconds(500) };
    _statusTimer.Tick += (_, _) =>
        StatusText = loop.IsRunning ? $"{loop.FramesPerSecond:F1} FPS" : "停止中";
    _statusTimer.Start();
}
```

`DispatcherTimer` は、UI スレッドで一定間隔ごとに `Tick` を起こすタイマーです。UI を触ってよいスレッドで動きます。更新が頻繁な値は、描画スレッドから UI へ送る（`Dispatcher.BeginInvoke`）より、UI が読みに行くほうが、UI の負荷を調整しやすくなります。

## VSync と遅延

`Present(1, 0)` は、画面の更新（VSync）を待つ関数です。60 Hz のモニターなら、描画スレッドは 1 フレーム約 16.7 ミリ秒ごとに待つので、描画スレッドが自然に 60 fps で回ります。UI スレッドは別なので、待たされません。消費電力が低く、ティアリング（画面のずれ）も起きないので、エディタにはこれで十分です。

`Present(0, DXGI_PRESENT_ALLOW_TEARING)` なら VSync を待たず最速になりますが、ティアリングが出ます。可変リフレッシュ レート（G-Sync など）向けです。さらに遅延を減らしたいときは、待機可能スワップ チェーン（`DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT`）という手段もありますが、この教材では触れません。

## 約束が守られているかをエンジン側でも確かめる

「エンジンを触るのは 1 本」という約束は、守られているかを確かめる手段がないと、いつか破られます。`Engine` の Debug ビルドにスレッド ID の検査を入れておきます。

```cpp
// Engine.cpp の Impl
struct Engine::Impl {
  // ...
  std::thread::id owner = std::this_thread::get_id();    // 作ったスレッド
};

// 各関数の先頭（Debug のみ）
#ifdef _DEBUG
#define ENGINE_CHECK_THREAD(impl) \
  do { if ((impl)->owner != std::this_thread::get_id()) { LogError("別のスレッドから呼ばれました"); __debugbreak(); } } while (0)
#else
#define ENGINE_CHECK_THREAD(impl) ((void)0)
#endif
```

`Tick` や `Resize` の先頭でこれを呼びます。UI スレッドから間違って呼ぶと、その場でデバッガーが止まり、コール スタックから原因が分かります。`__debugbreak()` は MSVC のデバッガーを止める命令で、`do { ... } while (0)` は複数の文を 1 つの文として扱えるマクロの定番の書き方です。

## 動かして確かめる

- 起動すると、第 37 章と同じようにビューポートの色が変わる。
- ステータス バーに「60.0 FPS」のような表示が出る（モニターのリフレッシュ レートに近い値）。
- 描画中でも、メニューや仕切りが滑らかに動く。UI スレッドを止めても（`Thread.Sleep(2000)` を呼ぶテスト用ボタンなど）、ビューポートは動き続ける。
- 閉じると、描画スレッドが止まってエンジンが破棄され、プロセスが終了する。
- UI スレッドから `Tick` を呼んでみると、Debug でブレークする。

??? failure "終了するときに固まる"
    `Stop()` が描画スレッドの終了を待っている最中に描画スレッドが UI スレッドの結果を待っている可能性があります。描画スレッドから UI を待たないようにします。あるいは、`Invoke` の中で例外が起きたのに `done.Set()` が呼ばれていません（`finally` が必要です）。

??? failure "リサイズ中に絵が引き伸ばされる"
    正常です。DXGI のフリップ モデルは、`ResizeBuffers` が終わるまで古いバッファーを引き伸ばして出します。気になるなら、リサイズの命令を複数積まずに、最新の大きさだけを保持します（デバウンス）。

??? failure "`Invoke` で UI が固まる"
    描画スレッドが `Present` の VSync を待っている間は、命令を処理できません。`Invoke` は 1 フレーム分（約 16 ミリ秒）待たされます。大量の `Invoke` を続けず、`Post` にするか、1 回の命令にまとめます。

??? failure "例外が出ても、描画スレッドが黙って止まる"
    スレッドの中の例外は、呼び出し元に伝わりません。`Run` の中で `try/catch` して、必ずログに書きます。

## この章のまとめ

- エンジンを触るスレッドは、描画スレッド 1 本にする。UI スレッドは命令を積む。
- 命令は `Post`（非同期）と `Invoke`（同期）で送る。描画スレッドは UI を待たない。
- 破棄も描画スレッドの中で行い、`Stop()` が `Join` で待つ。
- `Present(1, 0)` が、描画スレッドの速さを決める。

次の章では、ビューポートのマウスとキーボードを受け取って、カメラを動かします。入力も、描画スレッドに送る形にします。

[第 39 章 入力とエディタ カメラ](39-input-camera.md) へ進みます。

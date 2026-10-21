---
title: 第 18 章 描画ループとスレッド
tags:
  - C#連携
---

# 第 18 章 描画ループとスレッド

第 17 章では WPF の `CompositionTarget.Rendering` で、`Tick` を呼びました。動きますが<strong>エディタとして使うには問題</strong>があります。この章ではその問題を整理し<strong>専用の描画スレッド</strong>でエンジンを動かす形に作り替えます。同時に「エンジンの関数をどのスレッドから呼んでよいか」という連携で最も事故が起きやすい約束事を決めます。

## この章の考え方

### UI スレッドで描くと何が困るか

WPF の画面を操作できるのは、<strong>UI スレッド</strong>1 本だけです。ボタンのクリック、メニュー、ツリーの展開、すべてが UI スレッドで処理されます。ここで `Tick`（描画）も実行すると、次の問題が起きます。

| 問題 | 内容 |
| --- | --- |
| 描画が重いと UI が固まる | 1 フレームの描画に 30 ms かかればその間、ボタンもメニューも反応しない |
| UI が重いと描画が止まる | ツリーに 1 万個の項目を追加する間、ビューポートが止まる |
| `Present` の待ち | 垂直同期（VSync）を待つ間、UI スレッドが止まる |
| 更新頻度が不安定 | `CompositionTarget.Rendering` の呼ばれる頻度は保証されない |

そこで、<strong>描画専用のスレッド</strong>を作ります。UI スレッドと描画スレッドは別々に回るので、お互いを止めません。

```text
UI スレッド（WPF）            描画スレッド
  ボタン、メニュー、ツリー         while (動作中) {
  入力の受付                       キューの命令を実行
        │                          Tick(delta)       ← Present で VSync を待つ
        └─ 命令を積む ──▶ [キュー] ─▶ }
```

### 守るべき原則：エンジンを触るスレッドは 1 本

エンジン（`Engine`）は<strong>複数のスレッドから同時に呼ぶことを想定していません</strong>。シーンのデータを更新している最中に別のスレッドが描画すると、壊れます。

| 原則 | 内容 |
| --- | --- |
| <strong>エンジンを触るのは描画スレッドだけ</strong> | `Create`、`Tick`、`Resize`、シーンの編集、`Destroy`。すべて同じスレッドから |
| UI スレッドは直接触らない | 命令を<strong>キューに積む</strong>（非同期）。結果が欲しいときは描画スレッドに頼んで、待つ（同期） |
| 結果はコピーして UI に渡す | エンジン内部のポインターを UI スレッドに渡さない |

この原則があればエンジン側に<strong>ロックを書く必要がありません</strong>。ロックの代わりに<strong>スレッドを 1 本に決める</strong>方針です。

## この章のゴール

- `IRenderLoop` サービスを作り描画スレッドで `Tick` を回す。
- UI スレッドから描画スレッドへ命令を送れる（非同期・同期）。
- 画面の更新と描画を別のスレッドで動かし、お互いを止めない。
- FPS を計測してステータス バーに表示する。

## 手順 1：.NET のスレッドの基礎

C++ の `std::thread` に当たるものを先に整理します。

| C# | C++ | 説明 |
| --- | --- | --- |
| `Thread` | `std::thread` | スレッド。`Start()` で開始、`Join()` で終了を待つ |
| `ManualResetEventSlim` | `std::condition_variable` + フラグ | 「合図が来るまで待つ」仕組み。`Set()` で合図、`Wait()` で待つ |
| `ConcurrentQueue<T>` | ロック付き `std::queue` | 複数のスレッドから安全に出し入れできる待ち行列 |
| `CancellationTokenSource` | `std::stop_source` | 「止めて」という合図を渡す仕組み。`Cancel()` で通知、`Token` を渡す |
| `lock (obj) { … }` | `std::lock_guard` | 同じ `obj` を持つ区画は、同時に 1 本しか入れない |
| `Interlocked` | `std::atomic` | 不可分な加算、交換 |
| `volatile` | （近いのは `std::atomic` の relaxed） | 最新の値を読むことを保証。複雑な用途には使わない |

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `new Thread(() => {…})` | ラムダ式を渡して、スレッドを作る |
| `IsBackground` | `true` のスレッドは<strong>メイン スレッドが終われば強制終了</strong>される。`false`（既定）だとそのスレッドが終わるまでプロセスが残る |
| `Environment.CurrentManagedThreadId` | 今のスレッドの番号。どのスレッドで動いているか確認できる |

## 手順 2：IRenderLoop を作る

`Services\IRenderLoop.cs`:

```csharp
namespace Editor.Services;

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

実装 `Services\RenderLoop.cs`:

### 状態とキュー

```csharp
using System.Collections.Concurrent;
using System.Diagnostics;

namespace Editor.Services;

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `ConcurrentQueue<Action>` | スレッドをまたいで、安全に使える待ち行列。`Enqueue`（追加）、`TryDequeue`（取り出し） |
| `ManualResetEventSlim` | 待っているスレッドを起こす合図。`Set()` で起こし `Reset()` で戻し `Wait(ms)` で待つ |
| `volatile bool _running` | 別のスレッドからの変更が、すぐ見えるようにする指定。単純なフラグ向き |
| `Volatile.Read(ref _fps)` | 別のスレッドが書いた `double` を安全に読む |
| `new(false)` | 対象型 new（第 7 章）。引数の `false` は「最初は合図なし」 |

### 開始と停止

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
        _thread.Join();         // 描画スレッドが、エンジンを破棄して終わるまで待つ
        _thread = null;
    }

    public void Dispose() => Stop();
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Thread.Join()` | そのスレッドが終わるまで、<strong>呼び出し側が待つ</strong>。終了後にエンジンが破棄済みであることを保証できる |
| `IsBackground = false` | 描画スレッドが終わる前にプロセスが閉じないようにする（GPU の後片付けのため） |

### スレッドの本体

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
            // ① 溜まっている命令を、すべて実行する
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Stopwatch.StartNew()` | 作ってすぐに計測を始める |
| `while (_commands.TryDequeue(out var command))` | キューが空になるまで、取り出して実行する。`TryDequeue` は取れたら `true` |
| `Math.Min(…, 0.1)` | `delta` の上限を 0.1 秒にする。デバッガーで止めた後などに `delta` が巨大になるのを防ぐ |
| `Volatile.Write` | 別のスレッドが読む値を安全に書く |
| `while (…TryDequeue(out _)) { }` | 残りを捨てる。`out _` は結果を使わない |
| 1 つのスレッドで完結 | <strong>作成・Tick・命令・破棄が、すべて描画スレッド</strong>。エンジンへのスレッド規約が守られる |

### 命令を積む（非同期と同期）

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `Post` | 非同期。積んだらすぐ戻る。結果は返らない。編集の命令に使う |
| `Invoke<T>` | 同期。積んで完了を待ち結果を返す。名前の取得のような<strong>結果が必要な</strong>呼び出しに使う |
| `default!` | 型の既定値（`null` や 0）。`!` は「`null` でないと私が保証する」という警告の抑制 |
| クロージャ | ラムダ式が、外の変数（`result`、`error`）を<strong>捕まえて</strong>、書き換える。C++ の `[&]` と同じ |
| `finally { done.Set(); }` | 成功しても失敗しても、必ず合図する。`finally` を忘れると永久に待つ（デッドロック） |
| `ManagedThreadId` | スレッドの番号。自分が描画スレッドかどうかを調べる |
| `new InvalidOperationException("…", error)` | 元の例外を<strong>内側の例外</strong>（`InnerException`）として保存する |

!!! warning "Invoke のデッドロック"
    描画スレッドが UI スレッドの結果を待ちながら、UI スレッドが `Invoke` で描画スレッドを待つと<strong>お互いに待って止まります</strong>（デッドロック）。ルールは 1 つです。<strong>描画スレッドは UI スレッドを待たない</strong>。描画スレッドから UI に知らせるときは、`Dispatcher.BeginInvoke`（待たない）かイベント（第 10 章）を使います。

## 手順 3：ViewportViewModel を作り替える

`ViewportViewModel` を `IRenderLoop` を使う形にします。`IEngineService` を直接触るのは `RenderLoop` だけです。

```csharp
public class ViewportViewModel : BindableBase
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

`CompositionTarget.Rendering`、`Stopwatch`、`_previous` は不要になったので削除します。

`App.xaml.cs` の `RegisterTypes` で登録します。

```csharp
containerRegistry.RegisterSingleton<IRenderLoop, RenderLoop>();
```

| 新しく出てきたもの | 説明 |
| --- | --- |
| ラムダ式で命令を渡す | `engine => engine.Resize(width, height)` は、<strong>描画スレッドで実行される関数</strong>を渡している。`Post` はすぐに戻る |
| `width`、`height` をラムダが捕まえる | UI スレッドの値のコピーが、描画スレッドに渡る。`uint` は値型でコピーされるので安全 |

## 手順 4：描画スレッドを止めずに UI の更新を受ける

ステータス バーに FPS を表示したい。描画スレッドから UI を直接更新できないので、<strong>UI スレッドのタイマーで、値を読みに行きます</strong>（ポーリング）。

`MainWindowViewModel` に追加します。

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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `DispatcherTimer` | UI スレッドで、一定間隔で `Tick` イベントを起こすタイマー。UI を触ってよい |
| `TimeSpan.FromMilliseconds(500)` | 500 ミリ秒の時間の長さ |
| `{value:F1}` | 補間文字列の書式。小数 1 桁 |
| 方式の選択 | <strong>描画スレッドから UI へ送る</strong>（`Dispatcher.BeginInvoke`）と<strong>UI が読みに行く</strong>（ポーリング）の二つ。更新の頻度が高い値はポーリングのほうが、UI の負荷を制御しやすい |

## 手順 5：VSync と遅延

`Present(1, 0)` は<strong>画面の更新（VSync）を待つ</strong>関数です。描画スレッドが 60 Hz のモニターで 1 フレーム 16.7 ms ごとに待つので、<strong>描画スレッドが自然に 60 fps で回ります</strong>。UI スレッドは別なので待たされません。

| 設定 | 動作 |
| --- | --- |
| `Present(1, 0)` | VSync を待つ。消費電力が低くティアリング（画面のずれ）なし |
| `Present(0, DXGI_PRESENT_ALLOW_TEARING)` | VSync を待たない。最速。ティアリングあり。可変リフレッシュ レート（G-Sync など）向き |

エディタでは `Present(1, 0)` で十分です。CPU の使用率が下がります。

遅延をさらに減らしたい場合は<strong>待機可能スワップ チェーン</strong>（`DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT`）を使い、`GetFrameLatencyWaitableObject` で待つ方法があります。`SetMaximumFrameLatency(1)` と組み合わせます。この教材では触れません。

## 手順 6：エンジン側にもスレッド検査を入れる

「エンジンを触るのは 1 本」という約束は、<strong>守られているか確かめる</strong>手段が欲しくなります。`Engine` の Debug ビルドにスレッド ID の検査を入れておきます。

```cpp
// Engine.cpp の Impl
struct Engine::Impl {
  // …
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

| 新しく出てきたもの | 説明 |
| --- | --- |
| `std::thread::id` / `std::this_thread::get_id()` | スレッドの識別子 |
| `__debugbreak()` | デバッガーをその場で止める（MSVC）。呼び出し元のスレッドが分かる |
| `do { … } while (0)` | 複数の文を 1 つの文として扱えるマクロの定番の書き方 |

`Create` したスレッドを覚えておき `Tick`、`Resize` などの先頭で検査します。UI スレッドから誤って呼ぶと<strong>その場で止まり</strong>、コール スタックから原因が分かります。

## 動作確認

| 見る所 | 期待する結果 |
| --- | --- |
| 起動 | 第 17 章と同じく、ビューポートの色が変わる |
| ステータス バー | 「60.0 FPS」などが出る（モニターのリフレッシュ レートに近い値） |
| UI の応答 | 描画中でもメニューや仕切りが、滑らかに動く |
| 重い UI 処理 | UI スレッドを止めても（例：`Thread.Sleep(2000)` を呼ぶボタン）、ビューポートは動き続ける |
| 閉じる | 描画スレッドが止まりエンジンが破棄されプロセスが終了する |
| スレッド検査 | UI スレッドから `Tick` を呼ぶと Debug でブレークする |

## よくあるミス

??? failure "終了するとき固まる"
    `Stop()` が描画スレッドの終了を待っている最中に描画スレッドが UI スレッドの結果を待っている。描画スレッドから UI を待たない。または、`Invoke` の中で例外が起きて `done.Set()` が呼ばれなかった（`finally` が必要）。

??? failure "リサイズ中に絵が引き伸ばされる"
    正常です。DXGI のフリップ モデルは `ResizeBuffers` が完了するまで、古いバッファーを引き伸ばす。気になるときはリサイズの命令を `Post` で複数積まず最新の大きさだけを保持する（デバウンス）。

??? failure "`Invoke` で、UI が固まる"
    描画スレッドが `Present` の VSync を待つ間、命令を処理できない。`Invoke` は 1 フレーム分（約 16 ms）待つ。大量の `Invoke` を続けて呼ばず `Post` にするか 1 回の命令にまとめる。

??? failure "例外が出ても、描画スレッドが黙って止まる"
    スレッドの中の例外は<strong>呼び出し元に伝わらず</strong>、プロセスを落とすか無視される。`Run` の中で `try/catch` して必ずログに書く。

## この章のまとめ

- エンジンを触るスレッドは<strong>描画スレッド 1 本</strong>。UI スレッドは命令を積む。
- `Post`（非同期）と `Invoke`（同期）で、命令を送る。描画スレッドは UI を待たない。
- 破棄は描画スレッドの中で行い `Stop()` が `Join` で待つ。
- `Present(1, 0)` が描画スレッドの速度を決める。

## 次の章へ

次の章（[第 19 章 入力とエディタ カメラ](19-input-camera.md)）では、ビューポートのマウスとキーボードを受け取りカメラを動かします。入力も描画スレッドに送る形にします。

---
title: 第 60 章 TCP 編 2：Prest のエディタに組み込む
tags:
  - C#連携
  - TCP
---

# 第 60 章 TCP 編 2：Prest のエディタに組み込む

第 59 章で、エンジンの exe とエディタが TCP で会話できるようになりました。ただしそれは、確認用のコンソール アプリの上の話です。この章では、同じ仕組みを<strong>実際のエディタ（Prest）の構造に組み込みます</strong>。エディタが起動したらエンジンのプロセスを起動して、ポートが分かるまで待って繋ぎ、これまで P/Invoke で呼んでいた `IEngineService` の中身を、通信に置き換えます。

この章でも、まず動かすことを優先します。合言葉による守りや、エンジンが固まったときの見つけ方は、動くものができたあとの第 61 章で足します。

!!! info "このページを読む前に"
    - [第 59 章 TCP 編 1：最小のエンジンとエディタを繋ぐ](59-tcp-base.md)（前の章。`EngineClient`、`TcpTransport`、サーバー）
    - [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)（任意。差し替えの考え方）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）

!!! abstract "この章で足す・直すもの"
    - `Editor/Engine/EngineProcess.cs`（新規）：エンジンの exe を起動して、ポート番号を受け取る
    - `Editor/Engine/RemoteEngineService.cs`（新規）：`IEngineService` を、`EngineClient` 越しに実装する
    - `Editor/App.xaml.cs`（変更）：登録を `PInvokeEngineService` から差し替える
    - `EngineHost/TcpServer.cpp`（変更）：`Dispatch` に、エンジンを動かす命令を足す

## いまの構造を見る

Prest のエディタは、エンジンを `IEngineService` の窓口から使っています。

```csharp title="Editor/Engine/IEngineService.cs（いまのもの）"
public interface IEngineService : IDisposable
{
	bool IsRunning { get; }

	void Initialize(nint windowHandle, uint width, uint height);

	void Resize(uint width, uint height);
	void Tick(float dt);
    ulong FrameCount { get; }
    void SendInput(int type, int button, float x, float y, float delta, int key, uint modifiers);
}
```

実装は `PInvokeEngineService` で、`PrestAPI.dll` の `pe_engine_create` や `pe_engine_tick` を直接呼んでいます。呼び出し側の `RenderLoop` は `IEngineService` しか知りません。だから、別プロセスにするときも、<strong>呼び出し側を変えずに、`IEngineService` の実装だけを差し替えれば済みます</strong>。窓口の後ろ側を替えるだけという、第 54 章の考え方がそのまま使えます。

もう 1 つ、確かめておくことがあります。`RenderLoop` は `IEngineService` の各メソッドを、`Render` という名前の専用のスレッドから呼びます（`RenderLoop.Run` の中で `_engine.Initialize` を呼んでいます）。UI スレッドではありません。だから、`IEngineService` の同期的なメソッドの中で通信の返事を待っても、ウィンドウは固まりません。第 59 章で「同期のコードから呼ぶときは UI スレッドを避ける」と書いた条件が、ここでは満たされています。

## 1. エンジンを起動する

エンジンの exe を起動して、標準出力の `port=NNNN` を受け取る部分です。第 59 章の `Program.cs` に書いた数行を、失敗にも強い形にします。

```csharp title="Editor/Engine/EngineProcess.cs（新規）"
using System.Diagnostics;

namespace Prest.Editor.Engine;

public sealed record StartedEngine(Process Process, int Port);

public static class EngineProcess
{
    // エンジンを起動して、待ち受けのポートが分かるまで待つ
    public static async Task<StartedEngine> StartAsync(string exePath, string arguments, TimeSpan timeout)
    {
        var info = new ProcessStartInfo(exePath, arguments)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardOutput = true,    // 待ち受けのポート番号を受け取る
            RedirectStandardError = true,     // ログ用。読み手がいないと、エンジンの書き込みが止まる
        };
        Process process = Process.Start(info) ?? throw new InvalidOperationException("エンジンを起動できません");
        process.BeginErrorReadLine();         // 標準エラーは、読み捨てる（ログに回すなら、ここで受ける）
```

`RedirectStandardOutput = true` で、エンジンの標準出力をエディタが読める状態にします。`RedirectStandardError` も有効にして `BeginErrorReadLine` を呼んでいるのは、読み手がいないとパイプのバッファが満杯になって、エンジンのログの書き込みが止まってしまうからです。ここでは読み捨てるだけにしてあります。エディタのログに流したいときは、この行にイベントを付けます。

```csharp title="Editor/Engine/EngineProcess.cs（続き）"
        try
        {
            Task<string?> lineTask = process.StandardOutput.ReadLineAsync();   // 1 行目（port=NNNN）を待つ
            Task exitTask = process.WaitForExitAsync();                         // 起動の途中で終わる場合に備える
            Task finished = await Task.WhenAny(lineTask, exitTask, Task.Delay(timeout)).ConfigureAwait(false);

            // 出力の終わり（null）と終了は、ほぼ同時に起きる。どちらも「起動中に終わった」として扱う
            if (finished == lineTask && await lineTask.ConfigureAwait(false) is { } line)
            {
                // 約束の形（port=数字）でなければ、エンジンではない何かが書いたと見なす
                if (!line.StartsWith("port=") || !int.TryParse(line.AsSpan("port=".Length), out int port))
                {
                    throw new InvalidDataException($"想定外の出力: {line}");
                }
                return new StartedEngine(process, port);
            }
            if (finished == lineTask || finished == exitTask)
            {
                await process.WaitForExitAsync().ConfigureAwait(false);       // 終了コードが確定するまで待つ
                throw new InvalidOperationException($"エンジンが起動中に終了しました（終了コード 0x{process.ExitCode:X}）");
            }
            // 残るは時間切れ。プロセスは生きているが、待ち受けを始めない
            throw new TimeoutException($"{timeout.TotalSeconds} 秒以内に、エンジンが待ち受けを始めませんでした。");
        }
        catch
        {
            try { process.Kill(entireProcessTree: true); } catch (InvalidOperationException) { }   // 失敗したら残さない
            process.Dispose();
            throw;
        }
    }
}
```

`Task.WhenAny` で、3 つのうち最初に終わったものを待ちます。「ポートの行が来た」「プロセスが終わった」「時間切れ」です。標準出力を読む作りなら、短い間隔で `HasExited` を見て回る必要がなく、3 つのどれが先かが一度に分かります。

プロセスが起動の途中で終わった場合は、標準出力が閉じられて、`lineTask` が `null` で終わります。`exitTask` もほぼ同時に終わります。`WhenAny` はどちらが先に見えるか決まっていないので、どちらも「起動中に終わった」として扱い、終了コードを例外に載せます。

手元で 4 つの場合を確かめました。

```text title="起動の確認（実測）"
[A] 起動から port 通知まで 28 ms, port=53683
[B] 起動してすぐ終了: InvalidOperationException: エンジンが起動中に終了しました（終了コード 0x3） (49 ms)
[C] 何も出力しない: TimeoutException: 1 秒以内に、エンジンが待ち受けを始めませんでした。 (1051 ms)
[D] 想定外の出力: InvalidDataException: 想定外の出力: hello (41 ms)
```

正常なら 28 ミリ秒でポートが分かりました。起動してすぐ終わる場合は、終了コードつきの例外になります。何も出力しない場合は、指定した 1 秒で時間切れです。「待たされたあげくの時間切れ」ではなく、「すぐ分かる、理由つきの失敗」になるという設計が、そのまま働いています（B は `cmd /c exit 3`、C は 5 秒黙る `cmd`、D は `echo hello` で再現しました）。

## 2. IEngineService を通信で実装する

次が、`IEngineService` の TCP 版です。各メソッドを、命令 1 つに対応させます。

- `Initialize` は `init`（`window`、`width`、`height`）
- `Resize` は `resize`（`width`、`height`）
- `Tick` は `tick`（`dt`）
- `FrameCount` は `frame_count`（引数なし。`result` に数を返す）
- `SendInput` は `input`（`type`、`button`、`x`、`y`、`delta`、`key`、`modifiers`）

```csharp title="Editor/Engine/RemoteEngineService.cs（新規）"
using System.Text.Json;

namespace Prest.Editor.Engine;

// IEngineService を、別プロセスのエンジンに繋いで実装する。呼び出し側（RenderLoop）は、これまでと同じ
public sealed class RemoteEngineService : IEngineService
{
    private readonly string _exePath;
    private StartedEngine? _started;
    private EngineClient? _client;

    public RemoteEngineService(string enginePath) => _exePath = enginePath;

    public bool IsRunning => _client is not null;

    // 命令を 1 つ送って、返事を待つ。Render スレッドから呼ぶので、同期で待ってよい
    private JsonElement Call(string cmd, object? args = null)
    {
        var client = _client ?? throw new InvalidOperationException("エンジンが初期化されていません");
        return client.RequestAsync(cmd, args).GetAwaiter().GetResult();
    }

    public ulong FrameCount => Call("frame_count").GetProperty("result").GetUInt64();

    public void Initialize(nint windowHandle, uint width, uint height)
    {
        if (IsRunning) throw new InvalidOperationException("すでに初期化されています");

        // 起動 → ポート通知 → 接続。ここまでで、エンジンの命令を送れる状態になる
        _started = EngineProcess.StartAsync(_exePath, "", TimeSpan.FromSeconds(5)).GetAwaiter().GetResult();
        _client = new EngineClient(new TcpTransport(_started.Port));
        _client.ConnectAsync().GetAwaiter().GetResult();

        Call("init", new { window = (long)windowHandle, width, height });
    }

    public void Resize(uint width, uint height) => Call("resize", new { width, height });

    public void Tick(float dt) => Call("tick", new { dt });

    public void SendInput(int type, int button, float x, float y, float delta, int key, uint modifiers)
        => Call("input", new { type, button, x, y, delta, key, modifiers });

    public void Dispose()
    {
        _client?.DisposeAsync().AsTask().GetAwaiter().GetResult();   // 接続を閉じる。エンジンは、読み取りが終わって自分で終わる
        _client = null;
        if (_started is { } s)
        {
            if (!s.Process.WaitForExit(2000)) s.Process.Kill(entireProcessTree: true);   // 終わらなければ、強制終了
            s.Process.Dispose();
            _started = null;
        }
    }
}
```

`Initialize` の中で、エンジンの起動と接続まで行うのがこの作りの要です。`PInvokeEngineService.Initialize` が `pe_engine_create` を呼んでいた場所で、代わりに「プロセスを起動して繋ぐ」ことになります。これで、`RenderLoop` からも、DI の登録からも、起動の処理が見えなくなります。`IEngineService` の約束は変わりません。

`Call` が `GetAwaiter().GetResult()` で同期的に待つのは、先ほど見たとおり `Render` スレッドから呼ばれるからです。`Tick` は毎フレーム呼ばれるので、1 フレームごとに 1 往復の通信が起きます。同じ PC の中の往復は 100 マイクロ秒に届かない速さです（第 62 章の実測）。60 fps（1 フレーム約 16.7 ミリ秒）なら、通信が占める割合はごく小さいです。

`Dispose` は、接続を閉じて、エンジンが自分で終わるのを最大 2 秒待ち、終わらなければ強制終了します。エンジンを残さないための、最低限の後始末です。もっと行儀のよい閉じ方は、第 61 章で扱います。

## 3. エンジン側に、命令を足す

第 59 章の `Dispatch` に、エンジンを動かす命令を足します。エンジンの exe は `PrestAPI` の関数を直接呼べるので、`PInvokeEngineService` が呼んでいた `pe_engine_create` などをそのまま使えます。

```cpp title="EngineHost/TcpServer.cpp（変更：Dispatch に命令を足す）"
// 本物は、JSON ライブラリ（nlohmann など）で読む。ここでは、第 59 章の読み方に数値用を足す
double FindDouble(const std::string& json, const std::string& key) {
  const std::string pattern = "\"" + key + "\":";
  const auto pos = json.find(pattern);
  return pos == std::string::npos ? 0.0 : std::atof(json.c_str() + pos + pattern.size());
}

PrestEngine* g_engine = nullptr;   // エンジン本体。init で作り、プロセスの終わりで壊す

std::string Ok(const std::string& id, const std::string& result = "null") {
  return "{\"id\":" + id + ",\"ok\":true,\"result\":" + result + "}";
}
std::string Fail(const std::string& id, const std::string& message) {
  return "{\"id\":" + id + ",\"ok\":false,\"error\":\"" + message + "\"}";
}

std::string Dispatch(const std::string& request) {
  const std::string id = request.find("\"id\":") == std::string::npos
                             ? "null"
                             : std::to_string(FindNumber(request, "id"));
  const std::string cmd = FindString(request, "cmd");

  if (cmd == "ping") return Ok(id, "\"pong\"");

  if (cmd == "init") {
    PrestEngineDesc desc{};
    desc.window = reinterpret_cast<void*>(FindNumber(request, "window"));
    desc.width = static_cast<uint32_t>(FindNumber(request, "width"));
    desc.height = static_cast<uint32_t>(FindNumber(request, "height"));
    if (pe_engine_create(&desc, &g_engine) != PREST_OK) return Fail(id, pe_get_last_error());
    return Ok(id);
  }

  if (g_engine == nullptr) return Fail(id, "engine is not initialized");   // init より前の命令

  if (cmd == "resize") {
    const auto w = static_cast<uint32_t>(FindNumber(request, "width"));
    const auto h = static_cast<uint32_t>(FindNumber(request, "height"));
    return pe_engine_resize(g_engine, w, h) == PREST_OK ? Ok(id) : Fail(id, pe_get_last_error());
  }
  if (cmd == "tick") {
    const auto dt = static_cast<float>(FindDouble(request, "dt"));
    return pe_engine_tick(g_engine, dt) == PREST_OK ? Ok(id) : Fail(id, pe_get_last_error());
  }
  if (cmd == "frame_count") {
    uint64_t count = 0;
    if (pe_engine_get_frame_count(g_engine, &count) != PREST_OK) return Fail(id, pe_get_last_error());
    return Ok(id, std::to_string(count));
  }
  return Fail(id, "unknown command: " + cmd);
}
```

この断片の `PrestEngineDesc` のメンバー名、`PREST_OK` の名前、`pe_engine_destroy` を呼ぶ後始末の置き場所は、Prest の `PrestAPI.h` に合わせて確かめてください。名前を推測で書いた所があります。`input` 命令は、`pe_engine_send_input` に `PrestInputEvent` を作って渡す形で、`tick` と同じ要領で足せます。

`g_engine` はエンジンが 1 つだけという前提の、グローバル変数です。サーバーが 1 人のエディタだけを相手にする（第 59 章）ので、この形で足ります。プロセスが終わる前に、`pe_engine_destroy` で壊す処理を `ServeOnce` を抜けたあとに足しておきます。

## 4. DI の登録を差し替える

最後に、エディタの登録を差し替えます。`App.xaml.cs` の `RegisterTypes` の、この 1 行です。

```csharp title="Editor/App.xaml.cs（変更）"
// before
containerRegistry.RegisterSingleton<IEngineService, PInvokeEngineService>();

// after
containerRegistry.RegisterSingleton<IEngineService>(() =>
    new RemoteEngineService(Path.Combine(AppContext.BaseDirectory, "PrestEngineHost.exe")));
```

`RemoteEngineService` のコンストラクターは、exe のパスを 1 つ受け取るだけです。`RenderLoop` も、`IRenderLoop` を使うほかのクラスも、1 行も変えません。通信路を TCP から別のものに替えたくなったときも、`RemoteEngineService` の中の `TcpTransport` を差し替えるだけで済みます（第 59 章の `IEngineTransport`）。

`PrestEngineHost.exe` は、第 59 章の `TcpServer.cpp` に、前の節の命令を足してビルドしたものです。エディタの出力フォルダに置いてください。名前と置き場所は、Prest のビルドの設定に合わせて決めます。

## 動かして確かめる順番

この章の内容は、Prest 本体では動かして確かめていません。手順を分けて、1 つずつ確かめると、どこで失敗したのかが分かります。

1. エンジンの exe を、単体で起動する。標準出力に `port=NNNN` が出ることを確かめる
2. 第 59 章の `Program.cs` で、`ping` が返ることを確かめる
3. `init`、`tick` を足して、ウィンドウなしで（または、固定のウィンドウで）呼べることを確かめる
4. `RemoteEngineService` に差し替えて、エディタを起動する
5. エディタを閉じたとき、エンジンのプロセスが残っていないこと（タスク マネージャー）を確かめる

## 残っていること

この章で、エンジンが別のプロセスとして動くところまでは来ました。ただし、次のことは、まだ手をつけていません。

- <strong>描画先のウィンドウ</strong>：`init` に渡した `window` は、エディタのウィンドウのハンドルです。別のプロセスが、他のプロセスのウィンドウに描画する構成は、そのままでは安定して動かない場合があります。第 56 章で、描画結果の渡し方を扱います
- <strong>落ちたときの立て直し</strong>：エンジンのプロセスが落ちると、`RemoteEngineService` の呼び出しが `EngineDisconnectedException` で失敗します。再起動は、第 57 章の仕組みで足します
- <strong>安全と、固まりの検出</strong>：合言葉、ハートビート、行儀のよい終了は、第 61 章です

## これだけ覚える

- `IEngineService` の窓口があるから、実装を差し替えるだけで別プロセスにできる。呼び出し側は変えない。
- 起動は「プロセスを起動 → 標準出力の `port=` を待つ → 1 回だけ繋ぐ」。待つのは、ポートの行・プロセスの終了・時間切れの 3 つのうち最初のもの。
- 同期のメソッドの中で通信を待ってよいのは、呼ぶのが UI スレッドではないとき。Prest では、`Render` スレッドから呼ばれる。
- エンジン側は、`Dispatch` に命令を足すだけで増やせる。通信の部分は、そのまま使える。

## 確かめたもの、確かめていないもの

!!! note "確かめたもの、確かめていないもの"
    確かめたもの：`EngineProcess.StartAsync` は、.NET 10 でコンパイルして、第 59 章の `TcpServer.exe` と実際に繋いで動かした（正常な起動、すぐ終わる、何も出力しない、想定外の出力の 4 つ）。
    確かめていないもの：`RemoteEngineService` の C# と、エンジン側に足した `Dispatch` の C++ は、Prest 本体に入れてコンパイルしていない（`PrestEngineDesc` や `PREST_OK` などの名前は、`PrestAPI.h` で確かめてください）。`input` 命令。`init` に渡したウィンドウ ハンドルを、別のプロセスのエンジンが使って描画できるか。

## 関連ページ

- [第 59 章 TCP 編 1：最小のエンジンとエディタを繋ぐ](59-tcp-base.md)（前の章）
- [第 61 章 TCP 編 3：安全で壊れにくくする](61-tcp-hardening.md)（次の章。合言葉、固まりの検出、行儀のよい終了、テスト）
- [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)
- [第 55 章 エンジンをサーバーにする：EngineHost](55-engine-host.md)
- [第 56 章 ビューポートを別プロセスから受ける](56-remote-viewport.md)
- [第 57 章 落ちたら立て直す](57-recovery.md)

---
title: 第 60 章 TCP でエンジンに繋ぐ（localhost）
tags:
  - C#連携
  - TCP
---

# 第 60 章 TCP でエンジンに繋ぐ（localhost）

第 59 章で TCP の性質を見ました。バイトの流れであること。`Write` の成功は届いたことの証拠ではないこと。読まない相手には数百 KiB で書けなくなること。プロセスの死は一瞬で分かるのに、固まりは分からないこと。この章ではその知識を使って第 53〜57 章のエンジンとエディタの通信を、名前付きパイプから TCP（`127.0.0.1`）に載せ替えます。

第 53 章で「パイプの読み書きは『バイト列を送る』だけの小さな層に閉じ込めておく」と約束しました。この章はその約束を回収する章です。差し替えるのは <strong>Stream をどう作るか</strong>という 1 点だけです。長さ付きのメッセージ、要求と返事の対応、`RemoteEngineService`、ビューモデル。ここから上は 1 行も変わりません。

同じ PC の中だけで使うので、暗号化や、別の PC への接続は、扱いません。代わりに、同じ PC の「他のプログラム」から、エンジンをどう守るかを、真剣に考えます。

!!! info "このページを読む前に"
    - [第 59 章 TCP を深く知る：バイトの流れとして使うために](59-tcp-deep.md)（前の章。ストリーム、バッファ、切断の仕組み）
    - [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)（`EngineClient` と、長さ付きのメッセージ）
    - [第 55 章 エンジンをサーバーにする：EngineHost](55-engine-host.md)（`ServeOnce` と `EngineProcess`）
    - [第 57 章 落ちたら立て直す](57-recovery.md)（`EngineSupervisor` と `Disconnected`）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）

!!! abstract "この章で足す・直すもの"
    - `Editor/Engine/IEngineTransport.cs`（新規）：「Stream の作り方」の窓口。`PipeTransport` と `TcpTransport`
    - `Editor/Engine/EngineClient.cs`（変更）：パイプを直接持たず窓口から Stream を受け取る
    - `Editor/Engine/EngineProcess.cs`（変更）：標準入力で合言葉を渡し、標準出力でポート番号を受け取る
    - `Editor/Engine/Heartbeat.cs`（新規）：固まったエンジンを見つける
    - `EngineHost/TcpServer.cpp`（新規。第 53 章の `Server.cpp` の TCP 版）：Winsock のサーバー


## なぜ TCP 版も作るのか

パイプ版ですでに動いています。それでも TCP 版を足す理由は 3 つあります。

1 つめは <strong>エディタ以外のプログラムが、エンジンに繋ぎやすくなる</strong>ことです。Python のテスト スクリプトも第 58 章の MCP を橋渡しするプログラムも、ソケットならほぼどの言語からでも標準の機能だけで繋げます。名前付きパイプは言語によっては扱いが面倒なことがあります。

2 つめは接続先の決め方が単純になることです。パイプは名前の衝突を避けるために第 57 章で世代番号を付けていました。TCP はポート 0 で待ち受ければ、OS が空いている番号を選んでくれます。衝突はそもそも起きません。

3 つめは将来の選択肢です。同じメッセージの形のまま別の PC のエンジンに繋ぐ構成にも広げられます。この教材ではそこまで扱いません。ただ、窓口を作っておけばその道は閉じません。

ではパイプを捨てて TCP に統一するべきでしょうか。第 59 章で測ったとおり往復の時間はほぼ同じで、性能は理由になりません。<strong>両方を残して起動の引数で選べる</strong>ようにします。第 54 章で P/Invoke 版を残しておいたのと同じ考え方です。通信の不具合が出たときに通信路を替えて、原因を切り分けられます。


## 決めること

作り始める前に設計の約束を決めます。どれも第 59 章のどこかの節が、根拠です。

1. 待ち受けは `127.0.0.1` だけ。`0.0.0.0` にすると LAN に開く（第 59 章「ポートとアドレス」）。
2. ポートは 0 で OS に選ばせる。選ばれた番号はエンジンが標準出力に `port=NNNN` と書いて知らせる。決まった番号だと二重起動や前回の残りと衝突する（`AddressAlreadyInUse`）。
3. <strong>エディタはポートの通知を待ってから繋ぐ</strong>。待ち受けのないポートへの `connect` は手元で約 2 秒かかって失敗する。エンジンが起動するまで `connect` を繰り返す作りにはしない。
4. 最初の 1 通は合言葉。違う相手は切る。同じ PC にはエディタ以外のプログラムもいる。
5. <strong>合言葉は毎回違う乱数にして、標準入力で渡す</strong>。コマンド ライン引数に載せると、同じ PC の他のプログラムが、プロセスの一覧から読める場合がある。
6. 1 メッセージは 1 回の `Write`、`NoDelay` は有効（第 59 章「Nagle アルゴリズムと遅延 ACK」）。
7. 固まりはハートビートで見つける。プロセスの死は TCP が教えてくれる。

起動から終了までの流れを図にします。

<svg class="fig flow" viewBox="0 0 720 420" role="img" aria-label="エディタがエンジンを起動し、標準入力で合言葉を渡し、エンジンが 127.0.0.1 のポート 0 で待ち受けて標準出力にポート番号を書き、エディタが接続して合言葉を送り、ok が返ったら要求と返事を始め、最後に送信側を閉じて終わる"><defs><marker id="teA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">起動から終了まで（番号の順に進む）</text><text x="110" y="50" text-anchor="middle" style="font-size:13px;font-weight:600">エディタ</text><text x="610" y="50" text-anchor="middle" style="font-size:13px;font-weight:600">EngineHost</text><line x1="110" y1="60" x2="110" y2="408" stroke="#94a3b8" stroke-width="2"/><line x1="610" y1="60" x2="610" y2="408" stroke="#94a3b8" stroke-width="2"/><line x1="110" y1="80" x2="610" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="74" text-anchor="middle" style="font-size:12px;font-weight:600">① プロセスを起動</text><line x1="110" y1="112" x2="610" y2="112" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="106" text-anchor="middle" style="font-size:12px;font-weight:600">② 標準入力：合言葉（毎回違う乱数）</text><rect x="470" y="124" width="236" height="30" rx="8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="588" y="139" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">127.0.0.1 のポート 0 で listen</text><line x1="610" y1="184" x2="110" y2="184" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="178" text-anchor="middle" style="font-size:12px;font-weight:600">③ 標準出力：port=NNNN</text><line x1="110" y1="220" x2="610" y2="220" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="214" text-anchor="middle" style="font-size:12px;font-weight:600">④ connect ＋ 合言葉の 1 通目</text><line x1="610" y1="252" x2="110" y2="252" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="246" text-anchor="middle" style="font-size:12px;font-weight:600">⑤ "ok"（違う合言葉なら、何も返さず切る）</text><rect x="14" y="268" width="196" height="30" rx="8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="112" y="283" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">要求と返事（第 54 章と同じ）</text><line x1="110" y1="318" x2="610" y2="318" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="312" text-anchor="middle" style="font-size:12px;font-weight:600">⑥ 送信側を閉じる（FIN）</text><line x1="610" y1="354" x2="110" y2="354" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="348" text-anchor="middle" style="font-size:12px;font-weight:600">⑦ エンジンも送信側を閉じる（FIN）</text><text x="360" y="394" text-anchor="middle" style="font-size:12px">⑧ 両方が closesocket。EngineHost のプロセスは、終了コード 0 で終わる。</text></svg>

①〜③ の間、エディタは<strong>エンジンの標準出力を読んで待つ</strong>だけです。`connect` は、③ で番号が分かってから、1 回だけ呼びます。


## 窓口を Stream にする

最初の変更は `EngineClient` をパイプから切り離すことです。第 53 章の `EngineClient` は `NamedPipeClientStream` を直接持っていました。これを「`Stream` を作ってくれる窓口」に替えます。

```csharp title="Editor/Engine/IEngineTransport.cs（新規）"
namespace Editor.Engine;

// 「どうやって Stream を作るか」だけを差し替える窓口。EngineClient は、この先を知らない
public interface IEngineTransport
{
    // 時間内に繋がらなければ TimeoutException
    Task<Stream> ConnectAsync(TimeSpan timeout, CancellationToken ct = default);
}

// 送信側だけを閉じられる Stream（TCP の FIN）。パイプにはない
public interface IHalfCloseable
{
    void ShutdownSend();
}
```

`IEngineTransport` は 1 つのメソッドだけです。`IHalfCloseable` は第 59 章の「切断」の節で見た半閉じ（送信側だけ閉じる）を表します。パイプにはない機能なので別のインターフェースに分けました。`EngineClient` は「持っている Stream が `IHalfCloseable` なら使う」という書き方をします。

パイプ版は第 53 章の `ConnectAsync` をそのまま包みます。

```csharp title="Editor/Engine/PipeTransport.cs（新規）"
using System.IO.Pipes;

namespace Editor.Engine;

public sealed class PipeTransport(string pipeName) : IEngineTransport
{
    public async Task<Stream> ConnectAsync(TimeSpan timeout, CancellationToken ct = default)
    {
        var pipe = new NamedPipeClientStream(".", pipeName, PipeDirection.InOut, PipeOptions.Asynchronous);
        try
        {
            await pipe.ConnectAsync((int)timeout.TotalMilliseconds, ct).ConfigureAwait(false);
            return pipe;
        }
        catch
        {
            await pipe.DisposeAsync().ConfigureAwait(false);   // 繋がらなかった Stream を残さない
            throw;
        }
    }
}
```

`EngineClient` の変更は次の 5 か所です。それ以外（`RequestAsync`、書き込みの排他、読み取りのループの本体）は第 53 章のままです。

1. パイプのフィールドを窓口と Stream に替えます。

```csharp title="Editor/Engine/EngineClient.cs（変更 1：フィールドとコンストラクター）"
    private readonly IEngineTransport _transport;
    private Stream? _stream;                       // 接続できたあとに入る
    private volatile bool _closing;                // 自分から閉じている最中（切断を、異常として知らせない）
    // ……（_writeLock、_pending、_nextId、_readLoop は第 53 章のまま）

    public EngineClient(IEngineTransport transport) => _transport = transport;

    private Stream Stream => _stream ?? throw new InvalidOperationException("ConnectAsync が先に必要です。");
```

`_stream` は `ConnectAsync` が成功してから入ります。それ以前に `RequestAsync` を呼ぶと `Stream` プロパティが、原因の分かる例外を投げます。`_closing` は後で使います。

2. `ConnectAsync` が窓口から Stream を受け取ります。

```csharp title="Editor/Engine/EngineClient.cs（変更 2：ConnectAsync）"
    public async Task ConnectAsync(int timeoutMs = 5000)
    {
        _stream = await _transport.ConnectAsync(TimeSpan.FromMilliseconds(timeoutMs)).ConfigureAwait(false);
        _readLoop = Task.Run(ReadLoopAsync);     // 返事を読むループを、別のタスクで回す
    }
```

3. 読み書きの `_pipe` を `Stream` に置き換えます。`WriteMessageAsync` では `await Stream.WriteAsync(frame)` と `await Stream.FlushAsync()` に。`ReadLoopAsync` では `await Stream.ReadExactlyAsync(header)` と `await Stream.ReadExactlyAsync(body)` に替えるだけです。

メッセージの形も第 53 章のままで足ります。`WriteMessageAsync` は長さと本文を 1 つの配列 `frame` にまとめて、1 回の `WriteAsync` で書いていました。第 59 章で見たとおりこれは Nagle と遅延 ACK の待ち合わせを避ける作りでもあります。`ReadExactlyAsync` は部分読みを組み立てる関数です。TCP の細切れの届き方にもそのまま耐えます。

4. 読み取りのループの `finally` で、自分から閉じたときは `Disconnected` を呼びません。

```csharp title="Editor/Engine/EngineClient.cs（変更 4：ReadLoopAsync の finally）"
        finally
        {
            foreach (var tcs in _pending.Values)
            {
                tcs.TrySetException(new EngineDisconnectedException());   // 待っている全員に知らせる
            }
            if (!_closing) Disconnected?.Invoke();       // 自分から閉じたときは、「落ちた」とは知らせない
        }
```

第 57 章の `EngineSupervisor` は `Disconnected` を「エンジンが落ちた」知らせとして使い立て直しを始めます。自分から正常に閉じたときにまで `Disconnected` が飛ぶと閉じた直後にエンジンの再起動が始まってしまいます。第 57 章では `_disposed` の旗で `Supervisor` の側から防いでいました。`EngineClient` の側でも防いでおけば二重の安全になります。

5. 行儀のよい閉じ方を足します。

```csharp title="Editor/Engine/EngineClient.cs（変更 5：閉じ方）"
    // 行儀のよい閉じ方: 送信側を閉じて（FIN）、相手が閉じるのを待つ。待ち切れなければ強制的に閉じる
    public async Task CloseGracefullyAsync(TimeSpan wait)
    {
        _closing = true;
        if (_stream is IHalfCloseable half) half.ShutdownSend();
        if (_readLoop is not null) await Task.WhenAny(_readLoop, Task.Delay(wait)).ConfigureAwait(false);
        await DisposeAsync().ConfigureAwait(false);
    }

    public async ValueTask DisposeAsync()
    {
        _closing = true;
        if (_stream is not null) await _stream.DisposeAsync().ConfigureAwait(false);
        if (_readLoop is not null) await _readLoop.ConfigureAwait(false);
    }
```

`CloseGracefullyAsync` は第 59 章の「正しい閉じ方」のエディタ側の手順です。`ShutdownSend` で `FIN` を送ります。するとエンジンの側の `ReadMessage` が `false` を返して、エンジンが閉じる手順に入ります。エンジンも閉じるとこちらの読み取りのループが、EOF（`ReadExactlyAsync` の `EndOfStreamException`）で終わります。`Task.WhenAny` はその終わりを `wait` を上限に待ちます。相手が応答しない場合でも `wait` を過ぎれば、強制的に `DisposeAsync` します。

パイプ版の Stream には `IHalfCloseable` がないので、`ShutdownSend` は呼ばれずそのまま `DisposeAsync` に進みます。パイプではこれで相手に切断が伝わります。


## TcpTransport

TCP の窓口です。「接続して合言葉を送って `ok` を待つ」までを受け持ちます。

まず、半閉じのできる Stream です。

```csharp title="Editor/Engine/TcpStream.cs（新規）"
using System.Net.Sockets;

namespace Editor.Engine;

// NetworkStream に、送信側だけ閉じる操作を足したもの
public sealed class TcpStream(Socket socket) : NetworkStream(socket, ownsSocket: true), IHalfCloseable   // socket は、繋がったあとのもの
{
    public void ShutdownSend()
    {
        try { Socket.Shutdown(SocketShutdown.Send); }
        catch (SocketException) { }          // すでに切れていても、閉じたい気持ちは同じ
        catch (ObjectDisposedException) { }
    }
}
```

`NetworkStream` には `Socket` を `protected` で公開するプロパティがあるので、派生クラスの中から `Shutdown` を呼べます。`ownsSocket: true` なので `Stream` を `Dispose` すれば、ソケットも閉じます。`NetworkStream` のコンストラクターは <strong>繋がったあとのソケット</strong>しか受け付けません。繋がる前に渡すと `IOException`（「非接続のソケットでは、この操作は許可されません」）になります（実測）。次のコードで `TcpStream` を作るのが接続のあとになっているのは、このためです。

```csharp title="Editor/Engine/TcpTransport.cs（新規）"
using System.Net;
using System.Net.Sockets;
using System.Text;

namespace Editor.Engine;

public sealed class TcpTransport(int port, string token) : IEngineTransport
{
    public async Task<Stream> ConnectAsync(TimeSpan timeout, CancellationToken ct = default)
    {
        var socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp)
        {
            NoDelay = true,          // 小さな要求を、Nagle で溜めずにすぐ送る
        };

        // 接続と握手を、合わせて timeout の中に収める
        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(timeout);
```

アドレスの種類を `InterNetwork`（IPv4）に決めています。第 59 章のとおり `localhost` という名前は使いません。`NoDelay = true` は Nagle を切る設定です。`CancelAfter` の `timeout` は接続と握手の合計の制限時間です。`ct`（呼び出し側の取り消し）と時間切れをどちらも `cts.Token` 1 つにまとめています。

```csharp title="Editor/Engine/TcpTransport.cs（続き：接続）"
        try
        {
            await socket.ConnectAsync(new IPEndPoint(IPAddress.Loopback, port), cts.Token).ConfigureAwait(false);
        }
        catch (OperationCanceledException) when (!ct.IsCancellationRequested)
        {
            socket.Dispose();
            throw new TimeoutException($"{timeout.TotalSeconds} 秒以内に接続できませんでした。");
        }
        catch
        {
            socket.Dispose();        // 拒否（ConnectionRefused）など。socket を残さない
            throw;
        }
```

`OperationCanceledException` が出てしかも呼び出し側の `ct` が取り消されていないなら時間切れです。`TimeoutException` に翻訳します。第 59 章で見たとおり時間切れと接続の拒否は、別の失敗です。拒否は `SocketException`（`ConnectionRefused`）のまま上に伝えます。どちらの場合もソケットはここで破棄します。

```csharp title="Editor/Engine/TcpTransport.cs（続き：握手）"
        var stream = new TcpStream(socket);   // 繋がってから作る。以降は stream の Dispose が socket も閉じる
        try
        {
            // 握手: 合言葉を送り、"ok" が返れば、本物のエンジン
            await Framing.WriteFrameAsync(stream, Encoding.UTF8.GetBytes(token), cts.Token).ConfigureAwait(false);
            byte[] reply = await Framing.ReadFrameAsync(stream, cts.Token).ConfigureAwait(false);   // 違う合言葉なら、ここで切られる
            if (Encoding.UTF8.GetString(reply) != "ok") throw new InvalidDataException("握手の返事が想定外です。");
            return stream;
        }
        catch (Exception e) when (e is IOException or InvalidDataException)
        {
            // 合言葉が違う、または相手がエンジンではない。サーバーは何も返さずに切る
            await stream.DisposeAsync().ConfigureAwait(false);     // 失敗した接続を残さない
            throw new InvalidDataException("握手に失敗しました（合言葉が違う、または相手がエンジンではありません）。", e);
        }
        catch (OperationCanceledException) when (!ct.IsCancellationRequested)
        {
            // 呼び出し側の取り消しではない = 時間切れ。握手の返事が来なかった
            await stream.DisposeAsync().ConfigureAwait(false);
            throw new TimeoutException("握手の返事が来ませんでした。");
        }
        catch
        {
            await stream.DisposeAsync().ConfigureAwait(false);     // 想定外の例外でも、ソケットは必ず閉じる
            throw;
        }
    }
}
```

握手の 1 通目は合言葉を長さ付きのメッセージとして送ります。`Framing`（次のコード）は第 53 章の `WriteMessageAsync` と `ReadLoopAsync` の中身を取り出して関数にしたものです。

サーバーは合言葉が違うと返事をせずに接続を切ります。エディタの側では `ReadFrameAsync` が `EndOfStreamException` か `IOException`（`ConnectionReset`）で終わるので、`InvalidDataException` に包んで原因の分かる文面にします。何も返事をしない理由は攻撃者に情報を与えないためです。ただ、エディタの開発者にとっては「切られた」だけでは原因が分かりにくいので、エディタの側が文面を補います。

```csharp title="Editor/Engine/Framing.cs（新規）"
using System.Buffers.Binary;

namespace Editor.Engine;

// 長さ付きフレーム。長さと本文は、1 回の Write にまとめる
public static class Framing
{
    public const int MaxMessageSize = 16 * 1024 * 1024;

    public static async ValueTask WriteFrameAsync(Stream s, ReadOnlyMemory<byte> body, CancellationToken ct = default)
    {
        var frame = new byte[4 + body.Length];                           // 長さ 4 バイト + 本文を、1 つの配列にまとめる
        BinaryPrimitives.WriteInt32LittleEndian(frame, body.Length);     // 長さはリトル エンディアン（C++ 側と同じ）
        body.CopyTo(frame.AsMemory(4));
        await s.WriteAsync(frame, ct).ConfigureAwait(false);             // 1 回の Write（Nagle と遅延 ACK の待ち合わせを避ける）
        await s.FlushAsync(ct).ConfigureAwait(false);
    }

    public static async ValueTask<byte[]> ReadFrameAsync(Stream s, CancellationToken ct = default)
    {
        var header = new byte[4];
        await s.ReadExactlyAsync(header, ct).ConfigureAwait(false);   // 部分読みでも、4 バイト揃うまで待つ
        int length = BinaryPrimitives.ReadInt32LittleEndian(header);
        // 壊れた長さを信じて、巨大な配列を確保しない（HTTP の "GET " は、約 5.4 億バイトの長さに見える）
        if (length < 0 || length > MaxMessageSize) throw new InvalidDataException($"不正なメッセージ長: {length}");
        var body = new byte[length];
        await s.ReadExactlyAsync(body, ct).ConfigureAwait(false);        // 本文も、揃うまで読み続ける
        return body;
    }
}
```

`EngineClient` 本体の `WriteMessageAsync` と `ReadLoopAsync` も本当は `Framing` を呼ぶ形に整理できます。この章では第 53 章のコードの変更を最小にするために `EngineClient` の中身は、そのまま残しました。


## EngineHost 側：Winsock のサーバー

エンジンの側です。第 53 章の `ServeOnce`（パイプ版）と同じ約束、「1 人のエディタを相手にして、その人が終われば戻る」を TCP で作り直します。戻り値の意味も同じです。`false` は待ち受けを始められなかったことを表します（第 55 章の終了コード 2）。

C++ はヘッダーと道具になる小さなクラスから始めます。

```cpp title="EngineHost/TcpServer.cpp（新規）"
#include <winsock2.h>   // Winsock 本体。windows.h より先に include する
#include <ws2tcpip.h>    // inet_pton など

#include <cstdint>
#include <cstdlib>
#include <cstdio>
#include <cstring>
#include <functional>
#include <iostream>
#include <string>
#include <utility>
#include <vector>

#pragma comment(lib, "ws2_32.lib")   // MSVC だけ: リンクするライブラリを、ソースから指定する

// ---- WSAStartup / WSACleanup を、対にして守る ----
class WinsockSession {
 public:
  WinsockSession() {
    WSADATA data{};
    ok_ = (WSAStartup(MAKEWORD(2, 2), &data) == 0);  // Winsock 2.2 を要求する
  }
  ~WinsockSession() { if (ok_) WSACleanup(); }
  WinsockSession(const WinsockSession&) = delete;
  WinsockSession& operator=(const WinsockSession&) = delete;
  bool ok() const { return ok_; }
 private:
  bool ok_ = false;
};
```

`winsock2.h` は `windows.h` より先に include します。順序を逆にすると古い `winsock.h` が先に取り込まれて、定義が衝突します（古くから知られた注意点で、この章では確かめていません）。ここでは `windows.h` を直接 include していないので、問題は起きません。

`WSAStartup` は Winsock を使う前に必ず 1 回呼ぶ関数です。呼び忘れるとすべてのソケット関数が失敗します。Microsoft Learn は `WSAStartup` と `WSACleanup` を RAII のクラスで対にして、どの出口でも後片付けが走るようにすることを勧めています。バージョンは `MAKEWORD(2, 2)`（Winsock 2.2）を要求します。

```cpp title="EngineHost/TcpServer.cpp（続き：SOCKET の RAII）"
// ---- SOCKET を持つだけの小さな RAII。コピー不可、ムーブ可 ----
class Socket {
 public:
  Socket() = default;
  explicit Socket(SOCKET s) : s_(s) {}
  ~Socket() { Reset(); }                       // スコープを出るときに、必ず closesocket する
  // ムーブ: 持ち主を移す（移した元は INVALID_SOCKET になり、二重に閉じない）
  Socket(Socket&& o) noexcept : s_(std::exchange(o.s_, INVALID_SOCKET)) {}
  Socket& operator=(Socket&& o) noexcept {
    if (this != &o) { Reset(); s_ = std::exchange(o.s_, INVALID_SOCKET); }
    return *this;
  }
  Socket(const Socket&) = delete;              // コピー不可: 同じ SOCKET を 2 人が閉じてしまうため
  Socket& operator=(const Socket&) = delete;
  SOCKET get() const { return s_; }            // 生の SOCKET が要る API 呼び出し用（所有は移らない）
  bool valid() const { return s_ != INVALID_SOCKET; }
  void Reset() {
    if (s_ != INVALID_SOCKET) { closesocket(s_); s_ = INVALID_SOCKET; }
  }
 private:
  SOCKET s_ = INVALID_SOCKET;
};
```

`SOCKET` はただの整数のハンドルなので、`closesocket` を呼び忘れると漏れます。`unique_ptr` のように持ち主が 1 人になるクラスで包みます。`INVALID_SOCKET` を `valid` で見分けられるようにしています。

次が待ち受けです。

```cpp title="EngineHost/TcpServer.cpp（続き：待ち受け）"
// ---- 待ち受け: 127.0.0.1 だけ、ポートは 0（OS におまかせ）にもできる ----
Socket ListenLoopback(uint16_t port, uint16_t* bound_port) {
  Socket s(socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
  if (!s.valid()) return {};

  // 他のプログラムが、同じポートに割り込んで bind できないようにする（bind より前に設定）
  const BOOL exclusive = TRUE;
  setsockopt(s.get(), SOL_SOCKET, SO_EXCLUSIVEADDRUSE,
             reinterpret_cast<const char*>(&exclusive), sizeof(exclusive));

  sockaddr_in addr{};
  addr.sin_family = AF_INET;
  addr.sin_port = htons(port);
  inet_pton(AF_INET, "127.0.0.1", &addr.sin_addr);  // INADDR_ANY（0.0.0.0）にはしない
  if (bind(s.get(), reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) == SOCKET_ERROR) return {};
  if (listen(s.get(), 4) == SOCKET_ERROR) return {};

  // port=0 で bind したときの、実際のポートを聞く
  int len = sizeof(addr);
  getsockname(s.get(), reinterpret_cast<sockaddr*>(&addr), &len);
  *bound_port = ntohs(addr.sin_port);
  return s;
}
```

呼び出す関数の順は `socket`（作る）→ `bind`（アドレスとポートに結びつける）→ `listen`（待ち受けを始める）です。第 59 章で見た `TcpListener.Start()` の中身です。`htons` と `ntohs` はポート番号をネットワーク バイト オーダー（ビッグ エンディアン）と、手元の並びの間で変換します。TCP のヘッダーの数値はビッグ エンディアンで運ぶ決まりです。第 53 章の「長さ付きメッセージ」の長さは、こちらの取り決めでリトル エンディアンにしています。2 つが別の約束であることに注意してください。

`SO_EXCLUSIVEADDRUSE` は `bind` の前に設定します。第 59 章のとおり他のソケットが同じアドレスとポートに割り込めないようにする設定です。`inet_pton` で文字列の `127.0.0.1` をアドレスの構造体に変換します。`INADDR_ANY` を渡してしまうと LAN に開きます。この 1 行が第 59 章の「`IPAddress.Any` は絶対に避ける」に当たります。`listen` の第 2 引数（4）は待ち行列の長さです。繋ぎにくるのは 1 人のエディタだけなので、小さくて足ります。`getsockname` で OS が選んだポート番号を聞き出します。

読み書きの道具は第 53 章の `ReadExact` と `WriteExact` のソケット版です。

```cpp title="EngineHost/TcpServer.cpp（続き：確実に読み書きする）"
// ---- ちょうど size バイト受け取る。TCP は流れなので、recv は少なく返ることがある ----
bool RecvExact(SOCKET s, void* buffer, int size) {
  auto* p = static_cast<char*>(buffer);
  while (size > 0) {
    const int n = recv(s, p, size, 0);
    if (n == 0) return false;            // 相手が FIN を送った（正常な終わり）
    if (n == SOCKET_ERROR) return false; // RST、時間切れ、自分が閉じた、など
    p += n;
    size -= n;
  }
  return true;
}

// ---- 全部送る。send も、一部だけ送って戻ることがある ----
bool SendAll(SOCKET s, const void* buffer, int size) {
  const auto* p = static_cast<const char*>(buffer);
  while (size > 0) {
    const int n = send(s, p, size, 0);
    if (n == SOCKET_ERROR) return false;
    p += n;
    size -= n;
  }
  return true;
}
```

`recv` が 0 を返すのは相手が `FIN` を送った印です。エラーの `SOCKET_ERROR` は `RST` や時間切れ（`SO_RCVTIMEO`、後述）や自分でソケットを閉じたときなどで返ります。原因は `WSAGetLastError()` で分かります。ここでは、どちらも「続けられない」ので、`false` を返すだけにしています。`send` も同じ作りです。戻り値のバイト数だけ進める作りにしておくと一部だけ送って戻った場合にも全部送り切るまで続けられます。

```cpp title="EngineHost/TcpServer.cpp（続き：長さ付きメッセージ）"
constexpr uint32_t kMaxMessage = 16u * 1024 * 1024;

bool ReadMessage(SOCKET s, std::string& out) {
  uint32_t length = 0;  // リトル エンディアン（x64 の Windows は、そのまま読める）
  if (!RecvExact(s, &length, sizeof(length))) return false;
  if (length > kMaxMessage) return false;  // 壊れた長さを信じて、巨大な確保をしない
  out.resize(length);
  return length == 0 || RecvExact(s, out.data(), static_cast<int>(length));
}

bool WriteMessage(SOCKET s, const std::string& body) {
  // 長さと本文を 1 回の send にまとめる。2 回に分けると、小さな送信が 2 つになる（Nagle の節）
  std::vector<char> frame(sizeof(uint32_t) + body.size());
  const auto length = static_cast<uint32_t>(body.size());
  std::memcpy(frame.data(), &length, sizeof(length));
  std::memcpy(frame.data() + sizeof(length), body.data(), body.size());
  return SendAll(s, frame.data(), static_cast<int>(frame.size()));
}
```

長さの上限は 16 MiB です。これは第 53 章と同じ値で、「壊れた長さを信じて巨大な確保をしない」ためです。`WriteMessage` が長さと本文を `frame` 1 つにまとめて、1 回の `send` で送るのは第 59 章で見たとおり Nagle と遅延 ACK の待ち合わせを避けるためです。

次が握手です。

```cpp title="EngineHost/TcpServer.cpp（続き：握手）"
// ---- 握手: 最初の 1 通が合言葉と合えば "ok" を返す ----
bool Handshake(SOCKET s, const std::string& token) {
  // 繋いだだけで何も送らない相手に、いつまでも付き合わない（3 秒で諦める）
  const DWORD handshake_timeout_ms = 3000;
  setsockopt(s, SOL_SOCKET, SO_RCVTIMEO,
             reinterpret_cast<const char*>(&handshake_timeout_ms), sizeof(handshake_timeout_ms));

  std::string hello;
  if (!ReadMessage(s, hello) || hello != token) return false;
  if (!WriteMessage(s, "ok")) return false;

  const DWORD no_timeout = 0;  // 握手のあとは、エディタが黙っていても待ち続ける（0 = 時間切れなし）
  setsockopt(s, SOL_SOCKET, SO_RCVTIMEO,
             reinterpret_cast<const char*>(&no_timeout), sizeof(no_timeout));
  return true;
}
```

`SO_RCVTIMEO` はブロッキングの `recv` の時間切れ（ミリ秒）です。Microsoft Learn によると、既定は 0（時間切れなし）で、時間切れになった `recv` のあとその接続は「不定の状態」なので、閉じるべきだとされています。握手では 3 秒だけ待ってそれを超えたら、その相手を切ります。握手のあとは時間切れなしに戻します。エディタはユーザーが何もしなければ、何分も黙っているのが普通だからです。

3 秒の待ちには限界があります。サーバーは 1 人ずつ順に処理するので、繋いだだけで黙る相手が先にいると、本物のエディタの握手がその 3 秒の後ろに並びます。手元で測ると本物の握手が完了するまで 3013 ミリ秒でした。同じ PC の他のプログラムが、悪意で同じことを繰り返すとエンジンの起動が 3 秒ずつ遅れます（サービスの妨害）。エンジンを実運用に近づけるなら握手を別のスレッドで、並行して受ける作りにします。この章ではそこまで作りません。

最後が閉じ方と `ServeOnce` です。

```cpp title="EngineHost/TcpServer.cpp（続き：閉じ方と ServeOnce）"
// ---- 閉じ方: 自分の送信側を閉じて（FIN）、相手が閉じるまで読み捨ててから closesocket ----
void CloseGracefully(SOCKET s) {
  shutdown(s, SD_SEND);
  const DWORD timeout_ms = 1000;  // 相手が閉じてくれなくても、1 秒で諦める
  setsockopt(s, SOL_SOCKET, SO_RCVTIMEO,
             reinterpret_cast<const char*>(&timeout_ms), sizeof(timeout_ms));
  char sink[256];
  while (recv(s, sink, sizeof(sink), 0) > 0) {}  // 0（相手の FIN）か、エラー（時間切れ）で終わる
}

// ---- エディタが 1 人繋ぐまで待ち、繋がったら、その 1 人の相手をする ----
// 戻り値: false = 待ち受けを始められなかった（第 55 章の ServeOnce と同じ約束）
bool ServeOnce(const std::string& token,
               const std::function<std::string(const std::string&)>& handler) {
  uint16_t port = 0;
  Socket listener = ListenLoopback(0, &port);
  if (!listener.valid()) return false;
  std::printf("port=%u\n", port);   // エディタが、この 1 行を読んで接続先を知る
  std::fflush(stdout);

  for (;;) {
    Socket client(accept(listener.get(), nullptr, nullptr));
    if (!client.valid()) return false;

    // 小さい要求と返事を、すぐ送る（Nagle アルゴリズムを切る）
    const BOOL no_delay = TRUE;
    setsockopt(client.get(), IPPROTO_TCP, TCP_NODELAY,
               reinterpret_cast<const char*>(&no_delay), sizeof(no_delay));

    // 合言葉が違う相手は、返事をせずに切って、本物のエディタを待ち続ける
    if (!Handshake(client.get(), token)) continue;

    std::string request;
    while (ReadMessage(client.get(), request)) {   // エディタが閉じる、または壊れた長さで false
      if (!WriteMessage(client.get(), handler(request))) break;
    }
    CloseGracefully(client.get());
    return true;                                   // 1 人終わったら、エンジンも終わる
  }
}  // client と listener のデストラクタが closesocket
```

`CloseGracefully` が第 59 章の「正しい閉じ方」のエンジン側の手順です。`shutdown(s, SD_SEND)` で `FIN` を送ってから相手の `FIN` が来る（`recv` が 0）まで、読み捨てます。これをせずに `closesocket` すると未読のデータが残っていた場合に相手へ `RST` が飛ぶことがあります（第 59 章の実験）。相手が閉じてくれなくても 1 秒で諦めます。

`ServeOnce` の `for (;;)` は「合言葉が違う相手を切って、次を待つ」ためにあります。繋いできた相手が偽物でもエンジンは終わらず本物のエディタを待ち続けます。これがないと同じ PC の他のプログラムが 1 回繋ぐだけで、エンジンが終了してしまいます。手元でも確かめました。違う合言葉の相手が先に繋いでもそのあとで本物が繋ぐと握手が通りました。エンジンはその間、生きていました。

`std::printf("port=%u\n", port)` と `fflush` がエディタへの合図です。標準出力はパイプに繋がれていると、バッファされてすぐには流れません。`fflush` を忘れるとエディタがポートの通知を待ち続けます。第 55 章でログを標準エラー（バッファなし）に書いたのと使い分けています。標準出力はポートの通知だけに使いログは標準エラーのままにしてください。

`main` は合言葉を標準入力から読んで、`ServeOnce` を呼ぶだけです。

```cpp title="EngineHost/TcpServer.cpp（続き：main）"
int main() {
  // 合言葉は、コマンド ライン引数ではなく標準入力の 1 行目で受け取る
  std::string token;
  std::getline(std::cin, token);
  if (!token.empty() && token.back() == '\r') token.pop_back();

  WinsockSession wsa;
  if (!wsa.ok()) return 1;

  const bool served = ServeOnce(token, [](const std::string& request) {
    // 本物は、第 55 章の Dispatch。ここでは id だけ拾って、決まった返事を返す
    const auto pos = request.find("\"id\":");
    const std::string id = pos == std::string::npos ? "null" : std::to_string(std::atoll(request.c_str() + pos + 5));
    return "{\"id\":" + id + ",\"ok\":true,\"result\":null}";
  });
  return served ? 0 : 2;    // 2 = 待ち受けを始められなかった
}
```

本物のエンジンではラムダの中身を第 55 章の `Dispatch(handlers, request)` に置き換えます。この章の確認用には `id` だけを拾って、`ok` を返す返事を作る代役を置きました。

`/utf-8` を付けてコンパイルすることを忘れないでください。付けないと日本語のコメントの文字コードの解釈（既定は Shift_JIS 系のコード ページ）がずれて、コンパイルが失敗します（実際に手元でもそうなりました）。

このコードは `/W4 /utf-8 /std:c++latest` で警告なしにコンパイルできました。そして、この章の C# のクライアントと実際に繋いで、すべての動作を確かめています。


## 起動：合言葉は標準入力、ポートは標準出力

第 55 章の `EngineProcess.StartAsync` を TCP 版に直します。変わるのは起動の引数、標準入出力の設定、接続を待つ部分です。ジョブ オブジェクトの部分はそのままです。

```csharp title="Editor/Engine/EngineProcess.cs（変更：StartAsync の前半）"
    // エンジンを起動して、待ち受けのポートが分かるまで待つ
    public static async Task<StartedEngine> StartAsync(string exePath, string arguments, TimeSpan timeout)
    {
        // 起動のたびに作る合言葉（128 ビットの乱数を、16 進の 32 文字にしたもの）
        string token = Convert.ToHexString(RandomNumberGenerator.GetBytes(16));

        var info = new ProcessStartInfo(exePath, arguments)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardInput = true,     // 合言葉を渡す
            RedirectStandardOutput = true,    // 待ち受けのポート番号を受け取る
            RedirectStandardError = true,     // ログ（第 55 章）
        };
        Process process = Process.Start(info) ?? throw new InvalidOperationException("エンジンを起動できません");
        process.BeginErrorReadLine();         // 読み手がいないと、エンジンの書き込みが止まる（第 55 章）
```

`RandomNumberGenerator.GetBytes(16)` は暗号用の乱数を 16 バイト（128 ビット）作ります。`Random` は使いません。`Random` は暗号用ではなく値の推測しにくさが保証されていないからです。合言葉は起動のたびに変わるので、前回の合言葉が漏れても今回のエンジンには使えません。

`RedirectStandardInput = true` でエンジンの標準入力をエディタが書き込める状態にします。`ProcessStartInfo` の `Arguments` には合言葉を載せていません。コマンド ライン引数は同じ PC の他のプログラムが、プロセスの一覧から読める場合があります。標準入力ならエンジンとエディタの間だけに留まります。

```csharp title="Editor/Engine/EngineProcess.cs（変更：StartAsync の後半）"
        try
        {
            await process.StandardInput.WriteLineAsync(token).ConfigureAwait(false);
            await process.StandardInput.FlushAsync().ConfigureAwait(false);

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
                return new StartedEngine(process, port, token);
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

public sealed record StartedEngine(Process Process, int Port, string Token);
```

`Task.WhenAny` で 3 つのうち最初に終わったものを待ちます。「ポートの行が来た」「プロセスが終わった」「時間切れ」です。第 55 章では 300 ミリ秒ずつ短く待っては、`HasExited` を見ていました。標準出力を読む作りならその必要はなく、3 つのどれが先かが一度に分かります。

プロセスが起動の途中で終わった場合は、標準出力が閉じられて `lineTask` が `null` で終わります。`exitTask` もほぼ同時に終わります。`WhenAny` はどちらが先に見えるか決まっていないので、どちらも「起動中に終わった」として扱います。終了コードを例外に載せるのは、第 55 章と同じです。

手元で 4 つの場合を確かめました。

```text title="起動の確認（実測）"
[A] 起動から port 通知まで 56 ms, port=56324
[D] 起動してすぐ終了: InvalidOperationException: エンジンが起動中に終了しました（終了コード 0x3） (56 ms)
[D] 何も出力しない: TimeoutException: 1 秒以内に、エンジンが待ち受けを始めませんでした。 (1072 ms)
[D] 想定外の出力: InvalidDataException: 想定外の出力: hello (46 ms)
```

正常なら 56 ミリ秒でポートが分かりました。起動してすぐ終わる場合は 56 ミリ秒で、終了コードつきの例外になります。何も出力しない場合は指定した 1 秒で時間切れになります。第 55 章の「5 秒待たされたあとの時間切れ」を「すぐ分かる理由つきの失敗」に変えるという設計は、そのまま働いています。

`EngineSupervisor`（第 57 章）の変更は少しです。パイプの名前に付けていた世代番号（`_generation`、`_pipeBase`）は要らなくなります。ポートは毎回、OS が新しく選ぶので古いエンジンが残っていても、衝突しません。`LaunchAsync` は `StartAsync(exePath, "", timeout)` を呼んで `StartedEngine` から `new EngineClient(new TcpTransport(started.Port, started.Token))` を作り `ConnectAsync` します。


## 固まりを見つける：ハートビート

第 59 章でプロセスの死と固まりは、別物だと見ました。死んだときは TCP が切断を知らせます。手元で `Kill` したところ `EngineClient.Disconnected` が、1 ミリ秒後に飛びました。

```text title="Kill してから Disconnected まで（実測）"
[E] Kill から Disconnected まで 1 ms
[E] 切れたあとの要求 -> EngineDisconnectedException
```

固まりはそうはいきません。エンジンが無限ループに入った、デッドロックしたあるいはデバッガーで止まっている。プロセスは生きているので OS は接続を保ったままにします。しかも TCP の確認応答はアプリではなく OS が返すので、エディタから見ると「送ったデータは届いている（確認応答が返る）のに、返事だけが来ない」状態になります。

実際に、`NtSuspendProcess` でエンジンのプロセスを丸ごと固めて、確かめました。

```text title="エンジンを固めたときの TCP の状態（実測）"
[F] 固まってから、ハートビートが死亡判定するまで 1853 ms（Disconnected イベント=False）
[F] そのとき TCP の状態: ESTABLISHED / ESTABLISHED
```

接続は `ESTABLISHED` のままで `Disconnected` も飛びません。ハートビートが判定するまでエディタは、エンジンの異常に気づけません。

### TCP の keep-alive では、足りない

TCP には keep-alive という機能があります。一定時間通信がないとき OS が小さな確認用のセグメントを送り相手の OS が返事をするかを見ます。しかし、これは「相手の <strong>OS</strong> が生きているか」を見る機能です。アプリが固まっていても OS は確認に答えます。固まったエンジンの検出には使えません（TCP の仕組みからの推論です。この章の実験では keep-alive を使って確かめてはいません）。

しかも既定値が長いのです。Microsoft Learn によると、Windows の TCP では keep-alive の既定の待ち時間は 2 時間です。RFC 9293 も既定で無効にして、間隔の既定は 2 時間以上にすることを求めています（MUST-25、MUST-28）。

設定自体はできます。`TcpKeepAliveTime`（待ち時間）、`TcpKeepAliveInterval`（確認の間隔）、`TcpKeepAliveRetryCount`（確認の回数）を設定する操作は手元でも通りました。ただし、この章では使いません。

### ハートビートを作る

アプリのレベルで定期的に `ping` を送って、返事が来るかを見ます。

```csharp title="Editor/Engine/Heartbeat.cs（新規）"
namespace Editor.Engine;

// 繋がっているのに応答しない相手を見つける
public static class Heartbeat
{
    public static async Task RunAsync(Func<CancellationToken, Task> ping, TimeSpan interval, TimeSpan timeout,
                                      int maxMisses, Action onDead, CancellationToken ct)
    {
        int misses = 0;                                  // 連続で失敗した回数
        using var timer = new PeriodicTimer(interval);   // interval ごとに目盛りを刻む
        try
        {
            while (await timer.WaitForNextTickAsync(ct).ConfigureAwait(false))
            {
                // ping 1 回あたりの待ち時間。ct の取り消しと、timeout の両方で止まる
                using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
                cts.CancelAfter(timeout);
                try
                {
                    await ping(cts.Token).ConfigureAwait(false);
                    misses = 0;                         // 1 回でも返れば、連続の数え直し
                }
                catch (Exception) when (!ct.IsCancellationRequested)
                {
                    // 時間切れも、切断の例外も、ここでは同じ「失敗」。maxMisses 回続いたら死亡と判定する
                    if (++misses >= maxMisses) { onDead(); return; }
                }
            }
        }
        catch (OperationCanceledException) { }          // 止められただけ
    }
}
```

`PeriodicTimer` は一定の間隔で目盛りを刻む `async` 向けのタイマーです。「連続して `maxMisses` 回、返事が来なかったら死んだ」と判定します。1 回の遅れで判定しないのは、ガベージ コレクションや短い処理の詰まりで、一瞬返事が遅れただけでエンジンを殺してしまわないためです。

エディタ側の使い方は次のとおりです。

```csharp title="使い方（第 57 章の Supervisor の LaunchAsync の中）"
_heartbeatCts = new CancellationTokenSource();
_ = Heartbeat.RunAsync(
    ct => client.RequestAsync("ping", null, TimeSpan.FromMilliseconds(500)),   // ping の返事を待つ時間
    interval: TimeSpan.FromSeconds(1),
    timeout: TimeSpan.FromSeconds(2),
    maxMisses: 3,
    onDead: () => OnDisconnected(process),     // 死んだ扱い。Disconnected と同じ立て直しに入る
    ct: _heartbeatCts.Token);
```

`onDead` が呼ぶのは `Disconnected` と同じ立て直しの処理です。固まったエンジンはプロセスとしては生きているので、第 57 章の `RecoverAsync` が `dead.Dispose()` で、強制的に終了させてから新しいエンジンを起動します。

<svg class="fig flow" viewBox="0 0 720 220" role="img" aria-label="ハートビートの時間の流れ。エンジンが固まると、1 秒ごとの ping が連続して 3 回失敗し、死亡の判定になる"><defs><marker id="teH" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">ハートビート（間隔 1 秒、3 回連続で失敗したら死亡）</text><line x1="30" y1="120" x2="700" y2="120" stroke="currentColor" stroke-width="2" marker-end="url(#teH)"/><text x="700" y="140" text-anchor="end" style="font-size:11px">時間</text><g stroke="#4c8bf5" stroke-width="3"><line x1="80" y1="100" x2="80" y2="140"/><line x1="200" y1="100" x2="200" y2="140"/></g><text x="80" y="92" text-anchor="middle" style="font-size:11px;font-weight:600">ping → 返事 ○</text><text x="200" y="92" text-anchor="middle" style="font-size:11px;font-weight:600">ping → 返事 ○</text><rect x="260" y="40" width="440" height="26" rx="8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="480" y="53" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">エンジンが固まる（TCP は ESTABLISHED のまま）</text><g stroke="#e5aa28" stroke-width="3"><line x1="320" y1="100" x2="320" y2="140"/><line x1="440" y1="100" x2="440" y2="140"/><line x1="560" y1="100" x2="560" y2="140"/></g><text x="320" y="164" text-anchor="middle" style="font-size:11px;font-weight:600">失敗 1</text><text x="440" y="164" text-anchor="middle" style="font-size:11px;font-weight:600">失敗 2</text><text x="560" y="164" text-anchor="middle" style="font-size:11px;font-weight:600">失敗 3</text><text x="640" y="104" text-anchor="middle" style="font-size:11px;font-weight:600">死亡と判定</text><line x1="640" y1="110" x2="640" y2="132" stroke="currentColor" stroke-width="2"/><text x="360" y="200" text-anchor="middle" style="font-size:12px">判定までの時間は、おおよそ「間隔 × 回数 ＋ 返事の待ち時間」以下。</text></svg>

### 時間の決め方

手元で間隔 500 ミリ秒、返事の待ち 500 ミリ秒、3 回連続の設定で `NtSuspendProcess` から判定までを測ると、1853 ミリ秒でした。おおよそ「間隔 × 回数」から「間隔 × 回数 ＋ 返事の待ち時間」の間に収まります（ここでは 1500〜2000 ミリ秒）。

実際の値は、2 つの兼ね合いで決めます。短くすれば固まりに早く気づけます。ただし、一瞬の遅れでまだ生きているエンジンを殺してしまう危険が上がります。長くすればその逆になります。この章の例は間隔 1 秒、3 回連続で最悪でも数秒で判定する値です。エンジンの処理が長い（重いシーンの読み込みなど）ことが分かっているならその間は `ping` を止めるか、判定を延ばす仕組みを足してください。

もう 1 つ開発中の落とし穴があります。エンジンにデバッガーをつないで、ブレークポイントで止めるとエンジンは固まった状態と同じです。数秒たつとハートビートが「死んだ」と判定して、エンジンを強制終了してしまいます。デバッグ中はハートビートを止める起動の引数（たとえば `--no-heartbeat`）を用意しておくことをおすすめします（これは筆者の見立てで、この章では作っていません）。


## 行儀のよい終了

エディタを閉じるとき、あるいはエンジンを入れ替えるときは、第 59 章の手順で閉じます。手元で確かめた結果です。

```text title="CloseGracefullyAsync（実測）"
[A] 行儀よく閉じる: 5 ms, エンジンの終了=True, 終了コード=0, Disconnected 通知=False
```

5 ミリ秒で閉じてエンジンは終了コード 0 で終わりました。`Disconnected` は飛んでいません。つまり、`EngineSupervisor` が「落ちた」と誤解して立て直しを始めることもありません。

流れは次のとおりです。

1. エディタが `shutdown` を送って、返事を待つ（第 54 章の `RemoteEngineService.Dispose`）。
2. エディタが `CloseGracefullyAsync` を呼ぶ。`_closing` を立てて `ShutdownSend` で `FIN` を送る。
3. エンジンの `ReadMessage` が `false` を返す。`CloseGracefully` で自分も `FIN` を送って相手の閉じるのを待つ。
4. エディタの読み取りのループが、EOF で終わる。
5. 両側が閉じる。エンジンの `ServeOnce` が `true` を返して、`main` が終了コード 0 で終わる。

もし、エンジンが固まっていて 3 が進まないときは、`CloseGracefullyAsync` の待ちが指定した時間（`wait`）で切れて、強制的に閉じます。そのあと第 55 章の `EngineProcess.Dispose` が、プロセスを強制終了します。


## 同じ PC の他のプログラムから守る

localhost のポートは <strong>同じ PC のどのプログラムからも繋げます</strong>。パイプのようにアクセス制御（ACL）で相手を絞ることは、ソケットでは手軽にはできません。そこで、3 つの守りを重ねます。

1. `127.0.0.1` だけで待ち受ける（外の PC からは、繋げない）。
2. `ExclusiveAddressUse`（C++ は `SO_EXCLUSIVEADDRUSE`）で、ポートを横取りされない。
3. 合言葉。違う相手は切る。

合言葉を足す理由は他のプログラムが、うっかりあるいは悪意でこのポートに何かを送ってくることがあるからです。特に、<strong>Web ブラウザー</strong>は要注意です。ブラウザー上の Web ページは `http://127.0.0.1:ポート番号/` に対して、リクエストを送れます。ページを開いただけでエンジンのポートに勝手に命令が届く可能性があります（この章では、ブラウザーからの送信は試していません。次の実験はプログラムから HTTP を送ったものです）。

実際に、HTTP のリクエストをエンジンのポートに送ってみました。

```text title="HTTP を送り付けられたとき（実測）"
[G] HTTP を送ると -> IOException
[G] そのあとも、エンジンは生きている: True
[G] 本物は繋がる: {"id":1,"ok":true,"result":null}
[G] 終了コード 0
```

HTTP の先頭 4 バイト `GET ` を長さとして読むと `0x20544547`、つまり 542,393,671 バイトです。16 MiB を大きく超えているので、サーバーは「壊れた長さ」として握手を打ち切り接続を切ります（その結果、送った側には `IOException` が見えました）。エンジンはそのあとも生きていて、本物のエディタは問題なく繋がります。

ただし、これはメッセージの形が HTTP と違うことによる偶然に近い守りです。合言葉まで知っている相手なら通ります。合言葉は <strong>推測できない値</strong>にして、標準入力で渡すことではじめて意味を持ちます。

守れないものもはっきりさせておきます。同じユーザーで動いている悪意のあるプログラムは、このやり方では防げません（そのプログラムは、エディタのメモリを読むこともエンジンのプロセスを操作することもできると考えられます。これは筆者の見立てです）。この章の合言葉は <strong>うっかり繋いできた無関係のプログラムとブラウザー経由の攻撃</strong>を防ぐためのものです。


## 偽のエンジンでテストする

第 54 章でパイプの向こうに偽のエンジンを置いて、テストしました。同じことを TCP でもできます。しかも偽のエンジンをテスト プロセスの中に作れます。ポートは 0 なので並行して動かしても、衝突しません。

次の偽のエンジンは返事をわざと 1 バイトずつ書きます。第 59 章で見たとおり TCP はメッセージの切れ目を保証しません。細切れの届き方でも `EngineClient` が組み立てられるかを確かめるためです。

```csharp title="Editor.Tests/SlowTcpEngine.cs（新規）"
using System.Net;
using System.Net.Sockets;
using System.Text;
using Editor.Engine;

// 返事を 1 バイトずつ書く、偽のエンジン。細切れで届く TCP を、わざと再現する
public sealed class SlowTcpEngine : IAsyncDisposable
{
    private readonly TcpListener _listener = new(IPAddress.Loopback, 0);   // ポート 0 = 空いている番号を OS が選ぶ
    private readonly Task _server;

    // テスト側が繋ぐ先。Start のあとでないと、LocalEndpoint は使えない
    public int Port => ((IPEndPoint)_listener.LocalEndpoint).Port;

    public SlowTcpEngine(string token)
    {
        _listener.Start();
        _server = Task.Run(async () =>
        {
            using Socket sock = await _listener.AcceptSocketAsync();
            sock.NoDelay = true;                                           // 1 バイトずつ書いても、溜めずにすぐ送る
            using var ns = new NetworkStream(sock);
            await Framing.ReadFrameAsync(ns);                              // 合言葉（この偽物は、確かめない）
            await Framing.WriteFrameAsync(ns, "ok"u8.ToArray());
            while (true)
            {
                // 要求を 1 つ読み、同じ id の返事を作る（エンジンの代役）
                byte[] req = await Framing.ReadFrameAsync(ns);
                int id = System.Text.Json.JsonDocument.Parse(req).RootElement.GetProperty("id").GetInt32();
                byte[] body = Encoding.UTF8.GetBytes($"{{\"id\":{id},\"ok\":true,\"result\":\"1 バイトずつ\"}}");
                var frame = new byte[4 + body.Length];                    // 長さ 4 バイト + 本文
                BitConverter.GetBytes(body.Length).CopyTo(frame, 0);
                body.CopyTo(frame, 4);
                foreach (byte b in frame)
                {
                    await ns.WriteAsync(new[] { b });                       // 1 バイトずつ
                    await Task.Delay(1);                                    // 次のバイトまで、少し待つ
                }
            }
        });
    }

    public async ValueTask DisposeAsync()
    {
        _listener.Stop();
        try { await _server; } catch { }                                    // 接続が切れて終わった例外は、ここでは気にしない
    }
}
```

使う側は第 54 章と同じ形です。

```csharp title="テストの本体（抜粋）"
await using var engine = new SlowTcpEngine("tok");
var client = new EngineClient(new TcpTransport(engine.Port, "tok"));
await client.ConnectAsync(2000);
var reply = await client.RequestAsync("ping");
Assert.Equal("1 バイトずつ", reply.GetProperty("result").GetString());
```

実際に、33 バイトのフレームが 1 バイトずつ届いても `EngineClient` は、正しく組み立てました（「1 バイトずつ」という本文をそのまま取り出せました）。

同じ `EngineClient` がパイプ版の偽のエンジンでもそのまま動くことも確かめました。`new EngineClient(new PipeTransport(name))` に替えるだけで `RequestAsync` は同じ結果を返します。この章の設計の目的、「通信路だけを差し替える」ことが、実際にできているということです。


## 確かめた結果

この章のコードを実際に動かして確かめた結果をまとめます（Windows 11、.NET 10、MSVC。値は 1 台の PC の結果）。

起動と接続：

- エンジンの起動からポートが分かるまで：約 50 ミリ秒
- 接続と握手：約 11 ミリ秒
- `EngineClient` の `RequestAsync` を直列に 5000 回呼んだ、1 往復の平均：約 55 マイクロ秒（JSON の組み立てと返事の読み取りを含む）
- 200 件の要求を同時に送って、全部の返事が返るまで：約 8 ミリ秒（`id` で、取り違えなく対応づけられた）

切断：

- `Kill` から `Disconnected` まで：約 1 ミリ秒
- `NtSuspendProcess` で固めてからハートビート（間隔 500 ミリ秒、3 回連続）が判定するまで：約 1.8 秒。その間、TCP は `ESTABLISHED` のまま
- `CloseGracefullyAsync`：約 5 ミリ秒。エンジンは終了コード 0 で終わり `Disconnected` は飛ばない

守り：

- 違う合言葉：`InvalidDataException`。エンジンは生きたままでそのあとの本物の接続は通る
- 繋いだだけで黙る相手：本物の握手が、約 3 秒待たされる（既知の限界）
- HTTP のリクエスト：切られる。エンジンは生きたまま

パイプの 1 往復（`EngineClient` 経由）はこの章では測り直していません。第 59 章の生のソケットの比較（パイプ 27.8 マイクロ秒、TCP 25.2 マイクロ秒）が、手元の目安です。


## よくあるミス

??? failure "ポートの通知を待たずに固定のポートへ connect する"
    何が起きるか：エンジンの起動より先に `connect` すると、待ち受けのないポートへの接続になり手元で約 2 秒かかって拒否されます。繰り返すとそのたびに 2 秒です。固定のポートだと前のエンジンが残っているとき `AddressAlreadyInUse` で起動に失敗します。

    対処：ポート 0 で待ち受けて、標準出力で通知します。エディタは通知を待ってから 1 回だけ `connect` します。

??? failure "標準出力の fflush を忘れる"
    何が起きるか：パイプに繋がった標準出力は、バッファされます。`port=NNNN` がバッファに留まったままエディタが時間切れまで待ち続けます。

    対処：`std::fflush(stdout)` を呼びます。標準出力はポートの通知だけにして、ログは標準エラーに書きます。

??? failure "合言葉をコマンド ライン引数に載せる"
    何が起きるか：同じ PC の他のプログラムが、プロセスの一覧から合言葉を読める場合があります。

    対処：標準入力で渡します。

??? failure "NetworkStream を繋がる前のソケットで作る"
    何が起きるか：`NetworkStream` のコンストラクターが、`IOException`（「非接続のソケットではこの操作は許可されません」）を投げます。

    対処：`ConnectAsync` が成功してから、`NetworkStream`（や `TcpStream`）を作ります。

??? failure "自分から閉じたのに、Disconnected が飛んで、エンジンが再起動される"
    何が起きるか：エディタを閉じる途中で、`EngineSupervisor` が「落ちた」と判断して新しいエンジンを起動してしまいます。

    対処：自分から閉じるときは `_closing` を立てて `Disconnected` を飛ばさないようにします。

??? failure "デバッガーでエンジンを止めたら、エンジンが強制終了された"
    何が起きるか：ブレークポイントで止まったエンジンは、固まった状態と同じです。ハートビートが死んだと判定します。

    対処：デバッグ中はハートビートを止める起動の引数を用意します。

??? failure "待ち受けを IPAddress.Any にする"
    何が起きるか：LAN の他の PC からも繋がる入り口になります。

    対処：`127.0.0.1` だけにします。`netstat` で `127.0.0.1:ポート` の `LISTENING` になっていることを確かめます（実測：`TCP 127.0.0.1:56384 0.0.0.0:0 LISTENING`）。


## これだけ覚える

- パイプから TCP への差し替えは、Stream の作り方だけ。`IEngineTransport` の窓口で両方残せる。
- エンジンは `127.0.0.1` のポート 0 で待ち受けて、標準出力で通知する。エディタはそれを待ってから 1 回だけ繋ぐ。
- 合言葉は毎回違う乱数にして、標準入力で渡す。違う相手は切って本物を待ち続ける。
- プロセスの死は TCP が教える。固まりはハートビートで見つける。
- 閉じるときは送信側を閉じて（`FIN`）、相手が閉じるのを待ってから `closesocket`。
- NetworkStream は繋がったあとの Socket で作る。


## 確かめたもの、確かめていないもの

!!! note "確かめたもの、確かめていないもの"
    確かめたもの：C++ の `TcpServer.cpp` は、MSVC で `/W4 /utf-8 /std:c++latest` のコンパイルが通った。C# の `EngineClient`（第 53 章のコードをこの章の形に直したもの）、`PipeTransport`、`TcpTransport`、`TcpStream`、`Framing`、`Heartbeat`、起動の `StartAsync`（ジョブ オブジェクトを除く）は、.NET 10 でコンパイルして、この章の `TcpServer.exe` と実際に繋いで動かした。合言葉の違い 1 バイトずつ届く返事、プロセスの `Kill`、`NtSuspendProcess` による固まり行儀のよい終了、起動の 3 通りの失敗、パイプ版の差し替えも動かして確かめた。
    確かめていないもの：第 55 章のジョブ オブジェクトと第 57 章の `EngineSupervisor` への組み込みは、この章の形で動かしていない（差分の説明だけ）。本物のエンジンの `Dispatch` と繋いでいない。`TcpKeepAliveTime` などの設定は設定が通ることまでしか確かめていない（固まりに効かないという説明は、TCP の仕組みからの推論）。デバッガーでエンジンを止めたときの挙動は、試していない。

## 参考資料

- W. Eddy (Ed.), *Transmission Control Protocol (TCP)*, RFC 9293, 2022 年 8 月。keep-alive（§3.8.4）、半閉じ（§3.6）。読んだ範囲は第 59 章の「参考資料」に書いた。
- Microsoft Learn「Use TcpClient and TcpListener」（.NET）。`TcpListener.Start`、`AcceptSocketAsync`、`NetworkStream` の所有権。
- Microsoft Learn「SOL_SOCKET Socket Options」（Win32）。`SO_EXCLUSIVEADDRUSE`、`SO_RCVTIMEO`、`SO_KEEPALIVE`。
- Microsoft Learn「Graceful Shutdown, Linger Options, and Socket Closure」（Win32）。`shutdown` と `closesocket` の使い分け。
- Microsoft Learn「Getting started with Winsock」（Win32）。`WSAStartup` を RAII で守ることと `getaddrinfo` の勧め。

読んでいないもの：Winsock の非同期 I/O（IOCP、`WSAPoll`）の資料。この章のサーバーはブロッキングの `recv` と `send` で、1 人のエディタを相手にする作りです。複数の接続を同時に扱う本格的なサーバーには、別の作りが必要です。


## 関連ページ

- [第 59 章 TCP を深く知る：バイトの流れとして使うために](59-tcp-deep.md)
- [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)
- [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)
- [第 55 章 エンジンをサーバーにする：EngineHost](55-engine-host.md)
- [第 57 章 落ちたら立て直す](57-recovery.md)
- [第 58 章 AI から操作する：MCP](58-mcp.md)

次はこの部のまとめです。[第 61 章 まとめとこれから](61-next-steps.md) へ進みます。

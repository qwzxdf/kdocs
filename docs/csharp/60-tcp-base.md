---
title: 第 60 章 TCP 編の土台：最小のエンジンとエディタを繋ぐ
tags:
  - C#連携
  - TCP
---

# 第 60 章 TCP 編の土台：最小のエンジンとエディタを繋ぐ

第 59 章で TCP の性質を見ました。この章ではその知識を使って <strong>エンジンのプロセスとエディタ側のクライアントを、TCP で繋ぐ最小の構成</strong>を作ります。前の章（第 53〜57 章）のコードを開かなくても、この章だけで最後まで動かせるように書きます。

作るものは 2 つです。1 つは C++ の小さなサーバーです。`127.0.0.1` のポートで待ち受けて命令を 1 つ受け取るたびに返事を 1 つ返します。もう 1 つは C# のクライアントです。命令を送って返事を `await` で待ちます。複数の命令を同時に送っても返事を取り違えません。

エンジンの中身（描画、シーン）はこの章には出てきません。命令は `ping`（生きているかの確認）と `add`（足し算）の 2 つだけです。中身が空なのは <strong>通信の部分だけを先に完成させる</strong>ためです。自分のプロジェクトに入れるときは、`Dispatch`（命令の振り分け）の中身を自分のエンジンの処理に替えれば、通信の部分はそのまま使えます。

前提は C# と C++ の基本的な読み書きだけです。TCP の性質（`Read` が欲しい分だけ返らないこと、`Write` が止まること、切断の仕方）は、第 59 章に書いてあります。この章のコードの理由づけに何度か出てきます。

!!! info "このページを読む前に"
    - [第 59 章 TCP を深く知る：バイトの流れとして使うために](59-tcp-deep.md)（前の章。TCP の性質とこの章の設計の根拠）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）

!!! abstract "この章で作るもの"
    - `TcpServer.cpp`（C++）：Winsock のサーバー。長さ付きの JSON を読んで、返事を書く。合言葉の確認つき
    - `Framing.cs`、`TcpStream.cs`、`TcpTransport.cs`（C#）：長さ付きメッセージと TCP の接続
    - `EngineClient.cs`（C#）：要求を送って、返事を `id` で待つ
    - `Program.cs`（C#）：エンジンを起動して、命令を送る確認用のコンソール アプリ

## なぜ TCP 版も作るのか

パイプ版ですでに動いています。それでも TCP 版を足す理由は 3 つあります。

1 つめは <strong>エディタ以外のプログラムが、エンジンに繋ぎやすくなる</strong>ことです。Python のテスト スクリプトも第 58 章の MCP を橋渡しするプログラムも、ソケットならほぼどの言語からでも標準の機能だけで繋げます。名前付きパイプは言語によっては扱いが面倒なことがあります。

2 つめは接続先の決め方が単純になることです。名前付きパイプは名前の衝突を避けるために名前に世代番号を付けるなどの工夫が要ります。TCP はポート 0 で待ち受ければ、OS が空いている番号を選んでくれます。衝突はそもそも起きません。

3 つめは将来の選択肢です。同じメッセージの形のまま別の PC のエンジンに繋ぐ構成にも広げられます。この教材ではそこまで扱いません。ただ、窓口を作っておけばその道は閉じません。

ではパイプを捨てて TCP に統一するべきでしょうか。第 59 章で測ったとおり往復の時間はほぼ同じで、性能は理由になりません。<strong>両方を残して起動の引数で選べる</strong>ようにします。通信の不具合が出たときに通信路を替えて、原因を切り分けられるからです。


## メッセージの形

TCP はバイトの流れを運ぶだけで、メッセージの切れ目を知りません（第 59 章）。そこで、アプリの側でメッセージの形を決めます。

<svg class="fig flow" viewBox="0 0 720 262" role="img" aria-label="メッセージは 4 バイトの長さと JSON の本文でできている。要求と返事は id で対応づける"><defs><marker id="tbB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">1 つのメッセージと、要求・返事の対応</text><rect x="16" y="38" width="110" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="71" y="60" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">長さ N（4 バイト）</text><rect x="126" y="38" width="430" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="341" y="60" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">本文 N バイト（UTF-8 の JSON）</text><text x="570" y="55" style="font-size:12px;font-weight:400">先に長さを読めば、</text><text x="570" y="73" style="font-size:12px;font-weight:400">どこまでが 1 つか分かる</text><text x="100" y="124" text-anchor="middle" style="font-size:13px;font-weight:600">エディタ（C#）</text><text x="620" y="124" text-anchor="middle" style="font-size:13px;font-weight:600">エンジン（C++）</text><line x1="100" y1="134" x2="100" y2="248" stroke="#94a3b8" stroke-width="2"/><line x1="620" y1="134" x2="620" y2="248" stroke="#94a3b8" stroke-width="2"/><line x1="100" y1="152" x2="620" y2="164" stroke="currentColor" stroke-width="2" marker-end="url(#tbB)"/><text x="360" y="150" text-anchor="middle" style="font-size:12px;font-weight:400">id=1  add</text><line x1="100" y1="180" x2="620" y2="192" stroke="currentColor" stroke-width="2" marker-end="url(#tbB)"/><text x="360" y="178" text-anchor="middle" style="font-size:12px;font-weight:400">id=2  ping</text><line x1="620" y1="206" x2="100" y2="218" stroke="currentColor" stroke-width="2" marker-end="url(#tbB)"/><text x="360" y="204" text-anchor="middle" style="font-size:12px;font-weight:400">id=1  ok</text><line x1="620" y1="232" x2="100" y2="244" stroke="currentColor" stroke-width="2" marker-end="url(#tbB)"/><text x="360" y="230" text-anchor="middle" style="font-size:12px;font-weight:400">id=2  ok</text></svg>

長さは 4 バイトの整数（リトル エンディアン）です。x64 の Windows の C++ も C# の `BinaryPrimitives` もそのまま読み書きできます。長さの上限は 16 MiB と決めます。HTTP の先頭の `GET ` を長さとして読むと約 5.4 億バイトになります。壊れた長さを信じて巨大なメモリを確保しないための上限です。

本文の JSON は要求と返事で、次の形にします。

```json
{"id": 7, "cmd": "add", "args": {"a": 20, "b": 22}}
{"id": 7, "ok": true, "result": 42}
{"id": 8, "ok": false, "error": "unknown command: foo"}
```

要求の `id` はクライアントが決める通し番号です。返事には同じ `id` を入れて返します。これで返事が来た順番を気にせずどの要求への返事かを突き合わせられます。複数の要求を返事を待たずに送れるので、返事を待つ間も UI が止まりません。

`ok` が `false` のときは `error` に理由を入れます。これは <strong>エンジンが「失敗です」と答えた</strong>場合で、接続は生きています。エンジンが消えて接続が切れた場合とは、別の失敗です。クライアントは前者を `EngineCommandException`、後者を `EngineDisconnectedException` として別の例外にします。

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

<svg class="fig flow" viewBox="0 0 720 420" role="img" aria-label="エディタがエンジンを起動し、標準入力で合言葉を渡し、エンジンが 127.0.0.1 のポート 0 で待ち受けて標準出力にポート番号を書き、エディタが接続して合言葉を送り、ok が返ったら要求と返事を始め、最後に送信側を閉じて終わる"><defs><marker id="teA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">起動から終了まで（番号の順に進む）</text><text x="110" y="50" text-anchor="middle" style="font-size:13px;font-weight:600">エディタ</text><text x="610" y="50" text-anchor="middle" style="font-size:13px;font-weight:600">EngineHost</text><line x1="110" y1="60" x2="110" y2="408" stroke="#94a3b8" stroke-width="2"/><line x1="610" y1="60" x2="610" y2="408" stroke="#94a3b8" stroke-width="2"/><line x1="110" y1="80" x2="610" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="74" text-anchor="middle" style="font-size:12px;font-weight:600">① プロセスを起動</text><line x1="110" y1="112" x2="610" y2="112" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="106" text-anchor="middle" style="font-size:12px;font-weight:600">② 標準入力：合言葉（毎回違う乱数）</text><rect x="470" y="124" width="236" height="30" rx="8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="588" y="139" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">127.0.0.1 のポート 0 で listen</text><line x1="610" y1="184" x2="110" y2="184" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="178" text-anchor="middle" style="font-size:12px;font-weight:600">③ 標準出力：port=NNNN</text><line x1="110" y1="220" x2="610" y2="220" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="214" text-anchor="middle" style="font-size:12px;font-weight:600">④ connect ＋ 合言葉の 1 通目</text><line x1="610" y1="252" x2="110" y2="252" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="246" text-anchor="middle" style="font-size:12px;font-weight:600">⑤ "ok"（違う合言葉なら、何も返さず切る）</text><rect x="14" y="268" width="196" height="30" rx="8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="112" y="283" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">要求と返事（EngineClient）</text><line x1="110" y1="318" x2="610" y2="318" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="312" text-anchor="middle" style="font-size:12px;font-weight:600">⑥ 送信側を閉じる（FIN）</text><line x1="610" y1="354" x2="110" y2="354" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="348" text-anchor="middle" style="font-size:12px;font-weight:600">⑦ エンジンも送信側を閉じる（FIN）</text><text x="360" y="394" text-anchor="middle" style="font-size:12px">⑧ 両方が closesocket。EngineHost のプロセスは、終了コード 0 で終わる。</text></svg>

①〜③ の間、エディタは<strong>エンジンの標準出力を読んで待つ</strong>だけです。`connect` は③ で番号が分かってから、1 回だけ呼びます。


## EngineClient：Stream の上に、要求と返事を載せる

C# 側の中心は `EngineClient` です。命令を送って返事を待つ役目を持ちます。TCP の細かいこと（ソケット、握手）は `Stream` を作る部分に分けておいて、`EngineClient` は `Stream` だけを知る作りにします。

まず、`Stream` を作る窓口です。

```csharp title="Editor/Engine/IEngineTransport.cs（新規）"
namespace Editor.Engine;

// 「どうやって Stream を作るか」だけを差し替える窓口。EngineClient は、この先を知らない
public interface IEngineTransport
{
    // 時間内に繋がらなければ TimeoutException
    Task<Stream> ConnectAsync(TimeSpan timeout, CancellationToken ct = default);
}

// 送信側だけを閉じられる Stream（TCP の FIN）
public interface IHalfCloseable
{
    void ShutdownSend();
}
```

`IEngineTransport` は 1 つのメソッドだけです。この章では TCP 版（`TcpTransport`）を 1 つ作ります。窓口にしておく利点は通信路を差し替えられることです。たとえば、テスト用の偽の通信路や名前付きパイプに `EngineClient` を変えずに替えられます（第 61 章）。`IHalfCloseable` は第 59 章で見た半閉じ（送信側だけ閉じる）を表します。

次が `EngineClient` の全体です。ファイルの先頭と 2 つの例外から始めます。

```csharp title="Editor/Engine/EngineClient.cs（新規）"
using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.IO;
using System.Text.Json;
using System.Threading;

namespace Editor.Engine;

// エンジンが落ちた（接続が切れた）ことを表す例外
public sealed class EngineDisconnectedException : IOException
{
    public EngineDisconnectedException() : base("エンジンとの接続が切れました。") { }
}

// エンジンが「失敗」を返したことを表す例外（接続は生きている）
public sealed class EngineCommandException(string message) : Exception(message);
```

失敗を 2 つの例外に分けているのが、設計の要です。`EngineCommandException` はエンジンが「その操作はできません」と答えた場合で、画面にメッセージを出せば済みます。`EngineDisconnectedException` はエンジンのプロセスが消えた場合で、再接続や復旧の合図です。両方を同じ `Exception` で受けると「単なる失敗」と「相手が消えた」を見分けられません。

```csharp title="Editor/Engine/EngineClient.cs（続き：フィールドと接続）"
public sealed class EngineClient : IAsyncDisposable
{
    private const int MaxMessageSize = 16 * 1024 * 1024;

    private readonly IEngineTransport _transport;
    private Stream? _stream;                       // 接続できたあとに入る
    private volatile bool _closing;                // 自分から閉じている最中（切断を、異常として知らせない）
    private readonly SemaphoreSlim _writeLock = new(1, 1);
    private readonly ConcurrentDictionary<int, TaskCompletionSource<JsonElement>> _pending = new();
    private int _nextId;
    private Task? _readLoop;

    // 接続が切れたときに呼ばれる（スレッド プールのスレッドから）。UI を触るなら Dispatcher を通す
    public event Action? Disconnected;

    public EngineClient(IEngineTransport transport) => _transport = transport;

    public async Task ConnectAsync(int timeoutMs = 5000)
    {
        _stream = await _transport.ConnectAsync(TimeSpan.FromMilliseconds(timeoutMs)).ConfigureAwait(false);   // 時間内に繋がらなければ TimeoutException
        _readLoop = Task.Run(ReadLoopAsync);     // 返事を読むループを、別のタスクで回す
    }
}
```

`_pending` は「返事待ちの表」です。キーが要求の `id`、値が `TaskCompletionSource` でこれは「あとで結果を入れられる `Task`」を作る道具です。呼び出し側はこの `Task` を `await` します。返事を読むループが結果を入れた瞬間に続きが動き出します。複数のスレッドから触るので `ConcurrentDictionary` を使います。

`_closing` は自分から閉じている最中かどうかの旗です。後で使います。`ConnectAsync` は窓口から `Stream` を受け取って、<strong>返事を読むループを別のタスクで回し始めます</strong>。第 59 章で見たとおり読むループを書く処理と別に回しておかないと両側が書き合って動けなくなる危険があるからです。

```csharp title="Editor/Engine/EngineClient.cs（続き：要求を送って、返事を待つ）"
    // 命令を 1 つ送って、返事を待つ。返事が来るまで UI スレッドは止まらない（await）
    public async Task<JsonElement> RequestAsync(string cmd, object? args = null, TimeSpan? timeout = null)
    {
        int id = Interlocked.Increment(ref _nextId);      // 要求ごとの通し番号（スレッドが違っても重ならない）
        var tcs = new TaskCompletionSource<JsonElement>(TaskCreationOptions.RunContinuationsAsynchronously);
        _pending[id] = tcs;                                // 送る前に登録する（返事が先に届いても、取りこぼさない）
        try
        {
            await WriteMessageAsync(JsonSerializer.SerializeToUtf8Bytes(new { id, cmd, args })).ConfigureAwait(false);

            // 制限時間が来たら、待っている tcs に TimeoutException を入れる
            var limit = timeout ?? TimeSpan.FromSeconds(5);
            using var cts = new CancellationTokenSource(limit);
            using (cts.Token.Register(() => tcs.TrySetException(
                       new TimeoutException($"'{cmd}' の返事が {limit.TotalSeconds} 秒以内に来ませんでした。"))))
            {
                JsonElement reply = await tcs.Task.ConfigureAwait(false);   // 読むループが、返事を入れるまで待つ
                if (!reply.GetProperty("ok").GetBoolean())
                {
                    // エンジンが「失敗です」と答えた。接続は生きている
                    throw new EngineCommandException(reply.GetProperty("error").GetString() ?? "(理由なし)");
                }
                return reply;
            }
        }
        finally
        {
            _pending.TryRemove(id, out _);                 // 成功・失敗・時間切れのどれでも、表に残さない
        }
    }
```

`Interlocked.Increment` は複数のスレッドが同時に呼んでも重ならない番号を振ります。各 `await` の後ろの `.ConfigureAwait(false)` は「続きを元のスレッドに戻さなくてよい」という指定です。WPF の UI スレッドには続きを UI スレッドで動かす仕組み（同期コンテキスト）があります。この指定がないと UI スレッドから `RequestAsync(...).Result` のように待った瞬間に続きが UI スレッドの空きを待ち、UI スレッドは結果を待つという行き違いで固まります。通信のような部品の中では付けておくのが決まりです。

`TaskCreationOptions.RunContinuationsAsynchronously` は返事を読むループが `TrySetResult` した瞬間に `await` の続きが、そのスレッドで同期的に走ってしまうのを避ける指定です。これを付けないと返事を読むループの中で、呼び出し側の処理が動いてしまい次の返事の読み取りが遅れます。

時間切れは `CancellationTokenSource` に制限時間を渡し、時間が来たら `tcs` に例外を入れる、という仕組みです。時間切れで呼び出し側が諦めたあとに遅れて返事が届いても、`_pending` に `id` が残っていないので、読み取りのループがその返事を黙って捨てます。`finally` で `_pending` から必ず取り除くのは、成功でも失敗でも時間切れでも表に残さないためです。残すと表が増え続けます。

```csharp title="Editor/Engine/EngineClient.cs（続き：書き込み）"
    private Stream Stream => _stream ?? throw new InvalidOperationException("ConnectAsync が先に必要です。");

    private async Task WriteMessageAsync(byte[] body)
    {
        var frame = new byte[4 + body.Length];                       // 長さ 4 バイト + 本文を、1 つの配列にまとめる
        BinaryPrimitives.WriteInt32LittleEndian(frame, body.Length);  // 長さはリトル エンディアン（C++ 側と同じ）
        body.CopyTo(frame, 4);

        await _writeLock.WaitAsync().ConfigureAwait(false);            // 複数の命令が同時に書いても、バイトが交ざらないようにする
        try
        {
            await Stream.WriteAsync(frame).ConfigureAwait(false);       // 1 回の Write（Nagle と遅延 ACK の待ち合わせを避ける）
            await Stream.FlushAsync().ConfigureAwait(false);
        }
        catch (IOException)
        {
            throw new EngineDisconnectedException();   // 切れた接続への書き込みは、切断として扱う
        }
        finally
        {
            _writeLock.Release();
        }
    }
```

`SemaphoreSlim` の `_writeLock` は書き込みの順番待ちの列を作ります。2 つのタスクが同時に `WriteAsync` を呼ぶとバイトが途中で交ざり受けた側の長さの解釈が壊れます。長さと本文を 1 つの配列 `frame` にまとめて、1 回の `WriteAsync` で書くのは第 59 章で見た Nagle と遅延 ACK の待ち合わせを避けるためでもあります。切れた接続への書き込みは `IOException` になるので、`EngineDisconnectedException` に翻訳します。

```csharp title="Editor/Engine/EngineClient.cs（続き：返事を読むループ）"
    private async Task ReadLoopAsync()
    {
        var header = new byte[4];
        try
        {
            while (true)
            {
                await Stream.ReadExactlyAsync(header).ConfigureAwait(false);
                int length = BinaryPrimitives.ReadInt32LittleEndian(header);
                if (length < 0 || length > MaxMessageSize)
                {
                    throw new InvalidDataException($"不正なメッセージ長: {length}");
                }

                var body = new byte[length];
                await Stream.ReadExactlyAsync(body).ConfigureAwait(false);

                using var doc = JsonDocument.Parse(body);
                JsonElement root = doc.RootElement;
                if (root.TryGetProperty("id", out var idProp) && _pending.TryGetValue(idProp.GetInt32(), out var tcs))
                {
                    tcs.TrySetResult(root.Clone());   // doc を閉じたあとも使えるように複製する
                }
                // id のないメッセージは、エンジンからの通知（あとの章）
            }
        }
        catch (Exception e) when (e is IOException or ObjectDisposedException or InvalidDataException or JsonException)
        {
            // 切断、または壊れたデータ。どちらも、これ以上続けられない
        }
        finally
        {
            foreach (var tcs in _pending.Values)
            {
                tcs.TrySetException(new EngineDisconnectedException());   // 待っている全員に知らせる
            }
            if (!_closing) Disconnected?.Invoke();       // 自分から閉じたときは、「落ちた」とは知らせない
        }
    }
```

`ReadExactlyAsync` は指定したバイト数が揃うまで待つメソッドです。TCP は細切れで届くので長さも本文もこれで読みます。相手が閉じれば `EndOfStreamException`（`IOException` の仲間）を投げるので、`catch` に入ります。`finally` では返事待ちの全員に `EngineDisconnectedException` を渡します。待っている呼び出しが永遠に待ち続けないためです。`Disconnected` の通知は自分から閉じたとき（`_closing`）には出しません。自分で閉じただけなのに「エンジンが落ちた」と受け取られるのを防ぐためです。

```csharp title="Editor/Engine/EngineClient.cs（続き：閉じ方）"
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
}
```

`CloseGracefullyAsync` は第 59 章の「正しい閉じ方」のクライアント側の手順です。`ShutdownSend` で `FIN` を送ります。するとエンジンの側が読み終えて、自分も閉じます。こちらの読み取りのループが EOF で終わるのを `wait` を上限に待ちます。相手が応答しなくても `wait` を過ぎれば、強制的に `DisposeAsync` します。

### 同期のコードから呼ぶとき

`RequestAsync` は `Task` を返す非同期のメソッドです。エンジンへの命令が同期のコードの中にあるなら結果を待ってから進む形にできます。

```csharp
// 同期のコードから呼ぶ。UI スレッドでは呼ばない（エンジンが固まると、時間切れまで UI が固まる）
JsonElement reply = client.RequestAsync("add", new { a = 1, b = 2 }).GetAwaiter().GetResult();
```

`.GetAwaiter().GetResult()` は `.Result` や `.Wait()` と違って失敗したときに `AggregateException` に包まず元の例外（`EngineCommandException` など）をそのまま投げ直します。呼ぶ側が `catch (EngineCommandException)` と書けるのはこの性質のおかげです。ただし、UI スレッドから呼んではいけません。エンジンが固まったとき時間切れまでウィンドウが固まります。描画スレッドのような専用のスレッドから呼んでください。

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

握手の 1 通目は合言葉を長さ付きのメッセージとして送ります。`Framing`（次のコード）は `EngineClient` の `WriteMessageAsync` と `ReadLoopAsync` と同じ処理を取り出して関数にしたものです。

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

`EngineClient` 本体の `WriteMessageAsync` と `ReadLoopAsync` も本当は `Framing` を呼ぶ形に整理できます。この章では説明しやすいように `EngineClient` の中にそのまま書いてあります。


## EngineHost 側：Winsock のサーバー

エンジンの側です。「1 人のエディタを相手にして、その人が終われば戻る」サーバーを Winsock で作ります。戻り値の `false` は待ち受けを始められなかったことを表します（`main` は、終了コード 2 で終わります）。

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

呼び出す関数の順は `socket`（作る）→ `bind`（アドレスとポートに結びつける）→ `listen`（待ち受けを始める）です。第 59 章で見た `TcpListener.Start()` の中身です。`htons` と `ntohs` はポート番号をネットワーク バイト オーダー（ビッグ エンディアン）と、手元の並びの間で変換します。TCP のヘッダーの数値はビッグ エンディアンで運ぶ決まりです。この章の「長さ付きメッセージ」の長さは、アプリの取り決めでリトル エンディアンにしています。2 つが別の約束であることに注意してください。

`SO_EXCLUSIVEADDRUSE` は `bind` の前に設定します。第 59 章のとおり他のソケットが同じアドレスとポートに割り込めないようにする設定です。`inet_pton` で文字列の `127.0.0.1` をアドレスの構造体に変換します。`INADDR_ANY` を渡してしまうと LAN に開きます。この 1 行が第 59 章の「`IPAddress.Any` は絶対に避ける」に当たります。`listen` の第 2 引数（4）は待ち行列の長さです。繋ぎにくるのは 1 人のエディタだけなので、小さくて足ります。`getsockname` で OS が選んだポート番号を聞き出します。

読み書きの道具は `ReadExact` と `WriteExact` と呼ぶソケットの関数です。

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

長さの上限は 16 MiB です。これは前に述べた上限と同じ値で、「壊れた長さを信じて巨大な確保をしない」ためです。`WriteMessage` が長さと本文を `frame` 1 つにまとめて、1 回の `send` で送るのは第 59 章で見たとおり Nagle と遅延 ACK の待ち合わせを避けるためです。

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
// 戻り値: false = 待ち受けを始められなかった
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

`std::printf("port=%u\n", port)` と `fflush` がエディタへの合図です。標準出力はパイプに繋がれていると、バッファされてすぐには流れません。`fflush` を忘れるとエディタがポートの通知を待ち続けます。標準出力はポートの通知だけに使いログは標準エラーに書いてください（標準エラーは、バッファされません）。

`ServeOnce` に渡す `Dispatch` が命令の振り分けです。要求 1 つにつき返事を 1 つ作ります。返事には要求の `id` をそのまま写します。`id` を読めない壊れた要求には `id` を `null` にして返します。

```cpp title="EngineHost/TcpServer.cpp（続き：命令の振り分けと main）"
// ---- 命令の振り分け（代役）----
// 本物は、JSON ライブラリ（nlohmann など）で読む。
// ここでは、文字列から "cmd" と数字を拾うだけの、最小の読み方にしている。
std::string FindString(const std::string& json, const std::string& key) {
  const std::string pattern = "\"" + key + "\":\"";
  const auto pos = json.find(pattern);
  if (pos == std::string::npos) return {};
  const auto begin = pos + pattern.size();
  return json.substr(begin, json.find('"', begin) - begin);
}

long long FindNumber(const std::string& json, const std::string& key) {
  const std::string pattern = "\"" + key + "\":";
  const auto pos = json.find(pattern);
  return pos == std::string::npos ? 0 : std::atoll(json.c_str() + pos + pattern.size());
}

// 要求 1 つにつき、返事を 1 つ作る。返事には、要求の id をそのまま写す
std::string Dispatch(const std::string& request) {
  const std::string id = request.find("\"id\":") == std::string::npos
                             ? "null"
                             : std::to_string(FindNumber(request, "id"));
  const std::string cmd = FindString(request, "cmd");

  if (cmd == "ping") {
    return "{\"id\":" + id + ",\"ok\":true,\"result\":\"pong\"}";
  }
  if (cmd == "add") {   // 引数つきの命令の例: {"cmd":"add","args":{"a":1,"b":2}}
    const long long sum = FindNumber(request, "a") + FindNumber(request, "b");
    return "{\"id\":" + id + ",\"ok\":true,\"result\":" + std::to_string(sum) + "}";
  }
  // 知らない命令: 接続は生きたまま、「失敗です」と答える（EngineCommandException になる）
  return "{\"id\":" + id + ",\"ok\":false,\"error\":\"unknown command: " + cmd + "\"}";
}

int main() {
  // 合言葉は、コマンド ライン引数ではなく標準入力の 1 行目で受け取る
  std::string token;
  std::getline(std::cin, token);
  if (!token.empty() && token.back() == '
') token.pop_back();

  WinsockSession wsa;
  if (!wsa.ok()) return 1;

  const bool served = ServeOnce(token, Dispatch);
  return served ? 0 : 2;    // 2 = 待ち受けを始められなかった
}
```

`ping` は生きているかの確認で `pong` と返します。`add` は引数（`args` の `a` と `b`）を使う命令の例です。どちらでもない命令には `ok: false` と理由の `error` を返します。接続は生きたままでクライアントでは `EngineCommandException` になります。

`FindString` と `FindNumber` は文字列から `"cmd"` と数字を拾うだけの確認用の最小の読み方です。本物のエンジンでは JSON ライブラリ（nlohmann など）で読んで、命令の名前から処理への表を引きます。命令の足し方は `if (cmd == "...")` を増やすか表に登録するだけです。

`main` は合言葉を標準入力から読んで、`ServeOnce` を呼ぶだけです。標準入力から読む理由はコマンド ライン引数に載せると、同じ PC の他のプログラムから、プロセスの一覧で読める場合があるからです。

`/utf-8` を付けてコンパイルすることを忘れないでください。付けないと日本語のコメントの文字コードの解釈（既定は Shift_JIS 系のコード ページ）がずれて、コンパイルが失敗します（実際に手元でもそうなりました）。

このコードは `/W4 /utf-8 /std:c++latest` で警告なしにコンパイルできました。そして、この章の C# のクライアントと実際に繋いで、すべての動作を確かめています。


## 動かして確かめる

エンジンとクライアントを実際に動かします。

### エンジンをビルドする

`TcpServer.cpp` を Visual Studio の「Developer PowerShell」（または、x64 の開発者コマンド プロンプト）で、コンパイルします。

```powershell
cl /std:c++latest /EHsc /W4 /utf-8 TcpServer.cpp
```

`/utf-8` はソースの文字コードを UTF-8 と見なす指定で、日本語のコメントのために必要です。`/W4` は警告を多めに出す指定です。このコードは警告なしで通りました。できた `TcpServer.exe` を C# のコンソール アプリから起動します。

### クライアントを書く

C# のコンソール アプリを作って `Framing.cs`、`TcpStream.cs`、`TcpTransport.cs`、`EngineClient.cs`、`IEngineTransport.cs` を追加します。`Program.cs` は次のとおりです。

```csharp title="Program.cs"
using System.Diagnostics;
using System.Security.Cryptography;
using Editor.Engine;

// エンジンの起動: 合言葉を標準入力へ渡し、標準出力の "port=NNNN" を読む（最小の形）
var exe = @"C:\path\to\TcpServer.exe";                       // ビルドした exe のパス
string token = Convert.ToHexString(RandomNumberGenerator.GetBytes(16));   // 起動のたびに違う乱数
var info = new ProcessStartInfo(exe)
{
    UseShellExecute = false,
    RedirectStandardInput = true,      // 合言葉を渡す
    RedirectStandardOutput = true,     // ポート番号を受け取る
};
using Process engine = Process.Start(info)!;
engine.StandardInput.WriteLine(token);
engine.StandardInput.Flush();
string line = engine.StandardOutput.ReadLine()!;          // "port=56789"
int port = int.Parse(line["port=".Length..]);
Console.WriteLine($"エンジンが待ち受け中: 127.0.0.1:{port}");

// 繋いで、命令を送る
var client = new EngineClient(new TcpTransport(port, token));
await client.ConnectAsync(timeoutMs: 2000);

var pong = await client.RequestAsync("ping");
Console.WriteLine($"ping -> {pong.GetProperty("result").GetString()}");

var sum = await client.RequestAsync("add", new { a = 20, b = 22 });
Console.WriteLine($"add(20, 22) -> {sum.GetProperty("result").GetInt32()}");

try
{
    await client.RequestAsync("no_such_command");               // エンジンが「失敗です」と答える
}
catch (EngineCommandException e)
{
    Console.WriteLine($"知らない命令 -> EngineCommandException: {e.Message}");
}

// 同時に 100 件。返事は id で、取り違えなく対応づく
var tasks = Enumerable.Range(0, 100).Select(i => client.RequestAsync("add", new { a = i, b = 1 })).ToArray();
var results = await Task.WhenAll(tasks);
bool allCorrect = results.Select((r, i) => r.GetProperty("result").GetInt32() == i + 1).All(x => x);
Console.WriteLine($"100 件を同時に送った結果が、すべて正しい: {allCorrect}");

// 行儀よく閉じる
await client.CloseGracefullyAsync(TimeSpan.FromSeconds(2));
engine.WaitForExit(3000);
Console.WriteLine($"エンジンの終了コード: {engine.ExitCode}");
```

エンジンを起動して標準入力に合言葉を書き標準出力の 1 行目からポート番号を読みます。それから `TcpTransport` で繋ぎます。ここまでがエディタがエンジンを使い始める一連の流れです。

```text title="実行結果（実測）"
エンジンが待ち受け中: 127.0.0.1:57988
ping -> pong
add(20, 22) -> 42
知らない命令 -> EngineCommandException: unknown command: no_such_command
100 件を同時に送った結果が、すべて正しい: True
エンジンの終了コード: 0
```

`ping` と `add` がエンジンから返ってきました。知らない命令には `ok: false` の返事が返りクライアントでは `EngineCommandException` になります。接続は生きたままです。100 件を返事を待たずに同時に送っても、すべて正しい返事が正しい要求に結びつきました。`id` の対応づけが働いています。最後に、行儀よく閉じるとエンジンは終了コード 0 で終わります。

このコードは、.NET 10 と MSVC で、実際にコンパイルして動かして確かめました。

## 自分のエンジンに入れるには

土台ができたので自分のエンジンに入れる手順をまとめます。

1. `TcpServer.cpp` の `Dispatch` を自分のエンジンの命令の処理に替える。JSON の読み書きには nlohmann などのライブラリを使う。この章の `FindString` と `FindNumber` は確認用の代役です。
2. 命令を 1 つ足すたびに `ping` と同じ要領で、クライアントから呼んで返事を確かめる。
3. エンジンを動かす役目（起動、見張り、ハートビート、終了、再起動）は[第 61 章](61-tcp-engine.md)で、エディタの構造に組み込む。

## これだけ覚える

- メッセージは 4 バイトの長さ＋ UTF-8 の JSON。長さと本文は 1 回の `Write` で書く。長さの上限は 16 MiB。
- 要求には `id` を付け返事に写す。返事は `id` で返事待ちの表から探す。
- 失敗は 2 種類。エンジンの「失敗です」（`EngineCommandException`）と接続の切れ（`EngineDisconnectedException`）。
- 読むループは書く処理とは別のタスクで、常に回す。
- 待ち受けは `127.0.0.1` だけ。ポートは 0 で OS に選ばせエンジンが標準出力で知らせる。合言葉は標準入力で渡す。

## 関連ページ

- [第 59 章 TCP を深く知る：バイトの流れとして使うために](59-tcp-deep.md)
- [第 61 章 TCP 編の実装：エディタに組み込む](61-tcp-engine.md)（起動、ハートビート、終了、守り、テスト）

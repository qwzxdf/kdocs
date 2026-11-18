---
title: 第 61 章 TCP 編の実装：エディタに組み込む
tags:
  - C#連携
  - TCP
---

# 第 61 章 TCP 編の実装：エディタに組み込む

第 60 章で、エンジンと、エディタ側のクライアントを、TCP で繋ぐ最小の構成ができました。この章では、それを、<strong>実際のエディタの構造に組み込みます</strong>。エンジンのプロセスを起動して、見張って、固まったら見つけて、閉じるときに行儀よく閉じる。同じ PC の他のプログラムから、守る。そして、偽のエンジンでテストする。この章は、その部分を扱います。

この章のコードは、第 53〜57 章（名前付きパイプ版のエディタ）の `EngineProcess`、`EngineSupervisor` を、TCP 版に直す形で書いてあります。その章を読んでいなくても、この章の文章と、第 60 章のコードで、意味は追えます。第 53〜57 章を読んでいる場合は、<strong>直す箇所</strong>の対応を、書いておきます。

!!! info "このページを読む前に"
    - [第 60 章 TCP 編の土台：最小のエンジンとエディタを繋ぐ](60-tcp-base.md)（前の章。`EngineClient`、`TcpTransport`、サーバー）
    - [第 59 章 TCP を深く知る：バイトの流れとして使うために](59-tcp-deep.md)（TCP の性質。ハートビートや閉じ方の根拠）
    - [第 55 章 エンジンをサーバーにする：EngineHost](55-engine-host.md)、[第 57 章 落ちたら立て直す](57-recovery.md)（任意。`EngineProcess` と `EngineSupervisor` の元のコード）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）

!!! abstract "この章で足す・直すもの"
    - `Editor/Engine/PipeTransport.cs`（新規）：名前付きパイプ版の窓口。両方を残す場合に使う
    - `Editor/Engine/EngineProcess.cs`（変更）：標準入力で合言葉を渡し、標準出力でポート番号を受け取る
    - `Editor/Engine/Heartbeat.cs`（新規）：固まったエンジンを見つける
    - `Editor.Tests/SlowTcpEngine.cs`（新規）：細切れに返事を書く、偽のエンジン

## パイプ版も残す

第 60 章の `EngineClient` は、`IEngineTransport` の窓口で `Stream` を受け取ります。名前付きパイプ版を残したいときは、パイプを繋ぐ窓口を、もう 1 つ書くだけです。

パイプ版は、`NamedPipeClientStream` の `ConnectAsync` を、そのまま包みます。

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

通信の不具合が出たとき、通信路を替えて、原因を切り分けられます。起動の引数で、`PipeTransport` と `TcpTransport` のどちらを使うかを、選ぶ作りにしておくと便利です。

## 起動：合言葉は標準入力、ポートは標準出力

エンジンのプロセスを起動して、待ち受けのポートが分かるまで待つ部分です。第 60 章の `Program.cs` に書いた起動の処理（数行）を、失敗にも強い形にします。第 55 章の `EngineProcess.StartAsync` を読んでいる場合は、その中の、起動の引数と、接続を待つ部分の置き換えです。ジョブ オブジェクトの部分は、そのままです。

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

正常なら 56 ミリ秒でポートが分かりました。起動してすぐ終わる場合は 56 ミリ秒で、終了コードつきの例外になります。何も出力しない場合は指定した 1 秒で時間切れになります。「5 秒待たされたあとの時間切れ」ではなく、「すぐ分かる、理由つきの失敗」にするという設計が、そのまま働いています。

エンジンを見張って、落ちたら立て直す役目（第 57 章の `EngineSupervisor`）を作る場合は、変更は少しです。パイプの名前に付けていた世代番号は、要らなくなります。ポートは毎回、OS が新しく選ぶので古いエンジンが残っていても、衝突しません。`LaunchAsync` は `StartAsync(exePath, "", timeout)` を呼んで `StartedEngine` から `new EngineClient(new TcpTransport(started.Port, started.Token))` を作り `ConnectAsync` します。

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

エンジンのプロセスがなくても、`EngineClient` をテストできます。通信の向こうに、偽のエンジンを置きます。TCP なら、偽のエンジンを、テスト プロセスの中に作れます。ポートは 0 なので並行して動かしても、衝突しません。

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
    確かめたもの：C++ の `TcpServer.cpp` は、MSVC で `/W4 /utf-8 /std:c++latest` のコンパイルが通った。C# の `EngineClient`、`PipeTransport`、`TcpTransport`、`TcpStream`、`Framing`、`Heartbeat`、起動の `StartAsync`（ジョブ オブジェクトを除く）は、.NET 10 でコンパイルして、第 60 章の `TcpServer.exe` と実際に繋いで動かした。合言葉の違い 1 バイトずつ届く返事、プロセスの `Kill`、`NtSuspendProcess` による固まり行儀のよい終了、起動の 3 通りの失敗、パイプ版の差し替えも動かして確かめた。
    確かめていないもの：ジョブ オブジェクトと、`EngineSupervisor`（第 55・57 章）への組み込みは、この章の形で動かしていない（差分の説明だけ）。本物のエンジンの命令処理と繋いでいない。`TcpKeepAliveTime` などの設定は設定が通ることまでしか確かめていない（固まりに効かないという説明は、TCP の仕組みからの推論）。デバッガーでエンジンを止めたときの挙動は、試していない。

## 参考資料

- W. Eddy (Ed.), *Transmission Control Protocol (TCP)*, RFC 9293, 2022 年 8 月。keep-alive（§3.8.4）、半閉じ（§3.6）。読んだ範囲は第 59 章の「参考資料」に書いた。
- Microsoft Learn「Use TcpClient and TcpListener」（.NET）。`TcpListener.Start`、`AcceptSocketAsync`、`NetworkStream` の所有権。
- Microsoft Learn「SOL_SOCKET Socket Options」（Win32）。`SO_EXCLUSIVEADDRUSE`、`SO_RCVTIMEO`、`SO_KEEPALIVE`。
- Microsoft Learn「Graceful Shutdown, Linger Options, and Socket Closure」（Win32）。`shutdown` と `closesocket` の使い分け。
- Microsoft Learn「Getting started with Winsock」（Win32）。`WSAStartup` を RAII で守ることと `getaddrinfo` の勧め。

読んでいないもの：Winsock の非同期 I/O（IOCP、`WSAPoll`）の資料。この章のサーバーはブロッキングの `recv` と `send` で、1 人のエディタを相手にする作りです。複数の接続を同時に扱う本格的なサーバーには、別の作りが必要です。

## 関連ページ

- [第 60 章 TCP 編の土台：最小のエンジンとエディタを繋ぐ](60-tcp-base.md)
- [第 59 章 TCP を深く知る：バイトの流れとして使うために](59-tcp-deep.md)
- [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)
- [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)
- [第 55 章 エンジンをサーバーにする：EngineHost](55-engine-host.md)
- [第 57 章 落ちたら立て直す](57-recovery.md)
- [第 58 章 AI から操作する：MCP](58-mcp.md)

次は、この部のまとめです。[第 62 章 まとめとこれから](62-next-steps.md) へ進みます。

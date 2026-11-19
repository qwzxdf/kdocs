---
title: 第 61 章 TCP 編 3：安全で壊れにくくする
tags:
  - C#連携
  - TCP
---

# 第 61 章 TCP 編 3：安全で壊れにくくする

第 59 章の最小の構成は、手元では最後まで動きました。ただし、そのまま使い続けるには、いくつか弱い所があります。この章は、<strong>動いているものを、少しずつ丈夫にしていく</strong>章です。1 つ直すたびに、何を守ったのかを、実際に壊して確かめます。

最小の構成の弱点は、次の 5 つです。

- エディタが接続を閉じるとき、ただ捨てているだけで、相手が受け取り終えたかを確かめていない
- 同じ PC の他のプログラムが、エンジンのポートに繋いで、命令を送れる
- Web ページを開いただけで、ブラウザーがエンジンのポートに何かを送ってくる可能性がある
- エンジンが固まっても（プロセスは生きているので）、エディタが気づけない
- エンジンのプロセスがないと、`EngineClient` を試せない

この章で、順に直します。直したあとの形が、実際にエディタに入れる形です。

!!! info "このページを読む前に"
    - [第 59 章 TCP 編 1：最小のエンジンとエディタを繋ぐ](59-tcp-base.md)（この章で直す、最小の構成）
    - [第 60 章 TCP 編 2：Prest のエディタに組み込む](60-tcp-editor.md)（`EngineProcess` と `RemoteEngineService`）
    - [第 62 章 TCP を深く知る](62-tcp-deep.md)（任意。`FIN`、`RST`、Nagle などの仕組みの詳細）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）

!!! abstract "この章で足す・直すもの"
    - `Editor/Engine/TcpStream.cs`（新規）：送信側だけを閉じられる `Stream`
    - `Editor/Engine/EngineClient.cs`（変更）：`CloseGracefullyAsync` を足す
    - `EngineHost/TcpServer.cpp`（変更）：握手、`SO_EXCLUSIVEADDRUSE`、行儀のよい閉じ方
    - `Editor/Engine/TcpTransport.cs`（変更）：合言葉を送る握手
    - `Editor/Engine/EngineProcess.cs`（変更）：合言葉を作って、標準入力で渡す
    - `Editor/Engine/Heartbeat.cs`（新規）：固まったエンジンを見つける
    - `Editor.Tests/SlowTcpEngine.cs`（新規）：細切れに返事を書く、偽のエンジン

## 行儀のよい閉じ方

第 59 章の `EngineClient` は、閉じるときに `DisposeAsync` でストリームを捨てるだけでした。それでもエンジンは、読み取りが終わって終了コード 0 で終わりました。小さなやり取りが終わっているときは、それで足ります。

ただし、まだ相手が読み終えていないデータが残っているときに接続を捨てると、OS が相手に `RST`（接続のリセット）を送ることがあります。受け取った側は、読み取り中のデータを失って、`ConnectionReset` で失敗します。確実に閉じるには、<strong>送信側を先に閉じて（`FIN`）、相手が閉じるのを待ってから、最後に捨てる</strong>作りにします。

C# 側から作ります。まず、送信側だけを閉じられる `Stream` です。

```csharp title="Editor/Engine/TcpStream.cs（新規）"
using System.Net.Sockets;

namespace Editor.Engine;

// 送信側だけを閉じられる Stream（TCP の FIN）
public interface IHalfCloseable
{
    void ShutdownSend();
}

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

`NetworkStream` には、`Socket` を `protected` で公開するプロパティがあるので、派生クラスの中から `Shutdown` を呼べます。`ownsSocket: true` なので、`Stream` を `Dispose` すれば、ソケットも閉じます。`Shutdown(SocketShutdown.Send)` が、`FIN` を送る呼び出しです。送信側だけを閉じて、受信側は開いたままなので、相手の残りのデータを読めます（半閉じ）。

次に、`EngineClient` に閉じ方を足します。第 59 章の `DisposeAsync` の手前に置きます。

```csharp title="Editor/Engine/EngineClient.cs（続き：閉じ方を足す）"
    // 行儀のよい閉じ方: 送信側を閉じて（FIN）、相手が閉じるのを待つ。待ち切れなければ強制的に閉じる
    public async Task CloseGracefullyAsync(TimeSpan wait)
    {
        _closing = true;
        if (_stream is IHalfCloseable half) half.ShutdownSend();
        if (_readLoop is not null) await Task.WhenAny(_readLoop, Task.Delay(wait)).ConfigureAwait(false);
        await DisposeAsync().ConfigureAwait(false);
    }
```

`ShutdownSend` で `FIN` を送ると、エンジンの側が読み終えて、自分も閉じます。こちらの読み取りのループが EOF（相手が閉じた印）で終わるのを、`wait` を上限に待ちます。相手が応答しなくても、`wait` を過ぎれば、強制的に `DisposeAsync` します。`_closing` を先に立てるのは、この閉じ方のあとの切断を、「エンジンが落ちた」と受け取らないためです。

C++ 側は、`shutdown` と `closesocket` の間に、相手が閉じるのを待つ処理を足します。

```cpp title="EngineHost/TcpServer.cpp（続き：閉じ方）"
// ---- 閉じ方: 自分の送信側を閉じて（FIN）、相手が閉じるまで読み捨ててから closesocket ----
void CloseGracefully(SOCKET s) {
  shutdown(s, SD_SEND);
  const DWORD timeout_ms = 1000;  // 相手が閉じてくれなくても、1 秒で諦める
  setsockopt(s, SOL_SOCKET, SO_RCVTIMEO,
             reinterpret_cast<const char*>(&timeout_ms), sizeof(timeout_ms));
  char sink[256];
  while (recv(s, sink, sizeof(sink), 0) > 0) {}  // 0（相手の FIN）か、エラー（時間切れ）で終わる
}
```

`shutdown(s, SD_SEND)` で `FIN` を送ってから、相手の `FIN` が来る（`recv` が 0）まで読み捨てます。これをせずに `closesocket` すると、未読のデータが残っていた場合に、相手へ `RST` が飛ぶことがあります。相手が閉じてくれなくても、1 秒で諦めます。`SO_RCVTIMEO` はブロッキングの `recv` の時間切れで、時間切れになった `recv` のあと、その接続は「不定の状態」になるので、閉じるのが決まりです（Microsoft Learn）。この関数は、次の節の `ServeOnce` から呼びます。

流れは次のとおりです。

1. エディタが `CloseGracefullyAsync` を呼ぶ。`_closing` を立てて、`ShutdownSend` で `FIN` を送る。
2. エンジンの `ReadMessage` が `false` を返す。`CloseGracefully` で、自分も `FIN` を送って、相手の閉じるのを待つ。
3. エディタの読み取りのループが、EOF で終わる。
4. 両側が閉じる。エンジンの `ServeOnce` が `true` を返して、`main` が終了コード 0 で終わる。

手元で動かした結果です。

```text title="CloseGracefullyAsync（実測）"
[C] 行儀よく閉じる: 2 ms, エンジンの終了=True, 終了コード=0, Disconnected 通知=False
```

2 ミリ秒で閉じて、エンジンは終了コード 0 で終わりました。`Disconnected` は飛んでいません。つまり、エンジンを見張って立て直す仕組み（第 57 章）が「落ちた」と誤解して、再起動を始めることもありません。

エンジンが固まっていて、2 が進まないときは、`CloseGracefullyAsync` の待ちが `wait` で切れて、強制的に閉じます。そのあと、エンジンのプロセスは、第 60 章の `RemoteEngineService.Dispose` が強制終了します。

## 合言葉で、他のプログラムを締め出す

localhost のポートは、<strong>同じ PC のどのプログラムからも繋げます</strong>。名前付きパイプのように、アクセス制御（ACL）で相手を絞ることは、ソケットでは手軽にできません。そこで、3 つの守りを重ねます。

1. `127.0.0.1` だけで待ち受ける（外の PC からは繋げない）。これは第 59 章で済んでいます
2. ポートを横取りされないようにする（`SO_EXCLUSIVEADDRUSE`）
3. 合言葉。最初の 1 通が合言葉でない相手は、切る

合言葉が要る理由は、他のプログラムが、うっかり、あるいは悪意で、このポートに何かを送ってくることがあるからです。特に、<strong>Web ブラウザー</strong>は要注意です。ブラウザー上の Web ページは、`http://127.0.0.1:ポート番号/` に対して、リクエストを送れます。ページを開いただけで、エンジンのポートに勝手に命令が届く可能性があります（この章では、ブラウザーからの送信は試していません。あとの実験は、プログラムから HTTP を送ったものです）。

### 合言葉を作って、渡す

合言葉は、エディタがエンジンを起動するたびに作る乱数にして、標準入力で渡します。第 60 章の `EngineProcess` に、次のとおり足します。

```csharp title="Editor/Engine/EngineProcess.cs（変更：合言葉を足す）"
using System.Security.Cryptography;

public sealed record StartedEngine(Process Process, int Port, string Token);   // Token を足す

// StartAsync の先頭
        // 起動のたびに作る合言葉（128 ビットの乱数を、16 進の 32 文字にしたもの）
        string token = Convert.ToHexString(RandomNumberGenerator.GetBytes(16));

        var info = new ProcessStartInfo(exePath, arguments)
        {
            UseShellExecute = false,
            CreateNoWindow = true,
            RedirectStandardInput = true,     // 合言葉を渡す（足した行）
            RedirectStandardOutput = true,
            RedirectStandardError = true,
        };

// try の先頭（プロセスを起動したあと）
            await process.StandardInput.WriteLineAsync(token).ConfigureAwait(false);
            await process.StandardInput.FlushAsync().ConfigureAwait(false);

// 成功したときの return
                return new StartedEngine(process, port, token);
```

`RandomNumberGenerator.GetBytes(16)` は、暗号用の乱数を 16 バイト（128 ビット）作ります。`Random` は使いません。`Random` は暗号用ではなく、値の推測しにくさが保証されていないからです。合言葉は起動のたびに変わるので、前回の合言葉が漏れても、今回のエンジンには使えません。

合言葉をコマンド ライン引数（`ProcessStartInfo` の `Arguments`）には載せません。コマンド ライン引数は、同じ PC の他のプログラムが、プロセスの一覧から読める場合があります。標準入力なら、エンジンとエディタの間だけに留まります。

### エンジン側：握手と、ポートの横取り防止

C++ 側に、3 つの変更を入れます。

1 つめは、`ListenLoopback` で `bind` の前に `SO_EXCLUSIVEADDRUSE` を設定する 4 行です。他のプログラムが、同じアドレスとポートに割り込んで `bind` できなくなります。

```cpp title="EngineHost/TcpServer.cpp（変更：ListenLoopback の、sockaddr_in の前に足す）"
  // 他のプログラムが、同じポートに割り込んで bind できないようにする（bind より前に設定）
  const BOOL exclusive = TRUE;
  setsockopt(s.get(), SOL_SOCKET, SO_EXCLUSIVEADDRUSE,
             reinterpret_cast<const char*>(&exclusive), sizeof(exclusive));
```

2 つめは、握手です。最初の 1 通が合言葉と合えば `ok` を返します。

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

`SO_RCVTIMEO` は、ブロッキングの `recv` の時間切れ（ミリ秒）です。既定は 0（時間切れなし）です。握手では 3 秒だけ待って、それを超えたらその相手を切ります。握手のあとは、時間切れなしに戻します。エディタは、ユーザーが何もしなければ、何分も黙っているのが普通だからです。

3 つめは、`ServeOnce` です。合言葉を引数に取って、握手に失敗した相手は切って、次の相手を待つ作りにします。

```cpp title="EngineHost/TcpServer.cpp（変更：ServeOnce を、合言葉つきにする）"
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

`for (;;)` は、「合言葉が違う相手を切って、次を待つ」ためにあります。繋いできた相手が偽物でも、エンジンは終わらず、本物のエディタを待ち続けます。これがないと、同じ PC の他のプログラムが 1 回繋ぐだけで、エンジンが終了してしまいます。最後は、前の節の `CloseGracefully` で閉じます。

`main` は、合言葉を標準入力から読んで、`ServeOnce` に渡します。

```cpp title="EngineHost/TcpServer.cpp（変更：main）"
int main() {
  // 合言葉は、コマンド ライン引数ではなく標準入力の 1 行目で受け取る
  std::string token;
  std::getline(std::cin, token);
  if (!token.empty() && token.back() == '\r') token.pop_back();

  WinsockSession wsa;
  if (!wsa.ok()) return 1;
  return ServeOnce(token, Dispatch) ? 0 : 2;    // 2 = 待ち受けを始められなかった
}
```

`std::cin` を使うので、`#include <iostream>` も足してください。

### エディタ側：握手を送る

`TcpTransport` は、接続したあとに合言葉を送って、`ok` が返るのを待ちます。コンストラクターに `token` を足して、返す `Stream` を `TcpStream` に替えます。

```csharp title="Editor/Engine/TcpTransport.cs（変更：握手を足す）"
using System.Text;

public sealed class TcpTransport(int port, string token) : IEngineTransport   // token を足す
{
    // ... ConnectAsync の接続の部分までは、第 59 章と同じ ...

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

サーバーは、合言葉が違うと、返事をせずに接続を切ります。エディタの側では、`ReadFrameAsync` が `EndOfStreamException` か `IOException`（`ConnectionReset`）で終わるので、`InvalidDataException` に包んで、原因の分かる文面にします。何も返事をしない理由は、攻撃者に情報を与えないためです。ただ、エディタの開発者にとっては、「切られた」だけでは原因が分かりにくいので、エディタの側が文面を補います。

呼び出し側は、`StartedEngine` から合言葉を取って、`new TcpTransport(started.Port, started.Token)` とします。第 60 章の `RemoteEngineService` の `Initialize` の、1 行だけの変更です。

### 他のプログラムが繋いできたら

実際に、守りが働くかを確かめます。違う合言葉で繋ぐと、握手に失敗して、エンジンは生きたままです。そのあとに、本物のエディタが繋ぐと、握手が通ります。

```text title="違う合言葉と、HTTP を送り付けられたとき（実測）"
[B] 違う合言葉: InvalidDataException
[B] エンジンは生きている: True
[D] HTTP を送ると -> IOException
[D] そのあとも、エンジンは生きている: True
[D] 本物は繋がる: pong
[D] 終了コード 0
```

HTTP の先頭 4 バイト `GET ` を長さとして読むと、`0x20544547`、つまり 542,393,671 バイトです。16 MiB を大きく超えているので、サーバーは「壊れた長さ」として握手を打ち切り、接続を切ります（その結果、送った側には `IOException` が見えました）。エンジンはそのあとも生きていて、本物のエディタは問題なく繋がります。

ただし、これはメッセージの形が HTTP と違うことによる、偶然に近い守りです。合言葉まで知っている相手なら通ります。合言葉は、<strong>推測できない値</strong>にして、標準入力で渡すことではじめて意味を持ちます。

守れないものも、はっきりさせておきます。同じユーザーで動いている悪意のあるプログラムは、このやり方では防げません（そのプログラムは、エディタのメモリを読むことも、エンジンのプロセスを操作することもできると考えられます。これは筆者の見立てです）。この章の合言葉は、<strong>うっかり繋いできた無関係のプログラムと、ブラウザー経由の攻撃</strong>を防ぐためのものです。

この守りには、既知の限界が 1 つあります。サーバーは 1 人ずつ順に処理するので、繋いだだけで黙る相手が先にいると、本物のエディタの握手が、握手の時間切れ（3 秒）の後ろに並びます。手元で測ると、本物の握手が完了するまで 3013 ミリ秒でした。同じ PC の他のプログラムが、悪意で同じことを繰り返すと、エンジンの起動が 3 秒ずつ遅れます（サービスの妨害）。実運用に近づけるなら、握手を別のスレッドで並行して受ける作りにします。この章ではそこまで作りません。

## 固まりを見つける：ハートビート

第 62 章で、プロセスの死と固まりは別物だと見ました。死んだときは TCP が切断を知らせます。手元で `Kill` したところ `EngineClient.Disconnected` が、1 ミリ秒後に飛びました。

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


## パイプ版も残す

第 59 章の `EngineClient` は、`IEngineTransport` の窓口で `Stream` を受け取るだけです。名前付きパイプ版を残したいときは、パイプを繋ぐ窓口を、もう 1 つ書くだけで済みます。パイプ版は、`NamedPipeClientStream` の `ConnectAsync` を、そのまま包みます。

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

通信の不具合が出たとき、通信路を替えて、原因を切り分けられます。起動の引数で、`PipeTransport` と `TcpTransport` のどちらを使うかを選ぶ作りにしておくと便利です。パイプを使う側のエンジンの作り方は、第 55 章にあります。

## 偽のエンジンでテストする

エンジンのプロセスがなくても、`EngineClient` をテストできます。通信の向こうに、偽のエンジンを置きます。TCP なら、偽のエンジンを、テスト プロセスの中に作れます。ポートは 0 なので並行して動かしても、衝突しません。

次の偽のエンジンは返事をわざと 1 バイトずつ書きます。第 59 章で見たとおり、TCP はメッセージの切れ目を保証しません（詳しくは第 62 章）。細切れの届き方でも `EngineClient` が組み立てられるかを確かめるためです。

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

この章と、前の 2 章のコードを実際に動かして確かめた結果をまとめます（Windows 11、.NET 10、MSVC。値は 1 台の PC の結果）。

起動と接続：

- エンジンの起動からポートが分かるまで：約 50 ミリ秒
- 接続と握手：約 11 ミリ秒
- `EngineClient` の `RequestAsync` を直列に 5000 回呼んだ、1 往復の平均：約 55 マイクロ秒（JSON の組み立てと返事の読み取りを含む）
- 200 件の要求を同時に送って、全部の返事が返るまで：約 8 ミリ秒（`id` で、取り違えなく対応づけられた）

切断：

- `Kill` から `Disconnected` まで：約 1 ミリ秒
- `NtSuspendProcess` で固めてからハートビート（間隔 500 ミリ秒、3 回連続）が判定するまで：約 1.8 秒。その間、TCP は `ESTABLISHED` のまま
- `CloseGracefullyAsync`：数ミリ秒（手元の測定で 2〜5 ミリ秒）。エンジンは終了コード 0 で終わり、`Disconnected` は飛ばない

守り：

- 違う合言葉：`InvalidDataException`。エンジンは生きたままでそのあとの本物の接続は通る
- 繋いだだけで黙る相手：本物の握手が、約 3 秒待たされる（既知の限界）
- HTTP のリクエスト：切られる。エンジンは生きたまま

パイプの 1 往復（`EngineClient` 経由）はこの章では測り直していません。第 62 章の生のソケットの比較（パイプ 27.8 マイクロ秒、TCP 25.2 マイクロ秒）が、手元の目安です。


## よくあるミス

??? failure "合言葉をコマンド ライン引数に載せる"
    何が起きるか：同じ PC の他のプログラムが、プロセスの一覧から合言葉を読める場合があります。

    対処：標準入力で渡します。

??? failure "自分から閉じたのに、Disconnected が飛んで、エンジンが再起動される"
    何が起きるか：エディタを閉じる途中で、`EngineSupervisor` が「落ちた」と判断して新しいエンジンを起動してしまいます。

    対処：自分から閉じるときは `_closing` を立てて `Disconnected` を飛ばさないようにします。

??? failure "デバッガーでエンジンを止めたら、エンジンが強制終了された"
    何が起きるか：ブレークポイントで止まったエンジンは、固まった状態と同じです。ハートビートが死んだと判定します。

    対処：デバッグ中はハートビートを止める起動の引数を用意します。

## これだけ覚える

- 閉じるときは、送信側を閉じて（`FIN`）、相手が閉じるのを待ってから `closesocket`。
- 合言葉は毎回違う乱数にして、標準入力で渡す。違う相手は切って、本物を待ち続ける。
- ポートの横取りは、`SO_EXCLUSIVEADDRUSE` で防ぐ。
- プロセスの死は、TCP が教える。固まりは、ハートビートで見つける。
- 偽のエンジン（細切れに返事を書く）で、エンジンなしに `EngineClient` をテストできる。

## 確かめたもの、確かめていないもの

!!! note "確かめたもの、確かめていないもの"
    確かめたもの：C++ の `TcpServer.cpp`（握手、`SO_EXCLUSIVEADDRUSE`、行儀のよい閉じ方を足した版）は、MSVC で `/W4 /utf-8 /std:c++latest` のコンパイルが通った。C# の `EngineClient`、`TcpTransport`、`TcpStream`、`Framing`、`EngineProcess`（合言葉つき）は、.NET 10 でコンパイルして、その `TcpServer.exe` と実際に繋いで動かした。違う合言葉、HTTP の送り付け、行儀のよい閉じ方は、この版で動かして確かめた。`Heartbeat`、細切れに届く返事、パイプ版の差し替え、`Kill` と `NtSuspendProcess` の実験は、前に同じ形のコードで動かして確かめたもので、この章で組み直した版では動かし直していない。
    確かめていないもの：ジョブ オブジェクトと、`EngineSupervisor`（第 55・57 章）への組み込みは、この章の形で動かしていない（差分の説明だけ）。本物のエンジンの命令処理と繋いでいない。`TcpKeepAliveTime` などの設定は、設定が通ることまでしか確かめていない（固まりに効かないという説明は、TCP の仕組みからの推論）。デバッガーでエンジンを止めたときの挙動は、試していない。

## 参考資料

- W. Eddy (Ed.), *Transmission Control Protocol (TCP)*, RFC 9293, 2022 年 8 月。keep-alive（§3.8.4）、半閉じ（§3.6）。読んだ範囲は第 62 章の「参考資料」に書いた。
- Microsoft Learn「Use TcpClient and TcpListener」（.NET）。`TcpListener.Start`、`AcceptSocketAsync`、`NetworkStream` の所有権。
- Microsoft Learn「SOL_SOCKET Socket Options」（Win32）。`SO_EXCLUSIVEADDRUSE`、`SO_RCVTIMEO`、`SO_KEEPALIVE`。
- Microsoft Learn「Graceful Shutdown, Linger Options, and Socket Closure」（Win32）。`shutdown` と `closesocket` の使い分け。
- Microsoft Learn「Getting started with Winsock」（Win32）。`WSAStartup` を RAII で守ることと `getaddrinfo` の勧め。

読んでいないもの：Winsock の非同期 I/O（IOCP、`WSAPoll`）の資料。この章のサーバーはブロッキングの `recv` と `send` で、1 人のエディタを相手にする作りです。複数の接続を同時に扱う本格的なサーバーには、別の作りが必要です。


## 関連ページ

- [第 59 章 TCP 編 1：最小のエンジンとエディタを繋ぐ](59-tcp-base.md)
- [第 60 章 TCP 編 2：Prest のエディタに組み込む](60-tcp-editor.md)
- [第 62 章 TCP を深く知る：バイトの流れとして使うために](62-tcp-deep.md)（`FIN`、`RST`、Nagle、ウィンドウなどの仕組み）
- [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)
- [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)
- [第 55 章 エンジンをサーバーにする：EngineHost](55-engine-host.md)
- [第 57 章 落ちたら立て直す](57-recovery.md)
- [第 58 章 AI から操作する：MCP](58-mcp.md)

次は、この部のまとめです。[第 63 章 まとめとこれから](63-next-steps.md) へ進みます。

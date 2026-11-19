---
title: 第 62 章 TCP を深く知る：バイトの流れとして使うために
tags:
  - C#連携
  - TCP
---

# 第 62 章 TCP を深く知る：バイトの流れとして使うために

第 53 章では TCP を「`127.0.0.1` のポートで待ち受けて、ソケットでやり取りする」の数行で紹介しました。ところが、実際に TCP でエンジンとエディタを繋ぐとパイプのときには出なかった困りごとが出てきます。`Read` を呼んだのに欲しい分だけ返ってこない。`Write` が戻ってこない。相手を `Kill` したのに気づくのが遅れる。ポートが使用中だと言われる。エンジンが起動していないだけなのに、接続の失敗がなぜか 2 秒かかる。

どれも TCP がどういう約束をして、どういう仕組みでそれを守っているかを知れば、理由が説明できます。この章はその仕組みを順に見ていきます。この章は、先に読み通す章ではありません。第 59 章から第 61 章で、エンジンとの接続を作り進めながら、「なぜそう書くのか」を知りたくなったときや、動かして困ったときに、必要な節を引いてください。それぞれの章で出てきた TCP の話は、すべてここに詳しく書いてあります。

この章の前提は同じ PC の中（`127.0.0.1`）で使うことです。ループバックの TCP も本物の TCP として動きます。ヘッダーも確認応答もウィンドウも状態遷移もネットワークの向こう側と同じです。ただし、ネットワーク機器を通らないので、途中でパケットが消える順番が入れ替わるといったことは起きにくいはずです（この章では、それを観測してはいません。以下は筆者の推測です）。だからこの章は再送や輻輳制御を軽く、ストリームの性質・バッファ・ウィンドウ・切断・ポートを重く扱います。ゲームのエンジンとエディタの通信で、実際に問題になるのはこちらだからです。

!!! info "このページを読む前に"
    - [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)（通信路の比較と、長さ付きのメッセージの形）
    - [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)（`EngineClient` と、返事を待つ仕組み）
    - [第 59 章 TCP 編 1：最小のエンジンとエディタを繋ぐ](59-tcp-base.md)（任意。この章の話が、どこで必要になるかが分かる）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）


## 確かめた環境と、数字の読み方

この章の数字は次の環境で測りました。ほかの PC では値が変わります。傾向（何が何倍か、何が起きるか）を読んでください。

- Windows 11 Pro（10.0.26300）、.NET 10.0.402、Visual Studio 2026（MSVC、`/std:c++latest`）
- 実験はすべて `127.0.0.1` の上
- 実験のコードはこの章に載せたものをそのまま動かして確かめた

動かして確かめた値には「実測」と付けます。RFC や Microsoft Learn に書いてあることは、出典を書きます。どちらでもない説明（筆者の推測）はそう書きます。


## TCP が約束すること、約束しないこと

TCP（Transmission Control Protocol）が約束するのは、次の 4 つです。

1. 送ったバイトは順番どおりに届く。
2. 途中で欠けたり重複したりしない（欠けたら、TCP が自分で再送する）。
3. 受け取る側が追いつかないときは、送る側を待たせる（フロー制御）。
4. ネットワークが混んだときは送る量を減らす（輻輳制御）。

約束しないこともはっきりさせておきます。ここを取り違えるとバグになります。

メッセージの切れ目は約束しません。TCP が運ぶのはバイトの流れだけです。10 バイトを 4 回 `Write` しても、相手が 40 バイトを 1 回で読むかもしれません。次の節で実測します。

遅延の上限も約束しません。再送が起きればその分遅れます。

相手が生きていることも約束しません。相手のプロセスが固まっているだけなら TCP の接続は何事もなく繋がったままです。

そして、`Write` が成功したことは相手が受け取ったことを意味しません。`Write` が戻るのは OS のバッファにバイトが入った時点です。相手のアプリが読んだかどうかはもちろん相手の PC に届いたかどうかもまだ分かりません。後でこれを実測で見ます。


## バイトの流れ：Read が返す量は決まらない

最初の実験用にサーバーとクライアントを 1 組作る小さな関数を用意します。以降の実験でも使います。

```csharp title="実験の土台（Program.cs の先頭）"
using System.Diagnostics;
using System.Net;
using System.Net.Sockets;

// 127.0.0.1 で待ち受けて、1 本繋いだ組（クライアント, サーバー側の相手）を返す
static (TcpClient c, TcpClient s) Pair(out TcpListener l)
{
    l = new TcpListener(IPAddress.Loopback, 0);   // ポート 0 = 空いているポートを OS が選ぶ
    l.Start();
    var c = new TcpClient();
    var port = ((IPEndPoint)l.LocalEndpoint).Port;
    var t = l.AcceptTcpClientAsync();
    c.Connect(IPAddress.Loopback, port);
    return (c, t.Result);
}
```

`TcpListener` の第 2 引数が `0` なのは、ポート番号を OS に選ばせる指定です。選ばれた番号は `LocalEndpoint` から読めます。固定のポートを使うと前回の実行が残っていたときに衝突します（後の「ポートとアドレス」の節）。

### 1 回の Write は、1 回の Read にならない

1 MB を 1 回で `Write` して、受け取る側が何回の `Read` で受け取るかを数えます。

```csharp title="1 MB を 1 回 Write して、Read の回数と大きさを数える"
{
    var (c, s) = Pair(out var l);
    var data = new byte[1_000_000];
    var w = Task.Run(() => { s.GetStream().Write(data); s.GetStream().Flush(); });
    var sizes = new List<int>(); int total = 0; var buf = new byte[65536];
    var ns = c.GetStream();
    while (total < data.Length) { int n = ns.Read(buf); sizes.Add(n); total += n; }
    Console.WriteLine($"[1] 1MB を 1 回 Write -> Read {sizes.Count} 回, 先頭10回: {string.Join(",", sizes.Take(10))}, 最小 {sizes.Min()}, 最大 {sizes.Max()}");
    c.Dispose(); s.Dispose(); l.Stop();
}
```

```text title="実行結果（実測）"
[1] 1MB を 1 回 Write -> Read 16 回, 先頭10回: 65536,65536,65536,65536,65536,65075,65536,65536,65413,65536, 最小 17667, 最大 65536
```

1 回の `Write` が 16 回の `Read` に分かれました。受け取り用の配列を 65536 バイトにしたので、`Read` は最大でもその分しか返せません。しかし、65536 に満たない回（65075、65413、最小は 17667）もあります。`Read` は「その時点で受信バッファにあるバイト」を返すだけで、あと何バイト来るのかを知りません。

逆の例も見ます。10 バイトを 4 回に分けて書きます。

```csharp title="10 バイトを 4 回 Write して、100ms 後に 1 回 Read する"
{
    var (c, s) = Pair(out var l);
    var ws = s.GetStream(); s.NoDelay = true;
    for (int i = 0; i < 4; i++) ws.Write(new byte[10]);
    Thread.Sleep(100);
    var buf = new byte[1000]; int n = c.GetStream().Read(buf);
    Console.WriteLine($"[1b] 10 バイトを 4 回 Write -> 100ms 後の 1 回の Read: {n} バイト");
    c.Dispose(); s.Dispose(); l.Stop();
}
```

```text title="実行結果（実測）"
[1b] 10 バイトを 4 回 Write -> 100ms 後の 1 回の Read: 40 バイト
```

4 回の `Write` が 1 回の `Read` で 40 バイトとして出てきました。`NoDelay`（後で説明します）を付けて、書いた分をすぐ送り出させたうえでこの結果ですから、送る側の細工ではありません。受信バッファの中では 4 回分のバイトが、ただ並んでいるだけです。

ここから出る結論は 1 つです。メッセージの切れ目はアプリが自分で作るしかありません。第 53 章でメッセージの先頭に 4 バイトの長さを付けたのは、そのためです。そして、長さを読むときも本文を読むときも「欲しいバイト数が揃うまで読み続ける」必要があります。.NET の `ReadExactly`（C++ なら第 53 章の `ReadExact`）が、その役です。

1 バイトずつ届いても組み立てられることは、第 61 章のテストで確かめます。

### Write が戻るのは、バッファに入ったとき

`Write` が戻る条件も同じ考え方です。ここまでの `Write` はどれもすぐ戻りましたが、それは受信側がちゃんと読んでいたからです。読まない相手に書き続けるとどうなるかは、「フロー制御」の節で見ます。


## 接続の正体：4 つ組と、2 種類のソケット

TCP の接続は 4 つの値の組で区別されます。

- 自分の IP アドレス
- 自分のポート
- 相手の IP アドレス
- 相手のポート

同じ PC の中でもエディタがエンジンの `127.0.0.1:54941` に繋ぐとエディタ側には `127.0.0.1:54942` のような番号が自動で振られます。この自動の番号はエフェメラル ポートと呼ばれます。接続を作るたびに OS が空いている番号を選びます。同じサーバーのポートに 2 本繋いでもクライアント側のポートが違えば、4 つ組が違うので別の接続として区別されます。

実際に、`netstat -ano -p tcp` で見ます。

```text title="netstat -ano -p tcp の出力から、この接続だけを抜いたもの（実測）"
  TCP    127.0.0.1:54941        0.0.0.0:0              LISTENING       11392
  TCP    127.0.0.1:54941        127.0.0.1:54942        ESTABLISHED     11392
  TCP    127.0.0.1:54942        127.0.0.1:54941        ESTABLISHED     11392
```

3 行あります。1 行目は待ち受け（LISTENING）の行です。相手のアドレスが `0.0.0.0:0` なのは、まだ誰とも繋がっていないからです。2 行目と 3 行目が 1 本の接続を両側から見た 2 行です。ポートが入れ替わっていることに注目してください。2 行目は「サーバー側の端点から見た」接続（自分 54941、相手 54942）で 3 行目が「クライアント側の端点から見た」接続（自分 54942、相手 54941）です。

ここで大事なのは <strong>待ち受けのソケットと繋がったソケットは別物</strong>だということです。`TcpListener` は待ち受け専用です。`AcceptTcpClientAsync` を呼ぶたびに繋がった相手との専用のソケット（`TcpClient`）が新しく作られて返ってきます。サーバーが待ち受けのポート 54941 を持ち続けたまま繋がったソケットで、何本でも会話できるのはこのおかげです。

Microsoft Learn の説明も同じです。受け入れた接続は `TcpListener` が新しい `Socket` を作って返します（`AcceptSocketAsync` なら `Socket` を `AcceptTcpClientAsync` なら `TcpClient` を返します）。


## セグメントのヘッダー

TCP はバイトの流れをセグメントに区切って、IP のパケットに載せて運びます。セグメントの先頭には制御用のヘッダーが付きます。RFC 9293 の Figure 1 に沿って見ます。

<svg class="fig flow" viewBox="0 0 720 316" role="img" aria-label="TCP ヘッダー。送信元ポートと宛先ポート、シーケンス番号、確認応答番号、データ オフセットとフラグとウィンドウ、チェックサムと緊急ポインター、オプション、データの順に並ぶ"><text x="14" y="20" class="fig-title">TCP ヘッダー（1 目盛り = 1 ビット、横 32 ビット）</text><text x="40" y="38" style="font-size:11px">0</text><text x="352" y="38" text-anchor="middle" style="font-size:11px">16</text><text x="680" y="38" text-anchor="end" style="font-size:11px">31</text><rect x="40" y="44" width="320" height="34" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="200" y="61" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">送信元ポート（16）</text><rect x="360" y="44" width="320" height="34" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="520" y="61" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">宛先ポート（16）</text><rect x="40" y="78" width="640" height="34" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="360" y="95" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">シーケンス番号（32）：このセグメントの先頭バイトの番号</text><rect x="40" y="112" width="640" height="34" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="360" y="129" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">確認応答番号（32）：次に欲しいバイトの番号（ACK フラグが立つとき有効）</text><rect x="40" y="146" width="80" height="34" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="80" y="163" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">オフセット(4)</text><rect x="120" y="146" width="80" height="34" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="160" y="163" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">予約(4)</text><g fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"><rect x="200" y="146" width="20" height="34"/><rect x="220" y="146" width="20" height="34"/><rect x="240" y="146" width="20" height="34"/><rect x="260" y="146" width="20" height="34"/><rect x="280" y="146" width="20" height="34"/><rect x="300" y="146" width="20" height="34"/><rect x="320" y="146" width="20" height="34"/><rect x="340" y="146" width="20" height="34"/></g><g style="font-size:10px;font-weight:600" text-anchor="middle" dominant-baseline="central"><text x="210" y="163">C</text><text x="230" y="163">E</text><text x="250" y="163">U</text><text x="270" y="163">A</text><text x="290" y="163">P</text><text x="310" y="163">R</text><text x="330" y="163">S</text><text x="350" y="163">F</text></g><rect x="360" y="146" width="320" height="34" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="520" y="163" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">ウィンドウ（16）：あと何バイト受け取れるか</text><rect x="40" y="180" width="320" height="34" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="200" y="197" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">チェックサム（16）</text><rect x="360" y="180" width="320" height="34" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="520" y="197" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">緊急ポインター（16）</text><rect x="40" y="214" width="640" height="34" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6 4"/><text x="360" y="231" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">オプション（0〜40 バイト）：MSS、ウィンドウ スケールなど</text><rect x="40" y="248" width="640" height="34" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="2 4"/><text x="360" y="265" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">データ（ペイロード）</text><text x="40" y="304" style="font-size:12px">フラグは左から CWR、ECE、URG、ACK、PSH、RST、SYN、FIN。黄色は、この章で深く見るフィールド。</text></svg>

ヘッダーはオプションがなければ 20 バイトです。IPv4 のヘッダー（20 バイト）と合わせて、<strong>データが 1 バイトでも 40 バイトの付け足し</strong>が付きます。RFC 896 は 1 文字のキー入力が 41 バイトのパケットになることを、「約 4000 % のオーバーヘッド」と書いています。細かい `Write` を 1 つずつ別のセグメントにして送ると、無駄が大きいというのが後で出てくる Nagle アルゴリズムの動機です。

### ポート

16 ビットずつの送信元と宛先です。宛先ポートが「どのプログラムに渡すか」を決め、送信元ポートが「返事をどこに返すか」を決めます。範囲は 0〜65535 です。

### シーケンス番号と確認応答番号

TCP は流れのバイト 1 つ 1 つに番号を振ります。セグメントの番号ではなくバイトの番号です。シーケンス番号は「このセグメントの先頭のバイトの番号」で、確認応答番号は「ここまで受け取った。次はこの番号のバイトが欲しい」という意味です。

たとえば、番号 1000 から 500 バイトのセグメントを送って、無事届いたら相手は確認応答番号 1500 を返します。500 バイトのうちのどこが欠けても、番号が連続していないので受け取る側は気づけます。

番号の最初の値（ISN：初期シーケンス番号）は、0 ではなく接続のたびに違う値になります。RFC 9293 はクロックに基づく値を使うことを必須（MUST）とし、外から予測できない値にすることを求めています。古い接続のセグメントが遅れて届いて、新しい接続に紛れ込む事故を避けるためです。

番号は 32 ビットなので、2³² で一周して、0 に戻ります。比較はこの一周を考えて行います。

### フラグ

制御用の 1 ビットのスイッチです。この章に出てくるものを挙げます。

`SYN` は接続の開始を表します（番号の同期）。`ACK` は確認応答番号が有効なことを表します。接続が確立したあとはほぼすべてのセグメントに付きます。`FIN` は「もう送るデータはない」という通知です。`RST` は接続を即座に捨てる合図です（リセット）。`PSH` は受け取った側にすぐアプリへ渡すよう促します。`URG` と緊急ポインターは緊急データ用ですが、RFC 9293 は新しいアプリでは使わないよう求めています（SHOULD NOT）。

`CWR` と `ECE` はネットワークの混雑を知らせる ECN という仕組みの印です。この章では使いません。

### ウィンドウ

「あと何バイトなら受け取れるか」を受け取る側が送る側に教える値です。フロー制御の中心なので専用の節で詳しく扱います。16 ビットでは最大 65535 バイトしか表せないので、それより大きい値はオプションの「ウィンドウ スケール」を使って表します（RFC 7323）。

### チェックサム

ヘッダーとデータが壊れていないかの確認用です。送る側が計算し（MUST）、受ける側が検証します（MUST）。

### オプションと MSS

接続の開始時に `SYN` に付けて能力を教え合います。代表は MSS（Maximum Segment Size）で、「1 つのセグメントに載せられるデータの最大バイト数」です。オプションがなければ IPv4 では 536 バイトが既定です。RFC 9293 は通常の Ethernet では、MTU の 1500 から IP と TCP のヘッダー（各 20 バイト）を引いた 1460 が MSS になることを前提にしています。

ループバックでは MTU が大きいようです。手元の `netsh interface ipv4 show subinterfaces` ではループバックの MTU は `4294967295` と表示されました（実質、上限なしの扱いに見えます）。この章の実験で 5 MiB のメッセージを 14 ミリ秒で往復できた（後述）のも、小さなセグメントに刻まれずに済んでいるからだと考えられます。ただし、セグメントの大きさは測っていません。


## 接続の確立：3 回のやり取り

TCP はデータを送る前に 3 回のメッセージで接続を確立します。

<svg class="fig flow" viewBox="0 0 720 330" role="img" aria-label="3 ウェイ ハンドシェイク。クライアントが SYN を送り、サーバーが SYN と ACK を返し、クライアントが ACK を返して、両側が ESTABLISHED になる"><defs><marker id="tcA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">3 ウェイ ハンドシェイク</text><text x="110" y="52" text-anchor="middle" style="font-size:13px;font-weight:600">エディタ（connect）</text><text x="610" y="52" text-anchor="middle" style="font-size:13px;font-weight:600">エンジン（listen / accept）</text><line x1="110" y1="62" x2="110" y2="318" stroke="#94a3b8" stroke-width="2"/><line x1="610" y1="62" x2="610" y2="318" stroke="#94a3b8" stroke-width="2"/><rect x="14" y="68" width="92" height="22" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="60" y="80" text-anchor="middle" dominant-baseline="central" style="font-size:11px">CLOSED</text><rect x="614" y="68" width="92" height="22" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="660" y="80" text-anchor="middle" dominant-baseline="central" style="font-size:11px">LISTEN</text><line x1="110" y1="112" x2="610" y2="140" stroke="currentColor" stroke-width="2" marker-end="url(#tcA)"/><text x="360" y="112" text-anchor="middle" style="font-size:12px;font-weight:600">① SYN　seq = x</text><rect x="14" y="108" width="92" height="22" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="60" y="120" text-anchor="middle" dominant-baseline="central" style="font-size:11px">SYN-SENT</text><line x1="610" y1="178" x2="110" y2="206" stroke="currentColor" stroke-width="2" marker-end="url(#tcA)"/><text x="360" y="176" text-anchor="middle" style="font-size:12px;font-weight:600">② SYN + ACK　seq = y、ack = x + 1</text><rect x="614" y="164" width="92" height="22" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="660" y="176" text-anchor="middle" dominant-baseline="central" style="font-size:11px">SYN-RCVD</text><line x1="110" y1="242" x2="610" y2="270" stroke="currentColor" stroke-width="2" marker-end="url(#tcA)"/><text x="360" y="242" text-anchor="middle" style="font-size:12px;font-weight:600">③ ACK　ack = y + 1</text><rect x="14" y="228" width="92" height="22" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="60" y="240" text-anchor="middle" dominant-baseline="central" style="font-size:11px">ESTABLISHED</text><rect x="614" y="268" width="92" height="22" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="660" y="280" text-anchor="middle" dominant-baseline="central" style="font-size:11px">ESTABLISHED</text><text x="360" y="312" text-anchor="middle" style="font-size:12px">x と y は、それぞれが決めた初期シーケンス番号。SYN は、番号を 1 つ使う。</text></svg>

1. エディタの `connect` が `SYN` を送ります。自分の初期シーケンス番号 x を知らせます。エディタの状態は `SYN-SENT` になります。
2. エンジンの OS が `SYN` と `ACK` を 1 つのセグメントで返します。自分の初期シーケンス番号 y を知らせ x の次の番号（x + 1）が欲しいと答えます。
3. エディタが `ACK`（y + 1 が欲しい）を返します。この時点で両側が `ESTABLISHED` になります。

なぜ 3 回なのでしょうか。接続の確立は「双方の初期シーケンス番号を相手に覚えてもらう」作業です。エディタの番号 x をエンジンが受け取ったこととエンジンの番号 y をエディタが受け取ったことの、2 つを確かめる必要があります。② は「x を受け取った」と「自分の y」を 1 つにまとめられるので、合計で 3 回に収まります（RFC 9293 §3.4.1）。

`SYN` はデータがなくてもシーケンス番号を 1 つ消費します。そのため、確認応答番号は x ではなく x + 1 になります。`FIN` も同じです。

### OS が完了させる部分と、accept が受け取る部分

ここでアプリのコードとの対応を見ておきます。

`listen` を呼ぶと OS は接続要求を待ち受ける状態（`LISTEN`）になります。③ まで終わった接続は OS の中の待ち行列に並びます。アプリが `accept`（.NET では `AcceptTcpClientAsync`）を呼ぶとその待ち行列から 1 本が取り出されます。

つまり、<strong>アプリが `accept` を呼んでいなくても、接続の確立は終わる</strong>ことがあります。エディタ側の `connect` が成功しても、エンジンが `accept` を呼ぶ前ならエンジンのアプリはまだ接続に気づいていません。エディタが握手の `Write` を送っても、エンジンが `accept` して読むまで、返事は来ません。第 60 章で握手に時間切れを付けるのは、このためです。

待ち行列の長さは `listen` の引数（backlog）で決まります。`TcpListener.Start()` は `Socket` の `Bind` と `Listen` をまとめた呼び出しです。`Start(int backlog)` で待ち行列の長さも渡せます。

### 誰も待っていないポートに繋ぐと

では、エンジンが起動していない（誰も `listen` していない）ポートに `connect` すると、どうなるでしょうか。

RFC 9293 §3.5.2 によると、接続が存在しない状態（CLOSED）で受け取った `SYN` に対して、受け取った側は `RST` を返します。`RST` を受け取ったエディタの `connect` は「接続が拒否された」（`ConnectionRefused`、Windows のエラー番号 10061）で失敗します。

しかし、手元の Windows 11 ではこの失敗が返るまでに<strong>約 2 秒</strong>かかりました。

```text title="待ち受けのないポートへの connect（実測）"
v4 refused 10061 2033 ms
v4 refused 10061 2026 ms
v4 refused 10061 2056 ms
localhost SocketException 2087 ms
Socket.Connect 10061 2052 ms
```

5 回ともほぼ 2 秒（2026〜2087 ミリ秒）でした。`TcpClient`、`Socket`、名前の `localhost` のどれでも同じです。拒否そのものは一瞬で返っているはずです（`RST` は、すぐ返る約束です）。それなのに 2 秒かかるのは、OS が拒否を受けて自動で再試行しているからだと考えられます。ただし、その仕組みは確かめていません。実測で分かっているのは 2 秒前後かかることだけです。

この 2 秒は、第 59 章の設計に影響します。エンジンを起動した直後に繋がるまで `connect` を繰り返す（ポーリング）作りにすると、1 回の失敗ごとに 2 秒かかります。そこで、第 59 章では、エンジンを起動したエディタが、エンジンの標準出力から「待ち受けを始めた」知らせを受け取ってから繋ぎます。繋ぎにいって失敗を繰り返すことを避ける作りです。

`connect` に時間切れを付けた場合も測りました。

```text title="待ち受けなしで、時間切れを付けた connect（実測）"
[D] 待ち受けなし、時間切れ 500 ms -> TimeoutException, 511 ms
[D] 待ち受けなし、時間切れ 3000 ms -> SocketException, 2029 ms
```

時間切れが 500 ミリ秒なら拒否が返る前に自分で諦めて `TimeoutException` になります。3 秒なら 2 秒ほどで `SocketException`（`ConnectionRefused`）になります。<strong>「接続が拒否された」と「時間内に繋がらなかった」は、別の失敗</strong>です。ログにはどちらかが分かるように残してください。

### SYN の再送

`SYN` が途中で消えて返事が来ないときは、再送します。RFC 6298 は返事が来ない場合の最初の待ち時間（初期 RTO）を 1 秒にすることを勧めています（§2.1）。待つたびに時間は 2 倍に延びます（§5.5）。手元の `Get-NetTCPSetting` には `InitialRto` が 1000（ミリ秒）、`MaxSynRetransmissions` が 4 と出ています。ループバックでは `SYN` が途中で消えることは考えにくいので、この再送が働く場面はほぼないはずです。


## データ転送：確認応答と再送

データの流れはこうなります。送る側がシーケンス番号つきのセグメントを送ります。受け取る側が「ここまで受け取った」という確認応答番号を返します。送る側は確認応答が返ったバイトを送信バッファから捨てます。

確認応答は累積です。確認応答番号 1500 は「1499 までは全部受け取った」という意味です。たとえば、1000〜1499 のセグメントが欠けたまま 1500 以降のセグメントが届いたとします。このときも、確認応答番号は 1000 のままです。欠けた所が埋まるまで確認応答は進みません。

### 再送のタイマー

送ったセグメントの確認応答が一定時間来なければ、送る側は同じセグメントを再送します。この待ち時間を RTO（Retransmission Timeout）と呼びます。短すぎるとまだ生きているセグメントを無駄に再送します。長すぎると本当に消えたときに回復が遅れます。

RFC 6298 は RTO を直近の往復時間（RTT）の測定値から次のように決めます。

- 最初の測定値 R で `SRTT = R`、`RTTVAR = R / 2`、`RTO = SRTT + max(G, 4 × RTTVAR)`（`G` はタイマーの刻み幅）
- 次の測定値 R' では `RTTVAR = 0.75 × RTTVAR + 0.25 × |SRTT − R'|`、`SRTT = 0.875 × SRTT + 0.125 × R'`。そのあとで RTO を同じ式で計算し直す（RTTVAR を先に更新する）

`SRTT` は RTT の平均（滑らかにしたもの）で、`RTTVAR` は、そのばらつきです。ばらつきが大きいほど、RTO を長めに取ります。

数字を入れてみます。RTT が最初に 100 ミリ秒、次が 120 ミリ秒だったとします。

1. 最初：`SRTT = 100`、`RTTVAR = 50`、`RTO = 100 + 4 × 50 = 300` ミリ秒
2. 次：`RTTVAR = 0.75 × 50 + 0.25 × |100 − 120| = 37.5 + 5 = 42.5`、`SRTT = 0.875 × 100 + 0.125 × 120 = 102.5`、`RTO = 102.5 + 4 × 42.5 = 272.5` ミリ秒

RFC 6298 は計算した RTO が 1 秒に満たなければ、1 秒に切り上げることを勧めています（§2.4）。この例なら実際の RTO は 1 秒です。一方、手元の Windows の `MinRto` の設定は 300 ミリ秒でした。つまり、この PC は RFC の勧めより短い下限を使っています。Windows の実際の再送の挙動までは、確かめていません。

タイマーが切れて再送するたびに RTO は 2 倍になります（バックオフ）。1 秒、2 秒、4 秒と延びていきます。再送されたセグメントの RTT は測定に使いません（Karn のアルゴリズム、MUST）。再送に対する確認応答なのか最初の送信に対するものなのかを見分けられないからです。

### 高速再送

タイマーを待たずに欠けたセグメントを見つける方法もあります。受け取る側は順番の合わないセグメントを受け取ると、直前と同じ確認応答番号をすぐに返します（重複 ACK）。送る側が同じ確認応答番号を 3 回続けて受け取ったら、「その番号から始まるセグメントが欠けた」と判断して、タイマーを待たずに再送します（RFC 5681 §3.2）。

### ループバックでの意味

ここまでの再送の仕組みはネットワークでセグメントが消える場合の備えです。ループバックでは途中のルーターや回線を通らないので、この備えが働く場面は少ないはずです。そのため、この章では再送を実験で確かめていません。ただし、受け取る側のバッファが満杯ならセグメントを受け取ってもらえません。これは再送とは別の仕組み（次のフロー制御）が扱います。そして、アプリにとってこちらのほうが、ずっと身近です。


## フロー制御：Write が戻らなくなるとき

受け取る側のバッファには限りがあります。送る側が速すぎてアプリが読むのが遅いとバッファが溢れます。これを防ぐ仕組みがフロー制御です。

受け取る側はすべての確認応答にウィンドウの値を付けて、「あと何バイトなら受け取れる」と送る側に伝えます。送る側は確認応答をまだ受け取っていないバイトの量をこのウィンドウ以内に収めます。

<svg class="fig flow" viewBox="0 0 720 230" role="img" aria-label="送信側のバイト列。確認応答済み、送信済みで確認待ち、送信できる、まだ送れない、の 4 つの領域とウィンドウの範囲を示す"><text x="14" y="22" class="fig-title">送る側から見たバイト列とウィンドウ</text><rect x="30" y="60" width="150" height="46" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="105" y="83" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">確認応答済み</text><rect x="180" y="60" width="150" height="46" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="255" y="83" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">送信済み・確認待ち</text><rect x="330" y="60" width="150" height="46" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="405" y="83" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">今すぐ送れる</text><rect x="480" y="60" width="210" height="46" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="6 4"/><text x="585" y="83" text-anchor="middle" dominant-baseline="central" style="font-size:12px;font-weight:600">まだ送れない（ウィンドウの外）</text><line x1="180" y1="112" x2="180" y2="140" stroke="currentColor" stroke-width="2"/><text x="180" y="156" text-anchor="middle" style="font-size:12px">SND.UNA（未確認の先頭）</text><line x1="330" y1="112" x2="330" y2="176" stroke="currentColor" stroke-width="2"/><text x="330" y="192" text-anchor="middle" style="font-size:12px">SND.NXT（次に送る番号）</text><line x1="480" y1="112" x2="480" y2="140" stroke="currentColor" stroke-width="2"/><text x="480" y="156" text-anchor="middle" style="font-size:12px">SND.UNA + SND.WND</text><path d="M180,46 L480,46" stroke="currentColor" stroke-width="2" fill="none"/><text x="330" y="40" text-anchor="middle" style="font-size:12px;font-weight:600">ウィンドウ（相手が受け取れる量）</text><text x="360" y="220" text-anchor="middle" style="font-size:12px">確認応答が進むと、左端（SND.UNA）が右へ動いて、窓が右へずれる。</text></svg>

確認応答が返って `SND.UNA` が右へ進むと窓が右へずれて、新しいバイトを送れるようになります。受け取るアプリが読んでバッファに空きができると、次の確認応答に載るウィンドウの値が大きくなります。逆に、アプリが読まなければウィンドウは小さくなって、やがて 0 になります。

ウィンドウが 0 になったら、送る側は新しいデータを送れません。ただし、「窓が開いた」ことを知らせる更新が途中で消えると、送る側がいつまでも待ち続けてしまいます。そのため、送る側はウィンドウが 0 の間も小さな探りのセグメントを間をあけて送ります（ゼロ ウィンドウ プローブ。RFC 9293 §3.8.6.1、MUST）。

### アプリから見ると：Write が止まる

ここでアプリの `Write` がどう見えるかを実験します。サーバー側が一切 `Read` しない状態で、クライアントが 4 KiB ずつ書き続けます。

```csharp title="相手が読まないとき、送れる量はどこで止まるか"
{
    var (c, s) = Pair(out var l);
    Console.WriteLine($"[6] 既定 SendBufferSize={c.SendBufferSize}, ReceiveBufferSize={s.ReceiveBufferSize}");
    var ns = c.GetStream(); long sent = 0; var chunk = new byte[4096];
    var t = Task.Run(() => { while (true) { ns.Write(chunk); Interlocked.Add(ref sent, chunk.Length); } });
    Thread.Sleep(1500);
    long a = Interlocked.Read(ref sent); Thread.Sleep(500); long b2 = Interlocked.Read(ref sent);
    Console.WriteLine($"    相手が読まないとき: 送れた量 {a} バイト ({a / 1024.0:F0} KiB)、0.5 秒後 {b2}（増えない=Write が止まっている）");
    c.Client.Close(); s.Close(); l.Stop();
}
```

```text title="実行結果（実測）"
[6] 既定 SendBufferSize=65536, ReceiveBufferSize=65536
    相手が読まないとき: 送れた量 225280 バイト (220 KiB)、0.5 秒後 225280（増えない=Write が止まっている）
```

`SendBufferSize` と `ReceiveBufferSize` はどちらも 64 KiB が既定でした。ところが、書けた量は 220 KiB で、2 つの合計（128 KiB）よりも多くなっています。内訳は確かめていません。Windows がバッファの大きさを自動で調整している（Windows の TCP の設定には `AutoTuningLevelLocal: Normal` と出ています）ことが関係していると考えられますが、推測です。

確かなことは <strong>数百 KiB のところで `Write` が戻らなくなる</strong>ことです。0.5 秒たっても書けた量は 225280 のままでした。`Write` はエラーも例外も出さずにただ待たされています。

1 回の大きな `Write` では少し違う結果になりました。

```text title="1 MiB を 16 回続けて書く（相手は読まない）（実測）"
1 MiB を 16 回(相手は読まない): 完了した Write = 1 回
```

1 回目の 1 MiB の `Write` は戻りましたが、2 回目からは戻りませんでした。1 回目が 220 KiB のバッファよりずっと大きいのに戻れた理由は確かめていません。いずれにしても「Write が戻った」ことは、「相手が受け取れる状態だ」ことを意味しません。

### 両側が書き合うと、動けなくなる

もっと危険なのは両側が「先に書く」作りです。両側が相手の読み取りを待たずに書き続けると、両方の `Write` が止まります。止まった側は `Read` を呼べないので、相手の送ってきたデータを受け取れません。相手も同じなのでどちらも進めなくなります。

```csharp title="両側が 4 KiB ずつ書き続けて、誰も読まない"
var l = new TcpListener(IPAddress.Loopback, 0); l.Start(); int port = ((IPEndPoint)l.LocalEndpoint).Port;
var c = new TcpClient(); var a = l.AcceptTcpClientAsync(); c.Connect(IPAddress.Loopback, port); var s = a.Result;
long sc = 0, ss = 0; var chunk = new byte[4096];
Task.Run(() => { var n = c.GetStream(); while (true) { n.Write(chunk); Interlocked.Add(ref sc, chunk.Length); } });
Task.Run(() => { var n = s.GetStream(); while (true) { n.Write(chunk); Interlocked.Add(ref ss, chunk.Length); } });
Thread.Sleep(2000); long a1 = sc + ss; Thread.Sleep(1000); long a2 = sc + ss;
Console.WriteLine($"両側が 4KiB ずつ書き続ける: C {sc/1024} KiB, S {ss/1024} KiB, 1 秒で増えた量 {a2 - a1}");
```

```text title="実行結果（実測）"
両側が 4KiB ずつ書き続ける: C 236 KiB, S 188 KiB, 1 秒で増えた量 0
```

2 秒後には両側とも数百 KiB で止まり、次の 1 秒では、1 バイトも増えませんでした。エラーも例外もなく、ただ止まります。デッドロックです。

この作りを避ける方針は 1 つです。<strong>読むループを書く処理とは別に常に回しておく</strong>ことです。第 54 章の `EngineClient` が返事を読む `ReadLoopAsync` を別のタスクで回し続けているのは、この理由もあります。読むほうが止まらなければ相手の `Write` も止まりません。

もう 1 つ見落としやすい落とし穴があります。第 53 章のパイプ版サーバーのように「1 つ読んで、1 つ書く」を順に繰り返す作りは要求と返事が 1 対 1 の間は、安全です。しかし、サーバーが通知（返事を伴わない一方的な送信）を送り始めると、その瞬間から両側が書く作りに変わります。通知が大きくなるとデッドロックの条件がそろいます。通知を足すときは読むループを必ず別にしてください。

### ウィンドウで決まる速度の上限

送る側は確認応答を待たずにウィンドウの分まで送れます。逆に言うと、ウィンドウを使い切ったら確認応答が戻るまで止まるので、1 往復（RTT）あたりに運べる量は、ウィンドウの大きさが上限です。

```text
スループットの上限 ≒ ウィンドウ ÷ RTT
```

ループバックの RTT は手元で、1 バイトの往復が約 25 マイクロ秒でした（後述）。ウィンドウが 64 KiB なら `65536 バイト ÷ 25.2 μs ≒ 2.6 GB/s` が、目安の上限です。実測のスループットは 1615 MiB/s（約 1.7 GB/s）で、上限の 6 割強でした。ウィンドウだけが上限を決めているわけではないので、あくまで桁の目安です。

ネットワークの向こうの相手（RTT が 100 ミリ秒ほど）だと同じ 64 KiB のウィンドウでは、`65536 ÷ 0.1 ≒ 655 KB/s` にしかなりません。16 ビットのウィンドウでは足りないので、「ウィンドウ スケール」が作られました。ループバックでは RTT がとても小さいので、この制限が問題になることは少ないでしょう。

### 小さなウィンドウと愚かなウィンドウ症候群

受け取る側のアプリが 1 バイトずつ読むとバッファに 1 バイトの空きができるたびに、「ウィンドウが 1 バイト空きました」と知らせるのが、素直な実装です。すると、送る側は 1 バイトのデータに 40 バイトのヘッダーを付けて送ります。これを愚かなウィンドウ症候群（Silly Window Syndrome）と呼びます。

RFC 9293 は送る側（MUST-38）と受け取る側（MUST-39）の両方に、この症状を避ける処理を求めています（§3.8.6.2）。受け取る側はバッファの空きが、バッファ全体の 1/2 か MSS のどちらか小さいほうに満たない間は、窓を広げて知らせません。送る側は窓が十分広がるまで小さなデータを送るのを待ちます。アプリが気にすることはありません。OS が守ってくれます。


## 輻輳制御

ネットワークの途中が混んでいるときに全員が全速力で送ると、さらに混んで全員が遅くなります。この事態を避けるのが輻輳制御です。送る側がネットワークの混み具合を推測して、輻輳ウィンドウ（cwnd）という自主的な上限を持ちます。実際に送れる量は受け取る側のウィンドウ（rwnd）と cwnd の小さいほうです。

### スロー スタートと輻輳回避

接続の開始直後はネットワークの状態が分からないので、小さな cwnd から始めて、確認応答が返るたびに増やします（スロー スタート）。確認応答で新しく受け取ったバイト数ぶんだけ cwnd を増やします（上限は SMSS、RFC 5681 の式 2）。つまり、1 往復（RTT）ごとに cwnd がほぼ 2 倍になります。

cwnd が `ssthresh`（しきい値）を超えたら、増やし方を緩めます（輻輳回避）。確認応答のたびに `cwnd += SMSS × SMSS ÷ cwnd` で増やすので、1 往復でほぼ 1 セグメントだけ増えます。

セグメントの欠落（タイムアウトや重複 ACK）を見つけると、`ssthresh` を `max(FlightSize ÷ 2, 2 × SMSS)` に下げて cwnd も下げます。

### 最初の cwnd

最初の cwnd（初期ウィンドウ、IW）は RFC 5681 では SMSS に応じて決まります。

- SMSS が 1095 バイト以下なら 4 セグメントまで
- 1095 より大きく 2190 バイト以下なら 3 セグメントまで
- 2190 バイトより大きいなら 2 セグメントまで

SMSS が 1460 なら `3 × 1460 = 4380` バイトです。最初の 1 往復で送れるのは、4380 バイトまで。次の往復で 8760 バイト、その次は 17520 バイト、と倍々に増えます。

ただし、これは RFC 5681 の値です。手元の `Get-NetTCPSetting` には `InitialCongestionWindow` が 10 と出ています（セグメント数だと思われますが、単位は確かめていません）。また、輻輳制御のアルゴリズム（`CongestionProvider`）は `CUBIC` と出ています。この章では RFC 5681 の基本形だけを説明しました。CUBIC の式と IW を 10 にする RFC（RFC 6928）は、読んでいません。

### ループバックでの意味

ループバックではセグメントが消えない（と考えられる）ので、cwnd は増える一方です。実際に、5 MiB を 14 ミリ秒で往復できたことから、スロー スタートが体感できるほどの足かせにはなっていないようです。ただし、これも推測です。測ったのは全体の時間だけで cwnd は観測していません。

エンジンとエディタの通信を設計するときは、輻輳制御を意識する場面はほぼない、というのが筆者の見立てです。ただし、アルゴリズムの名前と役割は `netstat` の結果や性能の資料を読むときに出てくるので、覚えておく価値があります。


## Nagle アルゴリズムと遅延 ACK

TCP には小さなデータの送信を減らす仕組みが 2 つあります。送る側の Nagle アルゴリズムと受け取る側の遅延 ACK です。それぞれは理にかなっていますが、組み合わさると予想外の遅れを生むことがあります。

### Nagle アルゴリズム（送る側）

動機はさきほどのヘッダーの無駄です。1 文字ずつ送るキー入力のような使い方では、41 バイトのパケットにデータは 1 バイトしかありません。RFC 896（1984 年、John Nagle）はこれを解決する、単純な規則を提案しました。

> 前に送ったデータの確認応答が、まだ返っていないなら新しく書かれたデータをすぐには送らない。確認応答が返るまで溜めておく。

確認応答が返ったら溜まっていた分をまとめて 1 つのセグメントで送ります。接続がアイドル（未確認のデータがない）なら書かれたデータはすぐ送られるので、1 文字ずつのキー入力の反応は遅れません。RFC 9293 も実装することを推奨しています（SHOULD）。そして、アプリが接続ごとに無効にできることを必須としています（MUST、§3.7.4）。

### 遅延 ACK（受け取る側）

受け取る側がデータを受け取るたびに確認応答だけのセグメントをすぐ返すと確認応答がたくさん飛びます。そこで、少し待って返事のデータがあれば、それに相乗りさせる（あるいは次のセグメントの分とまとめる）のが、遅延 ACK です。

RFC 9293 §3.8.6.3 は、遅らせる時間を 0.5 秒未満に抑えること（MUST）、最大サイズのセグメントを 2 つ受け取るたびに少なくとも 1 回は確認応答を返すこと（SHOULD）を求めています。

手元の `Get-NetTCPSetting`（Internet）の値は、`DelayedAckTimeout` が 40（ミリ秒）、`DelayedAckFrequency` が 2 でした。

### 組み合わさると

この 2 つが組み合わさって起きる有名な落とし穴があります。送る側がヘッダー（4 バイト）と本文（10 バイト）を 2 回の `Write` に分けて送り、そのあと返事を待つ場合です。

<svg class="fig flow" viewBox="0 0 720 300" role="img" aria-label="Nagle アルゴリズムと遅延 ACK の組み合わせ。2 回に分けた Write の 2 つ目が、1 つ目の ACK を待って止まり、受け取る側は遅延 ACK で待つので、双方が待ち合わせる"><defs><marker id="tcN" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">2 回に分けて Write すると、起こりうる待ち合わせ</text><text x="100" y="52" text-anchor="middle" style="font-size:13px;font-weight:600">送る側（Nagle 有効）</text><text x="620" y="52" text-anchor="middle" style="font-size:13px;font-weight:600">受ける側（遅延 ACK）</text><line x1="100" y1="62" x2="100" y2="290" stroke="#94a3b8" stroke-width="2"/><line x1="620" y1="62" x2="620" y2="290" stroke="#94a3b8" stroke-width="2"/><line x1="100" y1="84" x2="620" y2="104" stroke="currentColor" stroke-width="2" marker-end="url(#tcN)"/><text x="360" y="84" text-anchor="middle" style="font-size:12px;font-weight:600">① Write(ヘッダー 4 バイト)：アイドルなので、すぐ送られる</text><rect x="14" y="124" width="230" height="52" rx="8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="129" y="142" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">② Write(本文 10 バイト)は、</text><text x="129" y="160" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">①の ACK を待って、保留される</text><rect x="470" y="124" width="236" height="52" rx="8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="588" y="142" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">4 バイトだけでは返事を作れず、</text><text x="588" y="160" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">ACK も遅らせる（遅延 ACK）</text><line x1="620" y1="214" x2="100" y2="240" stroke="currentColor" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#tcN)"/><text x="360" y="212" text-anchor="middle" style="font-size:12px;font-weight:600">③ 遅延 ACK のタイマーが切れて、ようやく ACK（Windows の設定値は 40 ms）</text><text x="360" y="278" text-anchor="middle" style="font-size:12px">①の ACK が来て、②がやっと送られる。往復 1 回が、数十ミリ秒に伸びる。</text></svg>

送る側は① を送ったあと② の本文を① の確認応答が返るまで保留します（Nagle）。受け取る側は 4 バイトだけでは返事を作れず確認応答も遅らせます（遅延 ACK）。互いに相手を待つ状態になり遅延 ACK のタイマーが切れるまで、動きません。

これを確かめる実験です。4 バイトのヘッダーと 10 バイトの本文を送って、4 バイトの返事をもらう往復を書き方と `NoDelay` の組み合わせごとに平均します。

```csharp title="Nagle × 遅延 ACK：書き方と NoDelay を変えて、往復の時間を測る"
static double Rtt(bool noDelay, bool split, int iters)
{
    var (c, s) = Pair(out var l);
    c.NoDelay = noDelay; s.NoDelay = noDelay;     // true なら Nagle を切る（両側とも同じ設定にする）
    var srv = Task.Run(() => {
        var ns = s.GetStream(); var b = new byte[64];
        // サーバー側: 14 バイト（ヘッダー 4 + 本文 10）が揃うまで読み、揃ったら 4 バイトの返事を書く
        try { while (true) { int got = 0; while (got < 14) { int n = ns.Read(b, got, 14 - got); if (n == 0) return; got += n; } ns.Write(new byte[4]); } } catch { }
    });
    var cs = c.GetStream(); var rb = new byte[4];
    var sw = Stopwatch.StartNew();
    for (int i = 0; i < iters; i++)
    {
        // split が true なら 2 回の Write（Nagle と遅延 ACK の待ち合わせが起こりうる形）。false なら 1 回の Write
        if (split) { cs.Write(new byte[4]); cs.Write(new byte[10]); } else cs.Write(new byte[14]);
        // 返事の 4 バイトが揃うまで読む（Read は少なく返ることがある）
        int g = 0; while (g < 4) g += cs.Read(rb, g, 4 - g);
    }
    sw.Stop(); c.Dispose(); s.Dispose(); l.Stop();
    return sw.Elapsed.TotalMilliseconds / iters;   // 1 往復あたりの平均（ミリ秒）
}
Console.WriteLine($"    まとめて 1 回 Write, Nagle 有効: {Rtt(false, false, 200):F3}");
Console.WriteLine($"    2 回に分けて Write, Nagle 有効: {Rtt(false, true, 50):F3}");
Console.WriteLine($"    2 回に分けて Write, NoDelay   : {Rtt(true, true, 2000):F3}");
Console.WriteLine($"    まとめて 1 回 Write, NoDelay   : {Rtt(true, false, 2000):F3}");
```

```text title="実行結果（1 往復の平均、ミリ秒）（実測）"
    まとめて 1 回 Write, Nagle 有効: 0.020
    2 回に分けて Write, Nagle 有効: 0.027
    2 回に分けて Write, NoDelay   : 0.026
    まとめて 1 回 Write, NoDelay   : 0.019
```

予想では「2 回に分けて Nagle 有効」の行が、数十ミリ秒に伸びるはずでした。ところが、手元のループバックでは遅れは再現しませんでした。4 つとも 0.02 ミリ秒前後（20〜27 マイクロ秒）です。「2 回に分ける」と少し遅い（0.027 と 0.020）のは、セグメントが 1 つ増える分だと考えられます。

なぜ再現しないのか理由は確かめていません。ループバックの経路では確認応答の扱いが、ネットワークの向こうとは違うのかもしれません。大事なのは「この PC のループバックで再現しなかった」ことが、「この問題は起きない」ことの証明にならない点です。別の OS や別の通信路で遅延 ACK の遅れが出る事例は、よく知られています（この章では確かめていません）。

そこで、遅れが出ても出なくても困らないように次の 2 つを両方とも守ります。

1. 1 つのメッセージは 1 回の `Write` で書く。ヘッダーと本文を別々に書かない。第 53 章の `WriteMessage` が長さと本文を 1 つの配列にまとめてから書いていたのは、この対策でもありました。
2. <strong>`NoDelay` を有効にする</strong>。`TcpClient.NoDelay = true`（C++ なら `setsockopt(…, TCP_NODELAY, …)`）。Nagle を切って書いたデータをすぐ送らせます。Microsoft Learn によると、Windows の `TCP_NODELAY` は既定では無効（Nagle が有効）です。

`NoDelay` にも副作用があります。細かい `Write` をたくさん呼ぶとそのまま小さなセグメントの山になります。1 バイトずつ書くループのようなコードを書かずメッセージ単位で組み立ててから、1 回で書く作りにしてください。


## 切断：FIN と RST

接続の終わり方は 2 通りあります。正常な終わり（`FIN`）と強制的な終わり（`RST`）です。

### FIN：片側ずつ閉じる

TCP の接続は実は 2 本の一方通行が重なったものです。片方向を閉じる合図が `FIN` で、「もう送るデータがない」という意味です。`FIN` を送った側も相手からのデータはまだ受け取れます（半閉じ half-close）。両方向を閉じるには両側が `FIN` を送ります。

<svg class="fig flow" viewBox="0 0 720 360" role="img" aria-label="接続の終わり方。先に閉じる側が FIN を送り、相手が ACK を返し、相手も FIN を送り、最初の側が ACK を返して TIME_WAIT になる"><defs><marker id="tcF" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">正常な切断（FIN を 2 回、ACK を 2 回）</text><text x="110" y="52" text-anchor="middle" style="font-size:13px;font-weight:600">先に閉じる側</text><text x="610" y="52" text-anchor="middle" style="font-size:13px;font-weight:600">後から閉じる側</text><line x1="110" y1="62" x2="110" y2="348" stroke="#94a3b8" stroke-width="2"/><line x1="610" y1="62" x2="610" y2="348" stroke="#94a3b8" stroke-width="2"/><line x1="110" y1="84" x2="610" y2="108" stroke="currentColor" stroke-width="2" marker-end="url(#tcF)"/><text x="360" y="86" text-anchor="middle" style="font-size:12px;font-weight:600">① FIN（もう送らない：Close / Shutdown(Send)）</text><rect x="14" y="76" width="92" height="22" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="60" y="88" text-anchor="middle" dominant-baseline="central" style="font-size:11px">FIN_WAIT_1</text><line x1="610" y1="144" x2="110" y2="168" stroke="currentColor" stroke-width="2" marker-end="url(#tcF)"/><text x="360" y="144" text-anchor="middle" style="font-size:12px;font-weight:600">② ACK</text><rect x="614" y="132" width="92" height="22" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="660" y="144" text-anchor="middle" dominant-baseline="central" style="font-size:11px">CLOSE_WAIT</text><rect x="14" y="156" width="92" height="22" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="60" y="168" text-anchor="middle" dominant-baseline="central" style="font-size:11px">FIN_WAIT_2</text><text x="596" y="196" text-anchor="end" style="font-size:11px">アプリが Read で 0 を受け取り、</text><text x="596" y="212" text-anchor="end" style="font-size:11px">自分も Close を呼ぶまで、CLOSE_WAIT のまま</text><line x1="610" y1="236" x2="110" y2="260" stroke="currentColor" stroke-width="2" marker-end="url(#tcF)"/><text x="360" y="236" text-anchor="middle" style="font-size:12px;font-weight:600">③ FIN</text><rect x="614" y="224" width="92" height="22" rx="6" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5"/><text x="660" y="236" text-anchor="middle" dominant-baseline="central" style="font-size:11px">LAST_ACK</text><line x1="110" y1="296" x2="610" y2="320" stroke="currentColor" stroke-width="2" marker-end="url(#tcF)"/><text x="360" y="296" text-anchor="middle" style="font-size:12px;font-weight:600">④ ACK</text><rect x="14" y="304" width="92" height="22" rx="6" fill="rgba(229,170,40,0.28)" stroke="#e5aa28"/><text x="60" y="316" text-anchor="middle" dominant-baseline="central" style="font-size:11px">TIME_WAIT</text><rect x="614" y="318" width="92" height="22" rx="6" fill="rgba(148,163,184,0.18)" stroke="#94a3b8"/><text x="660" y="330" text-anchor="middle" dominant-baseline="central" style="font-size:11px">CLOSED</text></svg>

アプリから見ると `Read` が `0` を返すのが、「相手が `FIN` を送った」ことの知らせです。これをファイルの終わり（EOF）と同じように扱います。`Read` が 0 を返したら読み取りのループを終えて、自分も閉じます。

実験で確かめます。クライアントが先に閉じてサーバーはまだ閉じない状態を `netstat` で見ます。

```text title="先に Close した側が FIN_WAIT_2、後の側が CLOSE_WAIT（実測）"
[client が先に close した直後 (server は未 close)]
  TCP    127.0.0.1:54941        127.0.0.1:54942        CLOSE_WAIT      11392
  TCP    127.0.0.1:54942        127.0.0.1:54941        FIN_WAIT_2      11392
[server も close]
  TCP    127.0.0.1:54942        127.0.0.1:54941        TIME_WAIT       0
```

図の ①②の後、後から閉じる側が `CLOSE_WAIT`、先に閉じた側が `FIN_WAIT_2` になっているのが、そのまま見えます。両方閉じたあと先に閉じた側のクライアント（54942）の行に `TIME_WAIT` が残りました。PID が 0 なのはもうプロセスのものではなく、OS が持っている状態だからです。

`CLOSE_WAIT` がいつまでも残るのはアプリが閉じ忘れている印です。相手が `FIN` を送ってきたのに、こちらが `Read` で 0 を受け取って閉じる処理を書いていないとソケットがこの状態に留まります。

### TIME_WAIT：先に閉じた側に残る

最後の ACK を送った側はすぐには `CLOSED` にならず `TIME_WAIT` で待ちます。RFC 9293 §3.6.1 はこの待ち時間を 2 × MSL とすることを必須としています。MSL（Maximum Segment Lifetime）は、セグメントがネットワークにいられる最長の時間で、この RFC は 2 分としています（§3.4.3）。つまり 4 分です。手元の Windows での実際の長さは、確かめていません。

待つ理由は 2 つです。1 つは最後の ACK が消えたとき相手が `FIN` を再送してくるので、それに応答するためです。もう 1 つは同じ 4 つ組の古い接続のセグメントが、新しい接続に紛れ込まないようにするためです。

`TIME_WAIT` が残るのは <strong>先に閉じた側</strong>です。エディタが先に切るならエディタ側に残ります。エンジンが固定のポートで待ち受けているときの再起動で、「ポートがまだ使えない」ことがあるのでは、と気になるかもしれません。手元で試したところ `TIME_WAIT` が残った状態でも同じポートで `TcpListener` を作り直すことができました（実測）。

### RST：即座に捨てる

`RST` は礼儀正しい終わり方ではありません。「その接続は存在しない、捨てろ」という合図で、受け取った側はバッファのデータも捨てて、すぐ接続を閉じます。次のような場面で出ます。

1. 未読のデータを残したまま `Close` した。
2. 閉じた接続にデータを送ってしまった。
3. 存在しない接続（誰も待っていないポートなど）にデータや `SYN` が届いた。
4. プロセスが死んだ。

1 を実験します。サーバーがクライアントの送った 100 バイトを読まずに `Close` します。

```csharp title="未読のデータを残して Close すると、相手に何が見えるか"
{
    var (c, s) = Pair(out var l);
    c.GetStream().Write(new byte[100]); Thread.Sleep(50);       // s は読まない
    s.Close();                                                    // 未読 100B を抱えて close
    Thread.Sleep(50);
    try { var b = new byte[10]; int n = c.GetStream().Read(b); Console.WriteLine($"[3] 未読ありで close -> 相手の Read = {n}"); }
    catch (Exception e) { Console.WriteLine($"[3] 未読ありで close -> 相手の Read 例外: {e.GetType().Name} / {(e.InnerException as SocketException)?.SocketErrorCode} {(e.InnerException as SocketException)?.NativeErrorCode}"); }
    c.Dispose(); l.Stop();
}
{   // 未読なしで close -> Read が 0
    var (c, s) = Pair(out var l);
    s.Close(); Thread.Sleep(50);
    int n = c.GetStream().Read(new byte[10]);
    Console.WriteLine($"[3b] 未読なしで close -> 相手の Read = {n} (EOF)");
    // 閉じられた後の Write
    try { c.GetStream().Write(new byte[10]); Thread.Sleep(50); c.GetStream().Write(new byte[10]); Console.WriteLine("    Write 成功(2回)"); }
    catch (Exception e) { Console.WriteLine($"    FIN 後の 2 回目の Write: {(e.InnerException as SocketException)?.SocketErrorCode}"); }
    c.Dispose(); l.Stop();
}
```

```text title="実行結果（実測）"
[3] 未読ありで close -> 相手の Read 例外: IOException / ConnectionReset 10054
[3b] 未読なしで close -> 相手の Read = 0 (EOF)
    FIN 後の 2 回目の Write: ConnectionAborted
```

未読のデータがある状態で閉じると、相手の `Read` は `0`（正常な EOF）ではなく `IOException`（`ConnectionReset`、10054）になります。<strong>同じ `Close` でも未読のデータがあるかどうかで、相手に見える結果が変わります。</strong>また `RST` を受け取った側は受信バッファに残っていた未読のデータを捨てることがあります。

3b の最後の行も大事です。相手が閉じたあとでこちらが `Write` します。1 回目の `Write` は成功しました（例外が出ていません）。相手はすでに閉じているのでその 10 バイトに `RST` を返したのだと考えられます。その `RST` が届いたあとの 2 回目の `Write` で、初めて `ConnectionAborted` になりました。つまり、`Write` が成功しても相手に届いたとは言えません。ここまでの章で言ってきた「`Write` の成功は、受け取りを意味しない」ことの実例です。

4 のプロセスの死は第 57 章の復旧に直結します。エンジンを強制終了してエディタの読み待ちに何が届くかを測りました。

```text title="エンジンのプロセスを Kill したとき、読み待ちに届く例外（実測）"
[C] サーバーを Kill -> 読み待ちに届いた例外: IOException/ConnectionReset, 3 ms 後
```

3 ミリ秒後に `ConnectionReset` が届きました。プロセスが死ぬと OS がそのプロセスの持っていた接続を片づけて、相手に `RST` を送るようです。ローカルのプロセスの死は <strong>ほぼ即座に</strong>分かります。ただし、これは「プロセスが死んだ」場合だけです。プロセスが生きていて固まっているだけならこの通知は来ません。これは、第 61 章の「ハートビート」の動機になります。

### 正しい閉じ方

片方が閉じる前にデータを全部読み切らせるため、閉じ方に手順を決めます。Microsoft Learn の説明にも同じ考え方があります。`closesocket` は暗黙に切断の手順を始めてしまうので、それに頼らず `shutdown` を明示的に呼ぶほうが、閉じるときの問題を減らせるという趣旨です。

1. 閉じたい側が `Shutdown(Send)`（C++ なら `shutdown(s, SD_SEND)`）を呼ぶ。これで `FIN` が送られる。
2. 相手が `Read` で 0 を受け取る（読み残しがなければ、ここまでのデータを全部読み切れる）。
3. 相手が自分の返事を全部送ってから、自分も `Shutdown(Send)` を呼ぶ。
4. 最初に閉じた側が `Read` で 0 を受け取るまで、読み続ける（読み捨てでよい）。
5. 両側が `Close`（`closesocket`）を呼ぶ。

第 59 章（サーバー）と第 61 章（閉じ方）のコードが、この順序で書かれています。

### Linger

`closesocket` の挙動を決めるのが `SO_LINGER` です。Microsoft Learn によると既定は、`closesocket` がすぐ戻り閉じる手順をバックグラウンドで進める動作です。そのかわりアプリは手順が実際に終わるのかいつ終わるのかを知る方法がありません。`SO_LINGER` を設定すると待つ時間を指定する（待ち切れなければ、`RST` による強制終了に切り替わる）こともすぐ強制終了させる（時間 0）こともできます。

時間 0 の `SO_LINGER` は `RST` を意図的に送る方法として使えます。ただし、未送信のデータが消えるので通常のコードでは使わないでください。


## 状態の一覧

TCP の接続はここまでに出てきた状態を行き来します。`netstat` の表示といつその状態になるかの索引です。詳しい遷移は RFC 9293 の Figure 5 にあります。

| 状態 | いつ見えるか |
| --- | --- |
| `LISTEN` | `listen` した待ち受け側 |
| `SYN_SENT` | `connect` して `SYN` を送った直後（返事待ち） |
| `SYN_RECEIVED` | `SYN` を受け取って、`SYN + ACK` を返した直後 |
| `ESTABLISHED` | 接続が確立した。データを送れる |
| `FIN_WAIT_1` | 自分が `FIN` を送って、その ACK を待つ |
| `FIN_WAIT_2` | 自分の `FIN` が ACK された。相手の `FIN` を待つ |
| `CLOSE_WAIT` | 相手の `FIN` を受け取った。自分がまだ閉じていない |
| `CLOSING` | 両側が同時に `FIN` を送った（同時クローズ） |
| `LAST_ACK` | 相手の `FIN` のあと自分も `FIN` を送って、ACK 待ち |
| `TIME_WAIT` | 最後の ACK を送ったあと 2 × MSL の間待つ |

`CLOSED` は状態が存在しないことを表す架空の状態です。`netstat` には出ません。

`SYN_RECEIVED` と `SYN_SENT`、`CLOSING` はループバックでも瞬間的に通り過ぎるだけなので、`netstat` で見ることはまずありません。見えたら何かが詰まっています。


## ポートとアドレス

### 127.0.0.1 と 0.0.0.0

待ち受けるアドレスの指定で見える範囲が変わります。

```text title="待ち受けのアドレスによる、netstat の表示の違い（実測）"
Any: TCP    0.0.0.0:54948          0.0.0.0:0              LISTENING       11392
Loopback: TCP    127.0.0.1:54949        0.0.0.0:0              LISTENING       11392
```

`IPAddress.Loopback`（`127.0.0.1`）で待ち受ければ同じ PC の中からしか繋げません。`IPAddress.Any`（`0.0.0.0`）ならこの PC のすべてのネットワーク インターフェイスで待ち受けるので、LAN の別の PC からも繋がる可能性があります。<strong>エンジンの待ち受けに `IPAddress.Any` を使うのは、LAN に開く作りになるため、絶対に避けます</strong>。この章の前提（localhost）では、常に `127.0.0.1` にします。

`localhost` という名前を使うことはおすすめしません。名前は `127.0.0.1`（IPv4）と `::1`（IPv6）のどちらにも解決されうるからです。待ち受けが IPv4 の `127.0.0.1` だけなら数字で書いたほうが確実です。

### ポート 0 と、固定のポート

ポート番号を決める方法は 2 通りあります。

1 つはポート 0 で待ち受けて、OS に選ばせる方法です（ここまでの実験で使ってきた方法です）。衝突しませんが繋ぐ側が選ばれた番号を知る手段が要ります。第 59 章ではエンジンが標準出力に `port=NNNN` と書いて、エディタが読みます。

もう 1 つは決まった番号を使う方法です。繋ぐ側が番号を知っているので簡単ですが、その番号が使われていると失敗します。

```csharp title="同じポートで 2 つ目の listen"
{
    var l1 = new TcpListener(IPAddress.Loopback, 0); l1.Start(); int port = ((IPEndPoint)l1.LocalEndpoint).Port;
    try { var l2 = new TcpListener(IPAddress.Loopback, port); l2.Start(); Console.WriteLine("[4] 2 つ目の listen 成功(!)"); }
    catch (SocketException e) { Console.WriteLine($"[4] 同じポートで 2 つ目の listen -> {e.SocketErrorCode} ({e.NativeErrorCode})"); }
    l1.Stop();
}
```

```text title="実行結果（実測）"
[4] 同じポートで 2 つ目の listen -> AddressAlreadyInUse (10048)
```

エンジンを二重に起動したときや前のエンジンが生きていたときにこの `AddressAlreadyInUse` になります。この失敗は「すでにエンジンが動いている」という有用な知らせでもあります。

### SO_REUSEADDR と SO_EXCLUSIVEADDRUSE

Windows のソケットには「同じアドレスとポートに複数のソケットを束縛できるようにする」オプション `SO_REUSEADDR` があります。Microsoft Learn には `SO_REUSEADDR` が、すでに使われているアドレスとポートへの束縛を許すこと `SO_EXCLUSIVEADDRUSE` が、それを防げることが書かれています。

手元で先に `TcpListener` が待ち受けているポートに `ReuseAddress` を付けた別のソケットで、`Bind` してみました。

```text title="実行結果（実測）"
ReuseAddress の 2 つ目: AccessDenied
Exclusive 側に ReuseAddress で bind: AccessDenied
TcpListener 既定の ExclusiveAddressUse = False
```

どちらも `AccessDenied` で割り込みはできませんでした。ただ、`TcpListener` の既定は `ExclusiveAddressUse = False` でした。他のプログラムの割り込みを確実に防ぎたいなら `ExclusiveAddressUse = true` を自分で設定してください（C++ では、`bind` の前に `SO_EXCLUSIVEADDRUSE`。第 61 章のコードで使っています）。この設定は `bind` の前に必要です。


## エラーの索引

ここまでに実測で出てきたソケットのエラーです。例外を見て何が起きたのかを引くための索引です。

| .NET の `SocketError` | Windows の番号 | 実測で出た場面 |
| --- | --- | --- |
| `AddressAlreadyInUse` | 10048 | 使用中のポートで `listen` |
| `ConnectionRefused` | 10061 | 待ち受けのないポートへ `connect`（約 2 秒後） |
| `ConnectionReset` | 10054 | 相手が `RST` を送った（未読で `Close`、プロセスの死） |
| `ConnectionAborted` | 10053 | 閉じた相手へ 2 回目の `Write` |
| `AccessDenied` | 10013 | `ReuseAddress` で使用中のポートに `Bind` |

`ConnectionReset` と `ConnectionAborted` の使い分けは Winsock の一般的な説明では、`ConnectionReset` が「相手が接続を強制終了した」、`ConnectionAborted` が「こちらの側のソフトウェアが接続を中断した」です（この章では、Microsoft Learn の該当ページを読んでいません）。どちらも、接続を使い続けられないという点では同じです。`IOException` の `InnerException` から `SocketException` を取り出して、`SocketErrorCode` を見ます。


## パイプとの比較

同じ PC の中の通信として、名前付きパイプと TCP（`127.0.0.1`）を並べます。往復の時間は 1 バイトを送って、1 バイトの返事をもらうのを同じ PC で繰り返して測った平均です。

| 観点 | 名前付きパイプ | TCP（127.0.0.1） |
| --- | --- | --- |
| 1 バイト往復（実測） | 27.8 μs | 25.2 μs |
| 他の OS | 使えない | 使える |
| 他の言語・ツール | ライブラリ次第 | ほぼ何でも繋げる |
| 繋げる相手 | ACL で絞れる | 同じ PC の誰でも |
| 作法 | 長さ付きフレーム | 長さ付きフレーム＋合言葉 |

往復の時間はほぼ同じ（誤差の範囲）です。性能が理由ならどちらを選んでもかまいません。TCP を選ぶ理由は他のツール（Python のスクリプトやテスト用のプログラムなど）が、繋ぎやすいことです。パイプを選ぶ理由は相手を絞れることです。

TCP の他の数字も実測で並べておきます。

- 接続して合言葉の握手を終えるまで：約 20 ミリ秒（最初の 1 回は、`.NET` の初期化などを含む）
- 5 MiB のメッセージを送って、同じ大きさの返事を受け取るまで：約 14 ミリ秒
- 一方向の連続転送：約 1615 MiB/s（400 MiB を送り続けた平均）
- 長さ付きフレームの 1 バイト往復（C++ サーバー相手、`ReadExactly` 含む）：約 65 マイクロ秒

最後の値が生のソケットの 25 マイクロ秒より大きいのは、5 バイトのフレームの組み立て、配列の確保、`async`/`await` のオーバーヘッドの分です。1 フレームの描画（約 16.7 ミリ秒）に比べれば、十分小さい値です。


## 手元で状態を見る道具

接続の状態を調べる方法を 3 つ挙げます。

`netstat -ano -p tcp` はこの章で何度も使ってきました。`-a` が全接続、`-n` が数字のまま表示、`-o` が持ち主のプロセスの ID（PID）の表示です。出力が多いのでポート番号で絞ります。

```powershell
netstat -ano -p tcp | Select-String ":54941 "
```

PowerShell の `Get-NetTCPConnection` は同じ情報をオブジェクトで返します。

```powershell
Get-NetTCPConnection -LocalAddress 127.0.0.1 -State Established, Listen, TimeWait, CloseWait |
    Select-Object LocalPort, RemotePort, State, OwningProcess
```

`Test-NetConnection` は「そのポートに繋がるか」を確かめます。

```powershell
Test-NetConnection -ComputerName 127.0.0.1 -Port 54941
```

エンジンが落ちたかどうかの調査では `CLOSE_WAIT` が増え続けていないか `LISTEN` のポートが残っていないかを、最初に見ます。パケットの中身まで見たい場合はパケットキャプチャのツールを使う方法もありますが、この章では使っていません。


## よくあるミス

??? failure "Read の戻り値をそのまま 1 メッセージの長さだと思う"
    何が起きるか：`Read` が 3 バイトだけ返したのに、ヘッダーの 4 バイトを読み終えたつもりで進み長さの値が壊れます。メッセージの境界がずれて以降のメッセージがすべて壊れます。

    対処：長さも本文も `ReadExactly`（C++ は `RecvExact`）のように揃うまで読み続ける関数で読みます。

??? failure "ヘッダーと本文を別々に Write する"
    何が起きるか：小さな `Write` が 2 つ続くため、Nagle と遅延 ACK の待ち合わせが起こりえます。手元のループバックでは再現しませんでしたが、環境によっては往復が数十ミリ秒に伸びます。

    対処：1 つの配列にまとめて、1 回で `Write` します。あわせて `NoDelay` を有効にします。

??? failure "両側が書いたまま読むループがない"
    何が起きるか：両方の `Write` が止まって、動かなくなります。エラーも例外も出ません。実測で 1 秒間、1 バイトも進まなくなりました。

    対処：読むループは書く処理とは別のタスクで、常に回します。

??? failure "Close する前に読み残しがある"
    何が起きるか：相手の `Read` に `0`（EOF）ではなく、`ConnectionReset` が届きます。送った返事の末尾が消えることもあります。

    対処：`Shutdown(Send)` を呼んで相手が閉じる（`Read` が 0）まで読み捨ててから、`Close` します。

??? failure "Read が 0 を返したのに、ループを続ける"
    何が起きるか：`Read` が 0 を即座に返し続けて、CPU を使い切る無限ループになります。

    対処：`Read` が 0 なら相手が `FIN` を送った印です。ループを抜けて自分も閉じます。`CLOSE_WAIT` が残るのもこの見逃しが原因です。

??? failure "エンジンが起動する前に connect を繰り返す"
    何が起きるか：待ち受けがないポートへの `connect` は、手元で約 2 秒かかって失敗します。ポーリングの間隔を 100 ミリ秒にしたつもりでも実際は 1 回 2 秒です。

    対処：エンジンを起動したエディタが、エンジンの出力で「待ち受けを開始した」ことを知ってから繋ぎます。繋ぎにいくときは時間切れを付けます。

??? failure "待ち受けに IPAddress.Any を使う"
    何が起きるか：エンジンの入り口が、LAN の他の PC にも開きます。合言葉がなければ誰でも命令を送れます。

    対処：`IPAddress.Loopback`（`127.0.0.1`）にします。さらに、合言葉を確認します（第 61 章）。

??? failure "Write が成功したので、相手に届いたと思う"
    何が起きるか：相手がすでに閉じていても、1 回目の `Write` は成功します（実測）。命令が実行されたと思い込んで、画面だけ更新するとエンジンとエディタの状態がずれます。

    対処：実行を確かめたい命令には、返事（ACK のようなアプリのレベルの確認）を要求します。第 54 章の要求と返事の対応が、この役です。


## これだけ覚える

- TCP はバイトの流れ。メッセージの切れ目は自分で作る（長さ付きフレーム）。揃うまで読み続ける。
- `Write` の成功はバッファに入っただけ。届いたことの保証ではない。
- 受け取る側が読まないと数百 KiB で `Write` が止まる。読むループは書く処理と別に常に回す。
- 1 メッセージは 1 回の `Write` で書く。`NoDelay` を有効にする。
- `Read` が 0 なら相手の `FIN`。自分も閉じる。未読のまま `Close` すると相手に `ConnectionReset` が届く。
- `127.0.0.1` でだけ待ち受ける。ポートは 0 で OS に選ばせ `ExclusiveAddressUse` を設定する。
- 待ち受けのないポートへの `connect` は、手元で約 2 秒かかる。「拒否」と「時間切れ」は別の失敗として扱う。
- プロセスの死はほぼ即座に分かる（約 3 ミリ秒）。固まりは分からない。


## 参考資料

読んだ範囲と読んでいない範囲を分けて書きます。

### 読んだもの

- W. Eddy (Ed.), *Transmission Control Protocol (TCP)*, RFC 9293, 2022 年 8 月（<https://www.rfc-editor.org/rfc/rfc9293.html>）。§3.1（ヘッダー）、§3.3.2（状態遷移）、§3.4（シーケンス番号、ISN、MSL）、§3.5（接続の確立、リセット）、§3.6（切断、TIME-WAIT）、§3.7（セグメント化、Nagle）、§3.8（再送、輻輳制御、キープ アライブ、ウィンドウ管理、遅延 ACK）、§3.9（ユーザー インターフェイス）、§3.10.7〜3.10.8 を読みました。末尾の約 5 万字（付録と索引にあたる部分）は読んでいません。
- J. Nagle, *Congestion Control in IP/TCP Internetworks*, RFC 896, 1984 年 1 月（<https://www.rfc-editor.org/rfc/rfc896.txt>）。全体を読みました。
- V. Paxson, M. Allman, J. Chu, M. Sargent, *Computing TCP's Retransmission Timer*, RFC 6298, 2011 年 6 月（<https://www.rfc-editor.org/rfc/rfc6298.txt>）。全体を読みました。
- M. Allman, V. Paxson, E. Blanton, *TCP Congestion Control*, RFC 5681, 2009 年 9 月（<https://www.rfc-editor.org/rfc/rfc5681.txt>）。§3（スロー スタート、輻輳回避、高速再送、高速回復）、§4.1（アイドル後の再開）、§4.2（遅延 ACK）を読みました。
- Microsoft Learn「Use TcpClient and TcpListener」（.NET）、「Getting started with Winsock」、「SOL_SOCKET Socket Options」、「IPPROTO_TCP socket options」、「Graceful Shutdown, Linger Options, and Socket Closure」（Win32）

### 読んでいないもの

- RFC 7323（ウィンドウ スケール、タイムスタンプ）、RFC 6928（IW を 10 にする提案）、CUBIC の資料、SACK（RFC 2018）、RFC 5961（リセット攻撃への対策）。この章では名前だけに触れています。
- Windows の TCP 実装そのものの資料。Windows の `TIME_WAIT` の長さや接続拒否のあとの再試行の仕組みは、確かめていません。

### 実験について

実験のコードはこの章に載せたものです。C# は .NET 10 で、C++ は MSVC で実際にコンパイルして動かしました。値は 1 台の PC の結果です。


## 関連ページ

- [第 59 章 TCP 編 1：最小のエンジンとエディタを繋ぐ](59-tcp-base.md)（この章の知識で、接続を作る）
- [第 60 章 TCP 編 2：Prest のエディタに組み込む](60-tcp-editor.md)（エンジンの起動と `IEngineService` の差し替え）
- [第 61 章 TCP 編 3：安全で壊れにくくする](61-tcp-hardening.md)（合言葉、ハートビート、行儀のよい終了、テスト）
- [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)
- [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)
- [第 57 章 落ちたら立て直す](57-recovery.md)

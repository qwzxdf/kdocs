---
title: 第 59 章 TCP 編 1：最小のエンジンとエディタを繋ぐ
tags:
  - C#連携
  - TCP
---

# 第 59 章 TCP 編 1：最小のエンジンとエディタを繋ぐ

エンジンを別のプロセスに分けたら、エディタとエンジンは何かで話さなければなりません。第 53 章では、その候補として名前付きパイプと TCP を比べました。この章からは TCP を選んで、<strong>エンジンの exe とエディタが実際に会話するところまで</strong>を、最小の形で作ります。

作るものは 2 つです。1 つは C++ の小さなサーバーで、`127.0.0.1` のポートで待ち受けて、命令を 1 つ受け取るたびに返事を 1 つ返します。もう 1 つは C# のクライアントで、命令を送って返事を `await` で待ちます。複数の命令を同時に送っても、返事を取り違えません。

エンジンの中身（描画やシーン）は、この章には出てきません。命令は `ping`（生きているかの確認）と `add`（足し算）の 2 つだけです。中身を空にしてあるのは、<strong>通信の部分だけを先に完成させる</strong>ためです。

この章は、手を動かす順に進めます。TCP の性質は、コードに必要になった所で、短く挟みます。詳しい仕組み（ウィンドウ、再送、切断の状態など）は第 62 章にまとめてあるので、先に読まなくても進めます。合言葉による守りや、エンジンが固まったときの見つけ方も、動くものができたあとの第 61 章で扱います。

!!! info "このページを読む前に"
    - [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)（なぜ分けるのか、通信路の比較）
    - [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)（任意。`IEngineService` を通信越しにする考え方）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）

!!! abstract "この章で作るもの"
    - `TcpServer.cpp`（C++）：Winsock のサーバー。長さ付きの JSON を読んで、返事を書く
    - `Framing.cs`、`TcpTransport.cs`、`IEngineTransport.cs`（C#）：長さ付きメッセージと TCP の接続
    - `EngineClient.cs`（C#）：要求を送って、返事を `id` で待つ
    - `Program.cs`（C#）：エンジンを起動して、命令を送る確認用のコンソール アプリ

## なぜ TCP で繋ぐのか

名前付きパイプでも、同じことはできます。それでも TCP を選ぶのは、<strong>エディタ以外のプログラムが、エンジンに繋ぎやすくなる</strong>からです。Python のテスト スクリプトや、第 58 章の MCP を橋渡しするプログラムは、ソケットならほぼどの言語からでも標準の機能だけで繋がります。

もう 1 つは、接続先の決め方が単純になることです。名前付きパイプは、名前の衝突を避けるために世代番号を付けるなどの工夫が要ります。TCP はポート 0 で待ち受ければ、OS が空いている番号を選んでくれます。

性能は理由になりません。第 62 章で測ったとおり、同じ PC の中ではパイプと TCP の往復の時間はほぼ同じです。

## 1. メッセージの形を決める

最初に決めるのは、エディタとエンジンが交わす「1 通のメッセージ」の形です。

TCP は、バイトの流れを運ぶだけの仕組みです。たとえば 10 バイトと 20 バイトを続けて `Write` しても、受け取る側の `Read` が 10 バイトと 20 バイトに分かれて返るとは限りません。30 バイトが 1 回で返ることも、5 バイトずつ細切れに返ることもあります。送った単位は、相手に届くときには残っていません。

そこで、メッセージの切れ目は、アプリの側で決めます。この教材では、本文の長さを先頭に付ける方法にします。

<svg class="fig flow" viewBox="0 0 720 262" role="img" aria-label="メッセージは 4 バイトの長さと JSON の本文でできている。要求と返事は id で対応づける"><defs><marker id="tbB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">1 つのメッセージと、要求・返事の対応</text><rect x="16" y="38" width="110" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="71" y="60" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">長さ N（4 バイト）</text><rect x="126" y="38" width="430" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="341" y="60" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">本文 N バイト（UTF-8 の JSON）</text><text x="570" y="55" style="font-size:12px;font-weight:400">先に長さを読めば、</text><text x="570" y="73" style="font-size:12px;font-weight:400">どこまでが 1 つか分かる</text><text x="100" y="124" text-anchor="middle" style="font-size:13px;font-weight:600">エディタ（C#）</text><text x="620" y="124" text-anchor="middle" style="font-size:13px;font-weight:600">エンジン（C++）</text><line x1="100" y1="134" x2="100" y2="248" stroke="#94a3b8" stroke-width="2"/><line x1="620" y1="134" x2="620" y2="248" stroke="#94a3b8" stroke-width="2"/><line x1="100" y1="152" x2="620" y2="164" stroke="currentColor" stroke-width="2" marker-end="url(#tbB)"/><text x="360" y="150" text-anchor="middle" style="font-size:12px;font-weight:400">id=1  add</text><line x1="100" y1="180" x2="620" y2="192" stroke="currentColor" stroke-width="2" marker-end="url(#tbB)"/><text x="360" y="178" text-anchor="middle" style="font-size:12px;font-weight:400">id=2  ping</text><line x1="620" y1="206" x2="100" y2="218" stroke="currentColor" stroke-width="2" marker-end="url(#tbB)"/><text x="360" y="204" text-anchor="middle" style="font-size:12px;font-weight:400">id=1  ok</text><line x1="620" y1="232" x2="100" y2="244" stroke="currentColor" stroke-width="2" marker-end="url(#tbB)"/><text x="360" y="230" text-anchor="middle" style="font-size:12px;font-weight:400">id=2  ok</text></svg>

長さは 4 バイトの整数（リトル エンディアン）にします。x64 の Windows の C++ も、C# の `BinaryPrimitives` も、そのまま読み書きできます。長さの上限は 16 MiB と決めます。壊れたデータの先頭 4 バイトを長さとして信じて、巨大なメモリを確保してしまわないための上限です。

本文の JSON は、要求と返事で次の形にします。

```json
{"id": 7, "cmd": "add", "args": {"a": 20, "b": 22}}
{"id": 7, "ok": true, "result": 42}
{"id": 8, "ok": false, "error": "unknown command: foo"}
```

要求の `id` は、クライアントが決める通し番号です。返事には同じ `id` を入れて返します。これで、返事が来た順番を気にせずに、どの要求への返事かを突き合わせられます。返事を待たずに次の要求を送れるので、待っている間も UI が止まりません。

`ok` が `false` のときは、`error` に理由を入れます。これは<strong>エンジンが「失敗です」と答えた</strong>場合で、接続は生きています。エンジンが消えて接続が切れた場合とは、別の失敗です。クライアントは前者を `EngineCommandException`、後者を `EngineDisconnectedException` として、別の例外にします。

## 2. エンジン側：Winsock のサーバー

C++ のサーバーから作ります。この章のサーバーは、次の方針にします。

- `127.0.0.1` だけで待ち受ける。`0.0.0.0` にすると、LAN の他の PC からも繋がる入り口になってしまう
- ポートは 0 にして、OS に空いている番号を選ばせる。選ばれた番号は、エンジンが標準出力に `port=NNNN` と書いて、エディタに知らせる
- 繋ぐのは 1 人のエディタだけ。そのエディタが閉じたら、エンジンも終わる

起動から終了までの流れは、次のとおりです。

<svg class="fig flow" viewBox="0 0 720 330" role="img" aria-label="エディタがエンジンを起動し、エンジンが 127.0.0.1 のポート 0 で待ち受けて標準出力にポート番号を書き、エディタが接続して要求と返事をやり取りし、エディタが閉じるとエンジンも終わる"><defs><marker id="teA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">起動から終了まで（番号の順に進む）</text><text x="110" y="50" text-anchor="middle" style="font-size:13px;font-weight:600">エディタ</text><text x="610" y="50" text-anchor="middle" style="font-size:13px;font-weight:600">エンジン</text><line x1="110" y1="60" x2="110" y2="318" stroke="#94a3b8" stroke-width="2"/><line x1="610" y1="60" x2="610" y2="318" stroke="#94a3b8" stroke-width="2"/><line x1="110" y1="80" x2="610" y2="80" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="74" text-anchor="middle" style="font-size:12px;font-weight:600">① プロセスを起動</text><rect x="470" y="94" width="236" height="30" rx="8" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="588" y="109" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">127.0.0.1 のポート 0 で listen</text><line x1="610" y1="154" x2="110" y2="154" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="148" text-anchor="middle" style="font-size:12px;font-weight:600">② 標準出力：port=NNNN</text><line x1="110" y1="190" x2="610" y2="190" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="184" text-anchor="middle" style="font-size:12px;font-weight:600">③ connect</text><rect x="14" y="204" width="196" height="30" rx="8" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="112" y="219" text-anchor="middle" dominant-baseline="central" style="font-size:11px;font-weight:600">要求と返事（EngineClient）</text><line x1="110" y1="264" x2="610" y2="264" stroke="currentColor" stroke-width="2" marker-end="url(#teA)"/><text x="360" y="258" text-anchor="middle" style="font-size:12px;font-weight:600">④ エディタが接続を閉じる</text><text x="360" y="304" text-anchor="middle" style="font-size:12px">⑤ エンジンの読み取りが終わり、終了コード 0 で終わる。</text></svg>

②でエディタは、エンジンの標準出力を読んで待つだけです。`connect` は番号が分かってから、1 回だけ呼びます。

C++ はヘッダーと、道具になる小さなクラスから始めます。

```cpp title="EngineHost/TcpServer.cpp（新規）"
#include <winsock2.h>   // Winsock 本体。windows.h より先に include する
#include <ws2tcpip.h>   // inet_pton など

#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <functional>
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

`winsock2.h` は `windows.h` より先に include します。順序を逆にすると、古い `winsock.h` が先に取り込まれて、定義が衝突します。

`WSAStartup` は、Winsock を使う前に必ず 1 回呼ぶ関数です。呼び忘れると、すべてのソケット関数が失敗します。Microsoft Learn は、これを RAII のクラスで `WSACleanup` と対にして、どの出口でも後片付けが走るようにすることを勧めています。

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

`SOCKET` はただの整数のハンドルなので、`closesocket` を呼び忘れると漏れます。`unique_ptr` のように持ち主が 1 人になるクラスで包んで、スコープを出るときに必ず閉じるようにします。

次が待ち受けです。

```cpp title="EngineHost/TcpServer.cpp（続き：待ち受け）"
// ---- 待ち受け: 127.0.0.1 だけ。ポートは 0（OS におまかせ）にもできる ----
Socket ListenLoopback(uint16_t port, uint16_t* bound_port) {
  Socket s(socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
  if (!s.valid()) return {};

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

呼ぶ順番は、`socket`（作る）→ `bind`（アドレスとポートに結びつける）→ `listen`（待ち受けを始める）です。`htons` と `ntohs` は、ポート番号を手元の並びとネットワーク バイト オーダー（ビッグ エンディアン）の間で変換します。この章の「長さ付きメッセージ」の長さはリトル エンディアンなので、2 つが別の約束であることに注意してください。

`inet_pton` で、文字列の `127.0.0.1` をアドレスの構造体に変換します。ここで `INADDR_ANY` を渡すと、LAN に開いてしまいます。この 1 行が、守りの最初の一歩です。ポートを 0 にして `bind` すると、OS が空いている番号を選びます。それを `getsockname` で聞き出して、`bound_port` に返します。固定の番号にしない理由は、前回のエンジンが残っていたり二重に起動したりしたときに、`bind` が失敗するからです。

次は、読み書きの道具です。

```cpp title="EngineHost/TcpServer.cpp（続き：確実に読み書きする）"
// ---- ちょうど size バイト受け取る。TCP は流れなので、recv は少なく返ることがある ----
bool RecvExact(SOCKET s, void* buffer, int size) {
  auto* p = static_cast<char*>(buffer);
  while (size > 0) {
    const int n = recv(s, p, size, 0);
    if (n <= 0) return false;            // 0 = 相手が閉じた（FIN）。負 = エラー。どちらも、続けられない
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

`recv` は、欲しいバイト数より少なく返ることがあります。先ほど見た「送った単位は残らない」の、受け取る側の姿です。そのため、必要なバイト数が揃うまで、ループで読み続けます。`recv` が 0 を返すのは、相手が接続を閉じたときです。`send` も同じで、一部だけ送って戻ることがあるので、戻り値の分だけ進めながら、全部送り切るまで続けます。

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
  // 長さと本文を 1 回の send にまとめる
  std::vector<char> frame(sizeof(uint32_t) + body.size());
  const auto length = static_cast<uint32_t>(body.size());
  std::memcpy(frame.data(), &length, sizeof(length));
  std::memcpy(frame.data() + sizeof(length), body.data(), body.size());
  return SendAll(s, frame.data(), static_cast<int>(frame.size()));
}
```

`ReadMessage` は、先に 4 バイトの長さを読んで、その長さの分だけ本文を読みます。`WriteMessage` が長さと本文を 1 つの配列にまとめて、1 回の `send` で送っているのには理由があります。小さな送信を 2 回に分けると、TCP の Nagle アルゴリズムと、受け取る側の遅延 ACK が重なって、返事が数十ミリ秒遅れることがあります。この仕組みは第 62 章で詳しく見ます。

最後が、1 人のエディタの相手をする `ServeOnce` と、命令の振り分けです。

```cpp title="EngineHost/TcpServer.cpp（続き：待ち受けて、1 人の相手をする）"
// ---- エディタが 1 人繋ぐまで待ち、繋がったら、その 1 人の相手をする ----
// 戻り値: false = 待ち受けを始められなかった
bool ServeOnce(const std::function<std::string(const std::string&)>& handler) {
  uint16_t port = 0;
  Socket listener = ListenLoopback(0, &port);
  if (!listener.valid()) return false;
  std::printf("port=%u\n", port);   // エディタが、この 1 行を読んで接続先を知る
  std::fflush(stdout);

  Socket client(accept(listener.get(), nullptr, nullptr));
  if (!client.valid()) return false;

  // 小さい要求と返事を、すぐ送る（Nagle アルゴリズムを切る）
  const BOOL no_delay = TRUE;
  setsockopt(client.get(), IPPROTO_TCP, TCP_NODELAY,
             reinterpret_cast<const char*>(&no_delay), sizeof(no_delay));

  std::string request;
  while (ReadMessage(client.get(), request)) {      // エディタが閉じると false になって、ループを抜ける
    if (!WriteMessage(client.get(), handler(request))) break;
  }
  return true;                                      // 1 人終わったら、エンジンも終わる
}  // client と listener のデストラクタが closesocket
```

`std::printf("port=%u\n", port)` と `fflush` が、エディタへの合図です。標準出力はパイプに繋がれていると、バッファされてすぐには流れません。`fflush` を忘れると、エディタがポートの通知を待ち続けます。標準出力はポートの通知だけに使って、ログは標準エラーに書いてください。

`accept` は、エディタが繋いでくるまでここで止まります。繋がったら `TCP_NODELAY` を設定して、小さなメッセージを溜めずにすぐ送るようにします。あとは、`ReadMessage` で要求を 1 つ読み、`handler` で返事を作り、`WriteMessage` で返すことを、エディタが閉じるまで繰り返すだけです。

次が、命令の振り分けです。要求 1 つにつき、返事を 1 つ作ります。返事には、要求の `id` をそのまま写します。

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
  WinsockSession wsa;
  if (!wsa.ok()) return 1;
  return ServeOnce(Dispatch) ? 0 : 2;    // 2 = 待ち受けを始められなかった
}
```

`ping` は生きているかの確認で、`pong` と返します。`add` は引数（`args` の `a` と `b`）を使う命令の例です。どちらでもない命令には、`ok: false` と理由の `error` を返します。接続は生きたままで、クライアントでは `EngineCommandException` になります。

`FindString` と `FindNumber` は、文字列から `"cmd"` と数字を拾うだけの、確認用の読み方です。本物のエンジンでは、JSON ライブラリ（nlohmann など）で読んで、命令の名前から処理への表を引きます。命令を足すときは、`if (cmd == "...")` を増やすか、表に登録するだけです。

`Dispatch` の中身を自分のエンジンの処理に替えれば、通信の部分はそのまま使えます。

### ビルドする

Visual Studio の「Developer PowerShell」（または x64 の開発者コマンド プロンプト）で、コンパイルします。

```powershell
cl /std:c++latest /EHsc /W4 /utf-8 TcpServer.cpp
```

`/utf-8` はソースの文字コードを UTF-8 と見なす指定で、日本語のコメントのために必要です。付けないと、既定の Shift_JIS 系のコード ページとして読まれて、コンパイルが失敗します。できた `TcpServer.exe` を、次の C# のプログラムから起動します。

## 3. エディタ側：EngineClient

C# 側の中心は、`EngineClient` です。命令を送って、返事を待つ役目を持ちます。TCP の細かいこと（ソケット、接続）は、`Stream` を作る部分に分けておいて、`EngineClient` は `Stream` だけを知る作りにします。

まず、`Stream` を作る窓口です。

```csharp title="Editor/Engine/IEngineTransport.cs（新規）"
namespace Editor.Engine;

// 「どうやって Stream を作るか」だけを差し替える窓口。EngineClient は、この先を知らない
public interface IEngineTransport
{
    // 時間内に繋がらなければ TimeoutException
    Task<Stream> ConnectAsync(TimeSpan timeout, CancellationToken ct = default);
}
```

窓口が 1 つのメソッドだけなのは、通信路を差し替えられるようにするためです。この章では TCP 版を 1 つ作ります。名前付きパイプ版や、テスト用の偽の通信路に替えるときも、`EngineClient` は変わりません（第 61 章）。

次に、長さ付きメッセージの読み書きです。C++ の `ReadMessage` と `WriteMessage` の、C# 版にあたります。

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
        await s.WriteAsync(frame, ct).ConfigureAwait(false);             // 1 回の Write
        await s.FlushAsync(ct).ConfigureAwait(false);
    }

    public static async ValueTask<byte[]> ReadFrameAsync(Stream s, CancellationToken ct = default)
    {
        var header = new byte[4];
        await s.ReadExactlyAsync(header, ct).ConfigureAwait(false);      // 4 バイト揃うまで待つ
        int length = BinaryPrimitives.ReadInt32LittleEndian(header);
        // 壊れた長さを信じて、巨大な配列を確保しない
        if (length < 0 || length > MaxMessageSize) throw new InvalidDataException($"不正なメッセージ長: {length}");
        var body = new byte[length];
        await s.ReadExactlyAsync(body, ct).ConfigureAwait(false);        // 本文も、揃うまで読み続ける
        return body;
    }
}
```

`ReadExactlyAsync` は、指定したバイト数が揃うまで待つメソッドです。C++ の `RecvExact` と同じ役目で、細切れに届く TCP から、長さも本文も正しく取り出します。相手が閉じれば `EndOfStreamException`（`IOException` の仲間）を投げます。

次が TCP の窓口です。

```csharp title="Editor/Engine/TcpTransport.cs（新規）"
using System.Net;
using System.Net.Sockets;

namespace Editor.Engine;

public sealed class TcpTransport(int port) : IEngineTransport
{
    public async Task<Stream> ConnectAsync(TimeSpan timeout, CancellationToken ct = default)
    {
        var socket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp)
        {
            NoDelay = true,          // 小さな要求を、Nagle で溜めずにすぐ送る
        };

        using var cts = CancellationTokenSource.CreateLinkedTokenSource(ct);
        cts.CancelAfter(timeout);
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

        return new NetworkStream(socket, ownsSocket: true);   // 繋がったあとに作る。Dispose すると socket も閉じる
    }
}
```

接続先は `IPAddress.Loopback`（`127.0.0.1`）です。`localhost` という名前は使いません。名前だと、IPv6 の `::1` を先に試して、待ち受けのない所で時間を取られることがあります。`NoDelay = true` は、サーバーと同じく Nagle を切る設定です。

`OperationCanceledException` が出て、しかも呼び出し側の `ct` が取り消されていないなら、時間切れです。`TimeoutException` に翻訳します。接続の拒否は `SocketException`（`ConnectionRefused`）のまま、上に伝えます。どちらの場合も、ソケットはここで破棄します。

最後の `return` で作る `NetworkStream` は、必ず `ConnectAsync` が成功したあとに作ります。繋がる前のソケットを渡すと、`IOException`（「非接続のソケットでは、この操作は許可されません」）になります。

いよいよ `EngineClient` です。ファイルの先頭と、2 つの例外から始めます。

```csharp title="Editor/Engine/EngineClient.cs（新規）"
using System.Collections.Concurrent;
using System.Text.Json;

namespace Editor.Engine;

// エンジンが落ちた（接続が切れた）ことを表す例外
public sealed class EngineDisconnectedException : IOException
{
    public EngineDisconnectedException() : base("エンジンとの接続が切れました。") { }
}

// エンジンが「失敗」を返したことを表す例外（接続は生きている）
public sealed class EngineCommandException(string message) : Exception(message);
```

失敗を 2 つの例外に分けているのが、設計の要です。`EngineCommandException` は、エンジンが「その操作はできません」と答えた場合で、画面にメッセージを出せば済みます。`EngineDisconnectedException` は、エンジンのプロセスが消えた場合で、再接続や復旧の合図です。両方を同じ `Exception` で受けると、「単なる失敗」と「相手が消えた」を見分けられません。

```csharp title="Editor/Engine/EngineClient.cs（続き：フィールドと接続）"
public sealed class EngineClient : IAsyncDisposable
{
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
        _stream = await _transport.ConnectAsync(TimeSpan.FromMilliseconds(timeoutMs)).ConfigureAwait(false);
        _readLoop = Task.Run(ReadLoopAsync);     // 返事を読むループを、別のタスクで回す
    }
```

`_pending` は「返事待ちの表」です。キーが要求の `id`、値が `TaskCompletionSource` で、これは「あとで結果を入れられる `Task`」を作る道具です。呼び出し側はこの `Task` を `await` します。返事を読むループが結果を入れた瞬間に、続きが動き出します。複数のスレッドから触るので、`ConcurrentDictionary` を使います。

`ConnectAsync` は、窓口から `Stream` を受け取って、<strong>返事を読むループを別のタスクで回し始めます</strong>。読むループを書く処理と別に回しておかないと、両側が書き合ったときに、どちらも読めずに動けなくなる危険があるからです（第 62 章「フロー制御」）。

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

`Interlocked.Increment` は、複数のスレッドが同時に呼んでも重ならない番号を振ります。各 `await` の後ろの `.ConfigureAwait(false)` は、「続きを元のスレッドに戻さなくてよい」という指定です。WPF の UI スレッドには、続きを UI スレッドで動かす仕組み（同期コンテキスト）があります。この指定がないと、UI スレッドから `RequestAsync(...).Result` のように待った瞬間に、続きが UI スレッドの空きを待ち、UI スレッドは結果を待つという行き違いで固まります。通信のような部品の中では、付けておくのが決まりです。

`TaskCreationOptions.RunContinuationsAsynchronously` は、返事を読むループが `TrySetResult` した瞬間に、`await` の続きがそのスレッドで同期的に走ってしまうのを避ける指定です。これを付けないと、返事を読むループの中で呼び出し側の処理が動いてしまい、次の返事の読み取りが遅れます。

時間切れは、`CancellationTokenSource` に制限時間を渡して、時間が来たら `tcs` に例外を入れる仕組みです。時間切れで呼び出し側が諦めたあとに遅れて返事が届いても、`_pending` に `id` が残っていないので、読み取りのループがその返事を黙って捨てます。`finally` で `_pending` から必ず取り除くのは、表が増え続けないようにするためです。

```csharp title="Editor/Engine/EngineClient.cs（続き：書き込み）"
    private Stream Stream => _stream ?? throw new InvalidOperationException("ConnectAsync が先に必要です。");

    private async Task WriteMessageAsync(byte[] body)
    {
        await _writeLock.WaitAsync().ConfigureAwait(false);     // 複数の命令が同時に書いても、バイトが交ざらないようにする
        try
        {
            await Framing.WriteFrameAsync(Stream, body).ConfigureAwait(false);
        }
        catch (IOException)
        {
            throw new EngineDisconnectedException();           // 切れた接続への書き込みは、切断として扱う
        }
        finally
        {
            _writeLock.Release();
        }
    }
```

`SemaphoreSlim` の `_writeLock` は、書き込みの順番待ちの列を作ります。2 つのタスクが同時に `WriteAsync` を呼ぶと、バイトが途中で交ざって、受けた側の長さの解釈が壊れます。切れた接続への書き込みは `IOException` になるので、`EngineDisconnectedException` に翻訳します。

```csharp title="Editor/Engine/EngineClient.cs（続き：返事を読むループ）"
    private async Task ReadLoopAsync()
    {
        try
        {
            while (true)
            {
                byte[] body = await Framing.ReadFrameAsync(Stream).ConfigureAwait(false);
                using var doc = JsonDocument.Parse(body);
                JsonElement root = doc.RootElement;
                if (root.TryGetProperty("id", out var idProp) && _pending.TryGetValue(idProp.GetInt32(), out var tcs))
                {
                    tcs.TrySetResult(root.Clone());   // doc を閉じたあとも使えるように複製する
                }
                // 待っている人がいない id（時間切れのあとに届いた返事）は、黙って捨てる
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

    public async ValueTask DisposeAsync()
    {
        _closing = true;
        if (_stream is not null) await _stream.DisposeAsync().ConfigureAwait(false);
        if (_readLoop is not null) await _readLoop.ConfigureAwait(false);
    }
}
```

読むループは、返事を 1 つ読むたびに、`id` で返事待ちの表から探して、結果を入れます。`finally` で、返事待ちの全員に `EngineDisconnectedException` を渡すのは、待っている呼び出しが永遠に待ち続けないためです。`Disconnected` は、自分から閉じたとき（`_closing`）には出しません。自分で閉じただけなのに、「エンジンが落ちた」と受け取られるのを防ぐためです。

### 同期のコードから呼ぶとき

`RequestAsync` は、`Task` を返す非同期のメソッドです。エンジンへの命令が同期のコードの中にあるなら、結果を待ってから進む形にできます。

```csharp
// 同期のコードから呼ぶ。UI スレッドでは呼ばない（エンジンが固まると、時間切れまで UI が固まる）
JsonElement reply = client.RequestAsync("add", new { a = 1, b = 2 }).GetAwaiter().GetResult();
```

`.GetAwaiter().GetResult()` は、`.Result` や `.Wait()` と違って、失敗したときに `AggregateException` に包まず、元の例外（`EngineCommandException` など）をそのまま投げ直します。呼ぶ側が `catch (EngineCommandException)` と書けるのは、この性質のおかげです。ただし、UI スレッドから呼んではいけません。エンジンが固まったとき、時間切れまでウィンドウが固まります。描画スレッドのような専用のスレッドから呼んでください。

## 4. 動かして確かめる

エンジンとクライアントを、実際に動かします。C# のコンソール アプリを作って、`IEngineTransport.cs`、`Framing.cs`、`TcpTransport.cs`、`EngineClient.cs` を追加します。`Program.cs` は次のとおりです。

```csharp title="Program.cs"
using System.Diagnostics;
using Editor.Engine;

// エンジンの起動: 標準出力の "port=NNNN" を読む（最小の形）
var exe = args[0];                                           // ビルドした TcpServer.exe のパス
var info = new ProcessStartInfo(exe)
{
    UseShellExecute = false,
    RedirectStandardOutput = true,     // ポート番号を受け取る
};
using Process engine = Process.Start(info)!;
string line = engine.StandardOutput.ReadLine()!;             // "port=56789"
int port = int.Parse(line["port=".Length..]);
Console.WriteLine($"エンジンが待ち受け中: 127.0.0.1:{port}");

// 繋いで、命令を送る
var client = new EngineClient(new TcpTransport(port));
await client.ConnectAsync(timeoutMs: 2000);

var pong = await client.RequestAsync("ping");
Console.WriteLine($"ping -> {pong.GetProperty("result").GetString()}");

var sum = await client.RequestAsync("add", new { a = 20, b = 22 });
Console.WriteLine($"add(20, 22) -> {sum.GetProperty("result").GetInt32()}");

try
{
    await client.RequestAsync("no_such_command");            // エンジンが「失敗です」と答える
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

// 閉じる。エンジンは、読み取りが終わって、自分で終わる
await client.DisposeAsync();
engine.WaitForExit(3000);
Console.WriteLine($"エンジンの終了コード: {engine.ExitCode}");
```

引数に `TcpServer.exe` のパスを渡して実行します。

```text title="実行結果（実測）"
エンジンが待ち受け中: 127.0.0.1:53477
ping -> pong
add(20, 22) -> 42
知らない命令 -> EngineCommandException: unknown command: no_such_command
100 件を同時に送った結果が、すべて正しい: True
エンジンの終了コード: 0
```

`ping` と `add` が、エンジンから返ってきました。知らない命令には `ok: false` の返事が返り、クライアントでは `EngineCommandException` になります。接続は生きたままです。100 件を返事を待たずに同時に送っても、すべて正しい返事が正しい要求に結びつきました。`id` の対応づけが働いています。最後にエディタが接続を閉じると、エンジンの読み取りが終わって、終了コード 0 で終わります。

このコードは、MSVC と .NET 10 で、実際にコンパイルして動かして確かめました。

## ここまでで、できたこと

エディタとエンジンが、別のプロセスとして、TCP で会話できるようになりました。このあとの章は、この最小の形に足していく順に進みます。

- 第 60 章：この通信を、Prest のエディタの構造に組み込む。エンジンの起動と、`IEngineService` の差し替え
- 第 61 章：動いたものを、安全で壊れにくくする。合言葉、固まりの検出、行儀のよい終了、テスト
- 第 62 章：TCP の仕組みを、詳しく知る。困ったときに引く章

この章の最小の形には、まだ足りない所が残っています。他のプログラムが同じポートに繋いでくる、エンジンが固まっても気づけない、閉じ方が乱暴、といった点です。動くものを先に作ってから直したほうが、何を守っているのかが分かるので、第 61 章にまとめてあります。

## よくあるミス

??? failure "標準出力の fflush を忘れる"
    何が起きるか：パイプに繋がった標準出力は、バッファされます。`port=NNNN` がバッファに留まったまま、エディタが待ち続けます。

    対処：`std::fflush(stdout)` を呼びます。標準出力はポートの通知だけにして、ログは標準エラーに書きます。

??? failure "NetworkStream を繋がる前のソケットで作る"
    何が起きるか：`NetworkStream` のコンストラクターが、`IOException`（「非接続のソケットでは、この操作は許可されません」）を投げます。

    対処：`ConnectAsync` が成功してから、`NetworkStream` を作ります。

??? failure "recv や Read を 1 回呼んで、メッセージが全部届いたと思う"
    何が起きるか：細切れに届いたときに、長さや本文が足りないまま処理して、データが壊れます。普段は動いて、負荷が高いときや大きなメッセージのときだけ壊れるので、見つけにくい不具合になります。

    対処：必要なバイト数が揃うまで読み続けます（C++ の `RecvExact`、C# の `ReadExactlyAsync`）。

??? failure "待ち受けを IPAddress.Any（0.0.0.0）にする"
    何が起きるか：LAN の他の PC からも繋がる入り口になります。

    対処：`127.0.0.1` だけにします。`netstat` で `127.0.0.1:ポート` の `LISTENING` になっていることを確かめます。

## これだけ覚える

- TCP はバイトの流れ。メッセージの切れ目は、アプリが決める。この章では 4 バイトの長さ＋ UTF-8 の JSON にした。
- 要求には `id` を付けて、返事に写す。返事は `id` で、返事待ちの表から探す。
- 失敗は 2 種類。エンジンの「失敗です」（`EngineCommandException`）と、接続の切れ（`EngineDisconnectedException`）。
- 読むループは、書く処理とは別のタスクで、常に回す。
- 待ち受けは `127.0.0.1` だけ。ポートは 0 で OS に選ばせて、エンジンが標準出力で知らせる。

## 確かめたもの、確かめていないもの

!!! note "確かめたもの、確かめていないもの"
    確かめたもの：`TcpServer.cpp` は MSVC でコンパイルが通った。C# の `EngineClient`、`TcpTransport`、`Framing`、`Program.cs` は .NET 10 でコンパイルして、`TcpServer.exe` と実際に繋いで動かした（上の実行結果）。
    確かめていないもの：本物のエンジンの命令処理とは繋いでいない。複数のエディタが同時に繋ぐ構成（このサーバーは 1 人を相手にして終わる）。`FindString` と `FindNumber` は確認用の簡易な読み方で、エスケープを含む JSON は正しく読めない。

## 関連ページ

- [第 60 章 TCP 編 2：Prest のエディタに組み込む](60-tcp-editor.md)（次の章。エンジンの起動と `IEngineService` の差し替え）
- [第 61 章 TCP 編 3：安全で壊れにくくする](61-tcp-hardening.md)（合言葉、ハートビート、行儀のよい終了、テスト）
- [第 62 章 TCP を深く知る：バイトの流れとして使うために](62-tcp-deep.md)（Nagle、ウィンドウ、切断など、この章で出た話の詳細）
- [第 53 章 プロセスを分ける：落ちても生きる構成](53-process-split.md)
- [第 54 章 IEngineService を差し替える](54-remote-engine-service.md)

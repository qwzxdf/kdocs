---
title: 第 53 章 プロセスを分ける：落ちても生きる構成
tags:
  - C#連携
---

# 第 53 章 プロセスを分ける：落ちても生きる構成

描画のコードで `nullptr` を触った瞬間にエディタが消えて、直前まで編集していたシーンも一緒に消えた。ここまで作ってきたエディタではこういうことが起きます。第 50 章ではミニダンプを残す仕組みを作りましたが、あれは「落ちたあとに原因を調べる」ためのもので、落ちること自体は防げません。

落ちる理由ははっきりしています。エディタ（C#）とエンジン（C++）が、同じプロセスの中に住んでいるからです。C++ のアクセス違反は C# の `try/catch` では捕まらず、プロセスごと終了します。エンジンが無限ループに入れば、エディタの画面も固まります。

この章から第 7 部です。エンジンを別のプロセスに出して、<strong>エンジンが落ちてもエディタは生き残る</strong>構成を作ります。この章では土台になる部分、つまり別プロセスとの会話の仕方を扱います。RPC という考え方、通信路の選び方、メッセージの形、そして C++ のサーバーと C# のクライアントの最小の実装です。最後に、エンジンをわざと落としてエディタが生きていることを確かめます。

!!! info "このページを読む前に"
    - [第 52 章 ビルド、テスト、配布](52-build-deploy.md)（前の章。ここまでの内容が前提になる）
    - [第 31 章 C# から C++ を呼ぶ：連携方式の比較](31-interop-overview.md)（IPC を「選ばなかった」理由。この章はその続き）
    - [第 50 章 ログとエラー処理](50-logging-errors.md)（同じプロセスで落ちたとき、何が残せて何が残せないか）
    - [C# 連携](index.md)（このセクション全体の地図と読む順番）


!!! abstract "この章で足すもの"
    | ファイル | 内容 |
    | --- | --- |
    | `EngineHost/Server.cpp`（新規） | 名前付きパイプのサーバー。メッセージを 1 つ読んで返事を 1 つ書く |
    | `Editor/Engine/EngineClient.cs`（新規） | 命令を送って返事を待つクライアント。切断とタイムアウトを例外にする |

    `EngineHost` はエンジンを動かす新しい exe です。プロジェクトとしての整え方は第 55 章で扱いこの章では通信の部分だけを取り出して書きます。


## 同じプロセスにいる限り道連れになる

プロセスは OS が用意するメモリの区画です。同じプロセスの中のコードは同じ区画を読み書きできます。P/Invoke が速いのも C++ の関数をそのまま呼べるのも同じ区画にいるからです。

その代わり片方が区画を壊せば、もう片方も壊れます。C++ の側で `nullptr` を書き込むと OS は「不正なメモリへのアクセス」としてプロセスを終了させます。.NET から見てもこれは捕まえられない例外です（第 50 章）。エンジンが数秒間ハングした場合もエンジンを呼んだスレッドが戻ってこないので、そのスレッドが UI スレッドなら画面が固まります。

区画を分ければ、この道連れは起きません。エンジンのプロセスが消えても、エディタのプロセスは別の区画で動き続けます。

<svg class="fig flow" viewBox="0 0 720 300" role="img" aria-label="同じプロセスではエンジンが落ちるとエディタも落ちる。別プロセスではエンジンだけが落ちる"><defs><marker id="psA" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">落ちたとき、どこまで巻き込まれるか</text><text x="170" y="52" text-anchor="middle" style="font-size:13px;font-weight:600">同じプロセス（ここまでの構成）</text><rect x="16" y="64" width="308" height="140" rx="14" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="170" y="86" text-anchor="middle" style="font-size:12px;font-weight:400">Editor.exe（プロセスは 1 つ）</text><rect x="32" y="110" width="120" height="50" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="92" y="135" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">WPF（C#）</text><rect x="188" y="110" width="120" height="50" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="248" y="135" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">Engine.dll</text><line x1="152" y1="135" x2="188" y2="135" stroke="currentColor" stroke-width="2" marker-end="url(#psA)"/><text x="170" y="178" text-anchor="middle" style="font-size:11px;font-weight:400">P/Invoke</text><text x="170" y="232" text-anchor="middle" style="font-size:12px;font-weight:400">Engine.dll が落ちると、</text><text x="170" y="250" text-anchor="middle" style="font-size:12px;font-weight:600">Editor.exe ごと消える</text><text x="548" y="52" text-anchor="middle" style="font-size:13px;font-weight:600">別プロセス（この章からの構成）</text><rect x="372" y="64" width="150" height="140" rx="14" fill="rgba(148,163,184,0.18)" stroke="#94a3b8" stroke-width="2"/><text x="447" y="86" text-anchor="middle" style="font-size:12px;font-weight:400">Editor.exe</text><rect x="392" y="110" width="110" height="50" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="447" y="135" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">WPF（C#）</text><rect x="570" y="64" width="134" height="140" rx="14" fill="rgba(148,163,184,0.10)" stroke="#94a3b8" stroke-width="2" stroke-dasharray="6 5"/><text x="637" y="86" text-anchor="middle" style="font-size:12px;font-weight:400">EngineHost.exe</text><rect x="584" y="110" width="106" height="50" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="637" y="135" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">Engine（C++）</text><line x1="522" y1="135" x2="570" y2="135" stroke="currentColor" stroke-width="2" marker-end="url(#psA)"/><line x1="570" y1="150" x2="522" y2="150" stroke="currentColor" stroke-width="2" marker-end="url(#psA)"/><text x="546" y="124" text-anchor="middle" style="font-size:11px;font-weight:400">パイプ</text><text x="548" y="232" text-anchor="middle" style="font-size:12px;font-weight:400">EngineHost.exe が落ちても、</text><text x="548" y="250" text-anchor="middle" style="font-size:12px;font-weight:600">Editor.exe は「切れた」を知るだけ</text><text x="360" y="284" text-anchor="middle" style="font-size:12px;font-weight:400">間にあるのは OS が管理するパイプだけ。メモリは共有しない。</text></svg>

ただし、分けることには代償があります。先に並べておきます。

- 呼び出しが遅くなります。関数を呼ぶ代わりにデータをバイト列にして OS に渡し、相手が読んで返事をバイト列で受け取ります。この章の最後で実測します。
- ポインターを渡せなくなります。区画が違えば同じアドレスは別の場所を指すからです。物は ID で指します。
- 失敗の形が増えます。関数が戻ってこない、相手が消えた、返事が遅い、といったことが日常になります。
- 道具が増えます。起動の順番、片方が消えたときの後始末、2 つのプロセスのデバッグが必要になります。

この代償に見合うのは、エンジンが不安定になりやすい時期や、ユーザーが書いた C++（ゲームのコード）を動かす場面です。逆に、エンジンが十分に安定していて、毎フレーム細かく呼び合うなら同じプロセスのほうが素直です。第 31 章で P/Invoke を主役にしたのもこの理由からです。

## RPC：別のプロセスの関数を呼ぶ

別のプロセスの関数をふつうの関数のように呼べるようにする仕組みを <strong>RPC</strong>（Remote Procedure Call）と呼びます。呼ぶ側のコードは同じ見た目のまま中身が通信に置き換わります。

```csharp
// 同じプロセスのとき
engine.SetPosition(3, new Vector3(1, 0, 2));

// RPC のとき（見た目はほぼ同じ。ただし await が付く）
await engine.SetPositionAsync(3, new Vector3(1, 0, 2));
```

裏では次の順に動いています。

1. 呼ぶ側が「どの関数を、どんな引数で呼ぶか」をバイト列にする（直列化）。
2. 通信路（パイプなど）でバイト列を送る。
3. 呼ばれる側がバイト列から関数名と引数を取り出し、本物の関数を実行する。
4. 結果（成功か失敗か、戻り値）をバイト列にして送り返す。
5. 呼ぶ側が受け取り、戻り値として返す。

RPC は関数呼び出しに見えますが、同じ前提は使えません。遅く、失敗し、ポインターを渡せません。そのため、API の形も変わります。`await` を付けて UI を止めないこと、タイムアウトを必ず決めること、細かい呼び出しを束ねることが、設計の前提になります。

## 通信路を選ぶ

バイト列を運ぶ道にはいくつか候補があります。エンジンとエディタは同じ PC にいるので、ネットワークを越える機能はほとんど要りません。

### 名前付きパイプ

Windows の標準の仕組みで、同じ PC 内のプロセス同士が、名前を使って双方向のバイト列をやり取りします。C# は `NamedPipeServerStream` と `NamedPipeClientStream`、C++ は `CreateNamedPipe` と `CreateFile` で扱えます。追加のライブラリが要らず、ネットワークに出ません。

短所は Windows 専用であることです。また、メッセージの区切りと形式を自分で決める必要があります。

### TCP（localhost）

`127.0.0.1` のポートで待ち受けて、ソケットでやり取りします。どの言語にも、どの OS にも同じ作りで書けるのが長所です。実機（コンソールやスマートフォン）で動くゲームへ繋ぐ通信も同じ形になります。

短所は、同じ PC の他のプログラムからも繋げることです。ポート番号の衝突や、ファイアウォールの確認ダイアログも起きます。

### gRPC

`.proto` というファイルに関数の形を書くと、C# と C++ の両方で、呼ぶ側と呼ばれる側のコードが自動で作られます。型の食い違いがコンパイルで見つかり、関数が数十個に増えても、手で書くコードが増えません。

短所は導入の重さです。C++ 側のライブラリが大きく、vcpkg での導入とコード生成の設定が要ります。学生が環境で詰まりやすい所でもあります。

### 共有メモリ

メモリの一部を 2 つのプロセスから見えるようにします。コピーが要らないので、メッシュやテクスチャのような大きなデータの受け渡しに向きます。

ただし、いつ書き終わったかを知らせる仕組み（イベントやフラグ）を自分で作る必要があり、扱いが難しいです。「命令」は別の通信路で送り、「大きなデータの置き場」にだけ使うのが定番です。

### 並べて比べる

| 観点 | 名前付きパイプ | TCP | gRPC |
| --- | --- | --- | --- |
| 導入の軽さ | 標準だけ | 標準だけ | ライブラリが大きい |
| 外から繋がれる範囲 | 同じ PC のみ | 同じ PC の他のプログラム | TCP と同じ |
| 型の食い違い | 手で合わせる | 手で合わせる | 自動で防げる |
| 他の OS・実機 | 使えない | 使える | 使える |

## この教材の選択

通信路は<strong>名前付きパイプ</strong>、中身は <strong>JSON</strong> にします。理由は 3 つあります。

1. 追加のライブラリがなく、Visual Studio と標準の API だけで動かせます。C++ 側の JSON には広く使われている nlohmann を使います。
2. ネットワークに出ません。AI から呼び出せるようにする章（第 58 章）で、外から勝手に命令を送られる入口を作りたくないからです。
3. JSON は人間にも読めるので、メッセージをログに出すだけでデバッグできます。MCP（第 58 章）も JSON ベースなので、そのまま繋げます。

遅くなったら、そこだけバイナリ形式に変えられます。実機に繋ぐ必要が出たら、同じメッセージを TCP に載せ替えられます。そのために、パイプの読み書きは「バイト列を送る」だけの小さな層に閉じ込めておきます。

## メッセージの形

パイプ（と TCP）はバイトの<strong>流れ</strong>を運ぶだけで、メッセージの切れ目を知りません。送った側が 100 バイトを 2 回に分けて書いても、受けた側は 60 バイトと 140 バイトで受け取るかもしれません。そこで、メッセージの先頭に長さを付けます。

<svg class="fig flow" viewBox="0 0 720 262" role="img" aria-label="メッセージは 4 バイトの長さと JSON の本文でできている。要求と返事は id で対応づける"><defs><marker id="psB" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="currentColor"/></marker></defs><text x="14" y="22" class="fig-title">1 つのメッセージと、要求・返事の対応</text><rect x="16" y="38" width="110" height="44" rx="9" fill="rgba(229,170,40,0.28)" stroke="#e5aa28" stroke-width="2"/><text x="71" y="60" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">長さ N（4 バイト）</text><rect x="126" y="38" width="430" height="44" rx="9" fill="rgba(76,139,245,0.22)" stroke="#4c8bf5" stroke-width="2"/><text x="341" y="60" text-anchor="middle" dominant-baseline="central" style="font-size:13px;font-weight:600">本文 N バイト（UTF-8 の JSON）</text><text x="570" y="55" style="font-size:12px;font-weight:400">先に長さを読めば、</text><text x="570" y="73" style="font-size:12px;font-weight:400">どこまでが 1 つか分かる</text><text x="100" y="124" text-anchor="middle" style="font-size:13px;font-weight:600">Editor（C#）</text><text x="620" y="124" text-anchor="middle" style="font-size:13px;font-weight:600">EngineHost（C++）</text><line x1="100" y1="134" x2="100" y2="248" stroke="#94a3b8" stroke-width="2"/><line x1="620" y1="134" x2="620" y2="248" stroke="#94a3b8" stroke-width="2"/><line x1="100" y1="152" x2="620" y2="164" stroke="currentColor" stroke-width="2" marker-end="url(#psB)"/><text x="360" y="150" text-anchor="middle" style="font-size:12px;font-weight:400">id=1  set_position</text><line x1="100" y1="180" x2="620" y2="192" stroke="currentColor" stroke-width="2" marker-end="url(#psB)"/><text x="360" y="178" text-anchor="middle" style="font-size:12px;font-weight:400">id=2  get_selection</text><line x1="620" y1="206" x2="100" y2="218" stroke="currentColor" stroke-width="2" marker-end="url(#psB)"/><text x="360" y="204" text-anchor="middle" style="font-size:12px;font-weight:400">id=1  ok</text><line x1="620" y1="232" x2="100" y2="244" stroke="currentColor" stroke-width="2" marker-end="url(#psB)"/><text x="360" y="230" text-anchor="middle" style="font-size:12px;font-weight:400">id=2  ok</text></svg>

長さは 4 バイトの整数（リトル エンディアン。x64 の Windows が普通に使う並びです）で、その後ろに UTF-8 の JSON を置きます。JSON の中身は要求と返事で次の形にします。

```json
{"id": 7, "cmd": "set_position", "args": {"id": 3, "x": 1, "y": 0, "z": 2}}
{"id": 7, "ok": true, "result": null}
{"id": 8, "ok": false, "error": "unknown object: 99"}
```

要求の `id` は、呼ぶ側が決める通し番号です。返事には同じ `id` を入れて返します。これで、返事が来た順番を気にせず、どの要求への返事かを突き合わせられます。同時に複数の要求を送り出しておけるので、返事を待つ間に UI が止まりません。`args` の中の `id` はシーンのオブジェクトの ID で、メッセージの `id` とは別物です。

`ok` が `false` のときは、`error` に理由を入れます。これは<strong>エンジンが「失敗です」と答えた</strong>場合で、接続は生きています。パイプが切れる（エンジンが消えた）場合とは別の失敗として、後で別の例外に分けます。

長さが壊れていたときの備えも要ります。もし読み取りの位置がずれて、JSON の文字 `{"id` の 4 バイト（`7B 22 69 64`）を長さとして読むと、値は 1,684,611,707、つまり約 1.6 GB になります。これをそのまま信じて確保すると、メモリを食い尽くします。そこで、長さの上限を 16 MiB と決めて、超えたら壊れたものとして接続を切ります。

## C++ 側：パイプのサーバー

エンジンの側（`EngineHost`）から作ります。やることは、パイプを作ってエディタの接続を待ち、メッセージを 1 つ読んで、処理して、返事を書く、の繰り返しです。

### 確実に読み書きする

```cpp title="EngineHost/Server.cpp（新規）"
#include <windows.h>

#include <cstdint>
#include <cstring>
#include <functional>
#include <string>

namespace {

constexpr uint32_t kMaxMessageSize = 16 * 1024 * 1024;  // 16 MiB。これを超える長さは壊れたデータとみなす

// size バイトが揃うまで読む。バイト モードのパイプは、要求より少なく返すことがある。
bool ReadExact(HANDLE pipe, void* buffer, DWORD size) {
  auto* p = static_cast<char*>(buffer);
  while (size > 0) {
    DWORD read = 0;
    if (!ReadFile(pipe, p, size, &read, nullptr) || read == 0) {
      return false;  // 相手が閉じた（ERROR_BROKEN_PIPE）か、読めなくなった
    }
    p += read;
    size -= read;
  }
  return true;
}

bool WriteExact(HANDLE pipe, const void* buffer, DWORD size) {
  auto* p = static_cast<const char*>(buffer);
  while (size > 0) {
    DWORD written = 0;
    if (!WriteFile(pipe, p, size, &written, nullptr)) {
      return false;
    }
    p += written;
    size -= written;
  }
  return true;
}
```

`ReadFile` は「要求したバイト数が揃うまで待つ」関数ではありません。いま届いている分だけを返して戻ることがあります。メッセージの長さの 4 バイトも本文も 1 回の `ReadFile` で全部読めるとは限らないので、揃うまで繰り返す `ReadExact` を挟みます。これを省いて 1 回で済ませると、小さいメッセージでは動くのに、大きなメッセージや負荷が高いときにだけ壊れる、再現しにくい不具合になります。

`read == 0` を失敗に含めているのは、読み取りが 0 バイトで成功を返す場合に、`while` が回り続けるのを避けるためです。`WriteExact` も同じ理由で、書き切るまで繰り返します。

### 1 メッセージを読み書きする

```cpp title="EngineHost/Server.cpp（続き）"
// 1 メッセージ = 4 バイトの長さ（リトル エンディアン）+ 本文（UTF-8 の JSON）。
bool ReadMessage(HANDLE pipe, std::string& out) {
  uint32_t length = 0;
  if (!ReadExact(pipe, &length, sizeof(length))) return false;
  if (length > kMaxMessageSize) return false;  // 壊れた長さ。巨大な確保を避けるために切る
  out.resize(length);
  return length == 0 || ReadExact(pipe, out.data(), length);
}

bool WriteMessage(HANDLE pipe, const std::string& body) {
  // 長さと本文を 1 回の書き込みにそろえる（別々に書くと、将来スレッドが増えたときに交ざる）
  std::string frame(sizeof(uint32_t) + body.size(), '\0');
  const auto length = static_cast<uint32_t>(body.size());
  memcpy(frame.data(), &length, sizeof(length));
  memcpy(frame.data() + sizeof(length), body.data(), body.size());
  return WriteExact(pipe, frame.data(), static_cast<DWORD>(frame.size()));
}

}  // namespace
```

`ReadMessage` は、まず長さを読み、上限を確かめてから、その長さの分だけ本文を読みます。上限の確認を、確保（`resize`）の前に置くのが肝心です。順番が逆だと、壊れた長さで巨大なメモリを確保してから気づくことになります。

`WriteMessage` は、長さと本文を 1 つのバッファーに詰めて、1 回の書き込みで送ります。`uint32_t` をそのまま `memcpy` するのは、x64 の Windows がリトル エンディアンだからです。C# 側が `BinaryPrimitives.ReadInt32LittleEndian` で読むのと対応しています。

### 接続を受けて処理を回す

```cpp title="EngineHost/Server.cpp（続き）"
// エディタとの接続を 1 つ受けて、切れるまで要求を処理する。戻り値は、接続を受けられたか。
bool ServeOnce(const wchar_t* pipe_name,
               const std::function<std::string(const std::string&)>& handler) {
  HANDLE pipe = CreateNamedPipeW(
      pipe_name,
      PIPE_ACCESS_DUPLEX,
      PIPE_TYPE_BYTE | PIPE_READMODE_BYTE | PIPE_WAIT | PIPE_REJECT_REMOTE_CLIENTS,
      1,            // 同時に 1 接続だけ。エディタ以外が割り込めないようにする
      64 * 1024,    // 出力バッファー
      64 * 1024,    // 入力バッファー
      0,            // 既定のタイムアウト
      nullptr);     // 既定のセキュリティ記述子
  if (pipe == INVALID_HANDLE_VALUE) return false;

  // エディタが繋ぐまで待つ。繋ぐ前に相手が先に繋いでいた場合は ERROR_PIPE_CONNECTED が返る（それも成功）。
  const bool connected = ConnectNamedPipe(pipe, nullptr) || GetLastError() == ERROR_PIPE_CONNECTED;
  if (connected) {
    std::string request;
    while (ReadMessage(pipe, request)) {  // エディタが閉じる（または壊れた長さが来る）と false で抜ける
      if (!WriteMessage(pipe, handler(request))) break;
    }
  }
  CloseHandle(pipe);
  return connected;
}
```

`CreateNamedPipeW` の引数のうち、意味を持つものを順に見ます。

パイプの名前は `\\.\pipe\MiniEngine` のように、`\\.\pipe\` で始めます。`PIPE_ACCESS_DUPLEX` は読み書きの両方向を許可します。`PIPE_TYPE_BYTE` はバイトの流れとして扱う指定です。メッセージ単位で扱う `PIPE_TYPE_MESSAGE` もありますが、それは Windows 専用の仕組みなので、将来 TCP に載せ替えるときに手間が増えます。今回は長さを自分で付けてバイト モードで揃えます。

`PIPE_REJECT_REMOTE_CLIENTS` は、ネットワーク越しの接続を断る指定です。名前付きパイプは、既定ではネットワーク上の別の PC からも開ける場合があります。同じ PC の中だけで使うなら、必ず付けます。同じ PC の他のユーザーからのアクセスは、ここでは既定の設定のままです。共有の PC で気になるときは、`SECURITY_ATTRIBUTES` で自分のユーザーだけに絞れますが、この章のコードには入れていません。

最大インスタンス数の `1` は、同じ名前のパイプを同時に 1 つしか作れなくします。同じ名前で 2 つ目のエンジンを起動すると、`CreateNamedPipeW` が失敗して `ServeOnce` が `false` を返します（手元で確かめました）。エンジンが二重に起動して、エディタがどちらに繋いだか分からなくなる事故を防げます。

`ConnectNamedPipe` は、エディタが繋ぐまで止まって待ちます。待っている間に先にエディタが繋いでいた場合は、`FALSE` と `ERROR_PIPE_CONNECTED` が返りますが、これは成功と同じ扱いです。

ループの終わりは 2 通りです。エディタがパイプを閉じるか、エディタのプロセスが消えると、`ReadFile` が失敗して `ReadMessage` が `false` を返します。エディタが先に消えたときにエンジンも一緒に終了する、つまり「親が消えたら自分も終わる」動きが、この 1 行で手に入ります。

### 命令を振り分ける

`handler` に渡すのは、読んだ JSON の文字列です。返すのは、返事の JSON の文字列です。実際の振り分けは、nlohmann を使うと、このように書けます。

```cpp title="EngineHost/Dispatch.cpp（新規。コンパイルしていない）"
#include <stdexcept>
#include <string>

#include <nlohmann/json.hpp>

using json = nlohmann::json;

std::string HandleRequest(const std::string& text) {
  json reply = {{"id", nullptr}, {"ok", false}};
  try {
    const json req = json::parse(text);        // 壊れた JSON は parse_error を投げる
    reply["id"] = req.at("id");                // 返事に、要求と同じ id を入れる
    const std::string cmd = req.at("cmd");

    if (cmd == "ping") {
      reply["result"] = "pong";
    } else if (cmd == "set_position") {
      const json& a = req.at("args");
      const int object_id = a.at("id");
      const float x = a.at("x"), y = a.at("y"), z = a.at("z");
      g_scene.SetPosition(object_id, x, y, z);  // g_scene と SetPosition は仮の名前
      reply["result"] = nullptr;
    } else {
      throw std::runtime_error("unknown cmd: " + cmd);
    }
    reply["ok"] = true;
  } catch (const std::exception& e) {
    reply["ok"] = false;
    reply["error"] = e.what();                 // C++ の例外は、ここで止めて「失敗」として返す
  }
  return reply.dump();
}
```

最後の `catch` が、第 31 章の「例外は境界で止める」の、この章での姿です。C++ の例外が通信の外に漏れることはありません。失敗はすべて `ok: false` の返事になり、エディタ側で `EngineCommandException` に変わります。

`id` を先に返事へ写しているのは、途中で例外が起きても、どの要求への失敗かをエディタが分かるようにするためです。`id` すら読めない壊れた JSON のときは `null` のまま返ります。

## C# 側：EngineClient

エディタの側です。やることは 3 つあります。要求を書く、返事を読むループを別のタスクで回す、返事を `id` で待ち手に渡す、です。

### 土台

```csharp title="Editor/Engine/EngineClient.cs（新規）"
using System.Buffers.Binary;
using System.Collections.Concurrent;
using System.IO.Pipes;
using System.Text.Json;

namespace Editor.Engine;

// エンジンが落ちた（パイプが切れた）ことを表す例外
public sealed class EngineDisconnectedException : IOException
{
    public EngineDisconnectedException() : base("エンジンとの接続が切れました。") { }
}

// エンジンが「失敗」を返したことを表す例外（接続は生きている）
public sealed class EngineCommandException(string message) : Exception(message);

public sealed class EngineClient : IAsyncDisposable
{
    private const int MaxMessageSize = 16 * 1024 * 1024;

    private readonly NamedPipeClientStream _pipe;
    private readonly SemaphoreSlim _writeLock = new(1, 1);
    private readonly ConcurrentDictionary<int, TaskCompletionSource<JsonElement>> _pending = new();
    private int _nextId;
    private Task? _readLoop;

    // 接続が切れたときに呼ばれる（スレッド プールのスレッドから）。UI を触るなら Dispatcher を通す
    public event Action? Disconnected;

    public EngineClient(string pipeName = "MiniEngine")
        => _pipe = new NamedPipeClientStream(".", pipeName, PipeDirection.InOut, PipeOptions.Asynchronous);

    public async Task ConnectAsync(int timeoutMs = 5000)
    {
        await _pipe.ConnectAsync(timeoutMs);     // 時間内に繋がらなければ TimeoutException
        _readLoop = Task.Run(ReadLoopAsync);     // 返事を読むループを、別のタスクで回す
    }
```

失敗を 2 つの例外に分けているのが設計の要です。`EngineCommandException` は、エンジンが「その操作はできません」と答えた場合で、画面にメッセージを出せば済みます。`EngineDisconnectedException` は、エンジンのプロセスが消えた場合で、再接続や復旧の処理（第 57 章）に進む合図です。両方を同じ `Exception` で受けると、「単なる失敗」と「相手が消えた」を見分けられません。

`_pending` は「返事待ちの表」です。キーが要求の `id`、値が `TaskCompletionSource` で、これは「あとで結果を入れられる `Task`」を作る道具です。呼び出し側はこの `Task` を `await` し、返事を読むループが結果を入れた瞬間に、続きが動き出します。複数のスレッドから触るので、`ConcurrentDictionary` を使います。

`ConnectAsync` の時間切れが必要な理由は、エンジンがまだ起動していない場合に、いつまでも待ち続けないためです。`NamedPipeClientStream.ConnectAsync` はサーバーがパイプを作るまで待つ仕組みなので、時間切れを必ず付けます。

### 要求を送って返事を待つ

```csharp title="Editor/Engine/EngineClient.cs（続き）"
    // 命令を 1 つ送って、返事を待つ。返事が来るまで UI スレッドは止まらない（await）
    public async Task<JsonElement> RequestAsync(string cmd, object? args = null, TimeSpan? timeout = null)
    {
        int id = Interlocked.Increment(ref _nextId);
        var tcs = new TaskCompletionSource<JsonElement>(TaskCreationOptions.RunContinuationsAsynchronously);
        _pending[id] = tcs;
        try
        {
            await WriteMessageAsync(JsonSerializer.SerializeToUtf8Bytes(new { id, cmd, args }));

            var limit = timeout ?? TimeSpan.FromSeconds(5);
            using var cts = new CancellationTokenSource(limit);
            using (cts.Token.Register(() => tcs.TrySetException(
                       new TimeoutException($"'{cmd}' の返事が {limit.TotalSeconds} 秒以内に来ませんでした。"))))
            {
                JsonElement reply = await tcs.Task;
                if (!reply.GetProperty("ok").GetBoolean())
                {
                    throw new EngineCommandException(reply.GetProperty("error").GetString() ?? "(理由なし)");
                }
                return reply;
            }
        }
        finally
        {
            _pending.TryRemove(id, out _);
        }
    }
```

`Interlocked.Increment` は、複数のスレッドが同時に呼んでも重ならない番号を振ります。`TaskCreationOptions.RunContinuationsAsynchronously` は返事を読むループが `TrySetResult` した瞬間に `await` の続きがそのスレッドで同期的に走ってしまうのを避ける指定です。これを付けないと、返事を読むループの中で呼び出し側の処理が動き、次の返事の読み取りが遅れます。

時間切れの仕組みは `CancellationTokenSource` に制限時間を渡し、時間が来たら `tcs` に例外を入れる、というものです。この章のサーバーは 1 つずつ順に処理するので、ある要求が遅れると後ろの要求も待たされます。時間切れで呼び出し側が諦めたあと、遅れて返事が届いても、`_pending` に `id` が残っていないので、読み取りのループがその返事を黙って捨てます（次の節で確かめます）。

`finally` で `_pending` から必ず取り除くのは、成功でも失敗でも時間切れでも、待ち手の表に残さないためです。残すと、表が増え続けます。

### 書き込みと読み取りのループ

```csharp title="Editor/Engine/EngineClient.cs（続き）"
    private async Task WriteMessageAsync(byte[] body)
    {
        var frame = new byte[4 + body.Length];
        BinaryPrimitives.WriteInt32LittleEndian(frame, body.Length);
        body.CopyTo(frame, 4);

        await _writeLock.WaitAsync();            // 複数の命令が同時に書いても、バイトが交ざらないようにする
        try
        {
            await _pipe.WriteAsync(frame);
            await _pipe.FlushAsync();
        }
        catch (IOException)
        {
            throw new EngineDisconnectedException();   // 壊れたパイプへの書き込みは、切断として扱う
        }
        finally
        {
            _writeLock.Release();
        }
    }

    private async Task ReadLoopAsync()
    {
        var header = new byte[4];
        try
        {
            while (true)
            {
                await _pipe.ReadExactlyAsync(header);
                int length = BinaryPrimitives.ReadInt32LittleEndian(header);
                if (length < 0 || length > MaxMessageSize)
                {
                    throw new InvalidDataException($"不正なメッセージ長: {length}");
                }

                var body = new byte[length];
                await _pipe.ReadExactlyAsync(body);

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
            Disconnected?.Invoke();
        }
    }

    public async ValueTask DisposeAsync()
    {
        await _pipe.DisposeAsync();
        if (_readLoop is not null) await _readLoop;
    }
}
```

`SemaphoreSlim` の `_writeLock` は、書き込みの順番待ちの列を作ります。2 つのタスクが同時に `WriteAsync` を呼ぶと、バイトが途中で交ざり、受けた側の長さの解釈が壊れます。C++ 側で長さと本文を 1 回の書き込みにそろえたのと同じ理由です。

`ReadExactlyAsync` は、指定したバイト数が揃うまで待つメソッドです。C++ の `ReadExact` に当たります。相手が閉じれば `EndOfStreamException`（`IOException` の仲間）を投げるので、`catch` の `IOException` に入ります。

`finally` ブロックが、この章の中心です。読み取りのループがどんな理由で終わっても（エンジンの消滅、壊れたデータ、自分で閉じた）、返事待ちの全員に `EngineDisconnectedException` を入れます。これがないと、エンジンが消えた瞬間に `await` していた呼び出しが、永久に待ち続けます。そして最後に `Disconnected` を呼び、画面に「エンジンが落ちました。再起動しますか」と出す合図にします。

`Disconnected` はスレッド プールのスレッドから呼ばれます。ここで直接 `ObservableCollection` や画面の部品を触ると、第 17 章の UI スレッドのルールに違反します。`Dispatcher` を通して UI スレッドに戻してから触ってください。

## 動かして確かめる

ここまでのコードを組み合わせて、エンジンをわざと落として、エディタが生き残るかを実際に確かめました。C++ 側は、サーバーの本体（`ServeOnce`）に、文字列の検索だけで `ping`・`fail`・`hang`・`crash` を返す簡単なハンドラーを付けたものです。`crash` は `nullptr` に書き込んでアクセス違反を起こし、`hang` は 3 秒止まってから返事をします。C# 側は、コンソール アプリから `EngineClient` を呼んでいます。

```csharp title="確認用のコンソール（Editor には入れない）"
var server = Process.Start(new ProcessStartInfo(@"..\server.exe") { UseShellExecute = false })!;
await using var client = new EngineClient("MiniEngineTest");
client.Disconnected += () => Console.WriteLine("[event] Disconnected");
await client.ConnectAsync();

var r = await client.RequestAsync("ping");
Console.WriteLine("ping -> " + r.GetProperty("result").GetString());

try { await client.RequestAsync("fail"); }
catch (EngineCommandException e) { Console.WriteLine("fail -> EngineCommandException: " + e.Message); }

try { await client.RequestAsync("hang", timeout: TimeSpan.FromSeconds(1)); }
catch (TimeoutException e) { Console.WriteLine("hang -> TimeoutException: " + e.Message); }

await Task.Delay(2500);                       // サーバーの 3 秒の居眠りが終わるのを待つ
Console.WriteLine("late reply ignored; ping again -> " + (await client.RequestAsync("ping")).GetProperty("result"));

try { await client.RequestAsync("crash"); }
catch (EngineDisconnectedException e) { Console.WriteLine("crash -> EngineDisconnectedException: " + e.Message); }

try { await client.RequestAsync("ping"); }
catch (EngineDisconnectedException) { Console.WriteLine("after crash -> EngineDisconnectedException"); }

server.WaitForExit();
Console.WriteLine($"server exit code: 0x{server.ExitCode:X}");
Console.WriteLine("editor (C#) is still alive.");
```

```text title="実行結果"
ping -> pong
fail -> EngineCommandException: unknown object
hang -> TimeoutException: 'hang' の返事が 1 秒以内に来ませんでした。
late reply ignored; ping again -> pong
[event] Disconnected
crash -> EngineDisconnectedException: エンジンとの接続が切れました。
after crash -> EngineDisconnectedException
server exit code: 0xC0000005
editor (C#) is still alive.
```

上から順に起きたことを読みます。

`ping` は普通に往復します。`fail` ではサーバーが `ok: false` を返し、`EngineCommandException` になります。接続はそのままです。

`hang` ではサーバーが 3 秒止まるのに対し、呼び出し側は 1 秒で諦めて `TimeoutException` になります。そのあと 2.5 秒待つとサーバーが居眠りから戻って遅れた返事を書きますが、`_pending` に該当の `id` がないので、黙って捨てられます。次の `ping` が正しく返ったことで、遅れた返事が後続の要求と取り違えられていないと分かります。

最後の `crash` が本番です。サーバー側でアクセス違反が起き、プロセスが終了コード `0xC0000005`（アクセス違反）で消えます。C# 側では、`Disconnected` が呼ばれ、待っていた `crash` の呼び出しが `EngineDisconnectedException` になります。その後の `ping` も同じ例外で、ここからは再接続の話になります。そして、エディタのプロセスは最後まで生きています。

環境は、C++ が MinGW-w64 の g++ 14.2（`-std=c++23`）、C# が .NET SDK 10 でターゲットを `net8.0` にしたコンソール アプリです。`ServeOnce` と `EngineClient` は、上のコードのまま、コンパイルして実行して確かめました。nlohmann を使う `HandleRequest` は確かめていません。

## 通信の速さを見積もる

ではどれくらい遅くなるのでしょうか。C++ 側が固定の返事を返すだけの `ping` を直列に 10,000 回、`await` で往復させて測りました（Release ビルド、同じ PC、Windows 10）。3 回測って、10,000 回あたり 337〜384 ms、1 回あたり約 34〜38 μs でした。

第 31 章の表では P/Invoke の呼び出しを数十ナノ秒としていました。それと比べて、3 桁ほど大きい値です。

この差が効くのは命令を大量に送る場面です。1,000 個のオブジェクトの位置を 1 つずつ `set_position` で送ると、約 35 ms かかります。60 fps の 1 フレームは約 16.7 ms なので、2 フレーム分以上です。毎フレーム全部を送る設計は成り立ちません。

対策は 2 つあります。

1. 束ねる。`set_positions` のように、複数のオブジェクトをまとめて 1 つの命令にします。往復は 1 回で済みます（JSON を作る時間は別にかかります）。
2. 送らない。位置の計算やアニメーションはエンジン側で行い、エディタは「選択が変わった」「値を編集した」のような、人間の操作の速さの命令だけを送ります。

エディタの命令は、ほとんどが人間の操作の速さです。ドラッグ中のギズモの移動でも、毎フレーム 1 回の命令なら、35 μs は十分に小さい値です。問題になるのは、シーンの全体を毎フレーム同期するような設計に限られます。

## この先の章

この章で作った `EngineClient` は、まだ `IEngineService`（第 33 章）に繋がっていません。次の章で、`IEngineService` の実装をもう 1 つ（パイプ版）にして、ビューモデルがどちらを使っているかを知らないまま差し替えられるようにします。

ビューポートは、今のところ同じプロセスの子ウィンドウです。別プロセスのエンジンが描いた絵を WPF の中に出す方法は、第 56 章で扱います。子ウィンドウとして埋め込む方式は入力のキューが共有されるため、エンジンが固まるとエディタも固まる癖があります。そのため、この部では共有テクスチャを使います。

## よくあるミス

??? failure "メッセージが小さいときは動くのに、大きいと壊れる"
    `ReadFile` を 1 回呼んで、全部読めたと思い込んでいます。バイト モードのパイプは、届いた分だけで戻ることがあります。`ReadExact` のように、指定のバイト数が揃うまで繰り返してください。C# 側の `ReadAsync` でも同じなので、`ReadExactlyAsync` を使います。

??? failure "エンジンが落ちたのに、エディタの `await` が戻ってこない"
    切断を検出して、返事待ちの全員に例外を入れる処理（`ReadLoopAsync` の `finally`）がありません。読み取りのループが終わったときに、`_pending` の中身をすべて失敗にしてください。あわせて、`RequestAsync` に必ず時間切れを付けます。

??? failure "ConnectAsync が時間切れになる"
    エンジンがまだパイプを作っていません。エンジンを起動してから接続するまでの間に時間差があります。時間切れを少し長く取り、失敗したら、数回やり直すようにします。パイプの名前の綴りが C++ と C# で食い違っていても、同じ症状になります（C++ は `\\.\pipe\MiniEngine` と書き、C# は名前の `"MiniEngine"` だけを書きます）。

??? failure "返事が別の要求のものに見える"
    複数のタスクが同時に `WriteAsync` を呼んで、バイトが途中で交ざっています。書き込みを `SemaphoreSlim` で直列にして、長さと本文を 1 回の書き込みにまとめてください。

??? failure "Disconnected の中で画面を更新すると例外が出る"
    `Disconnected` は UI スレッドではないスレッドから呼ばれます。`Application.Current.Dispatcher.InvokeAsync(...)` で UI スレッドに戻してから、画面を触ります。

??? failure "エンジンを再起動しても、エディタが繋がらない"
    古いエンジンのプロセスが残っていて、パイプの名前を握っています。最大インスタンス数が 1 なので、新しいエンジンは `CreateNamedPipeW` に失敗します。エディタがエンジンを起動したなら、エディタの終了時（と再起動の前）にプロセスを終了させてください。

## この章のまとめ

- 同じプロセスにいる限り、C++ のクラッシュは C# を道連れにする。落ちても生きるには、エンジンを別のプロセスに出す。
- 別プロセスの関数を呼ぶ仕組みが RPC。遅く、失敗し、ポインターを渡せないので、API の形が変わる。
- 通信路は名前付きパイプ、中身は JSON。メッセージは「長さ + 本文」で区切り、要求と返事は `id` で対応づける。
- エンジンの「失敗」（`EngineCommandException`）と、エンジンの「消滅」（`EngineDisconnectedException`）を、別の例外にする。
- 手元では 1 往復が約 35 μs だった。大量の命令は束ねるか、エンジン側で完結させる。

次の章では、この `EngineClient` を `IEngineService` の実装として組み込みます。

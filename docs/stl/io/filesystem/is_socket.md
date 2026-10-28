---
title: std::filesystem::is_socket
summary: "パスがソケットかを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_socket

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

Unix 系の OS では、ネットワーク通信の窓口（ソケット）に、ファイルシステム上の名前が付くことがあります（Unix ドメイン ソケット）。ゲーム サーバーと管理ツールが、`/tmp/game.sock` のようなファイルで話し合う、という使い方です。

`std::filesystem::is_socket` は、<strong>パスがそのようなソケット ファイルか</strong>を調べます。通常のファイルやフォルダーなら `false` です。

!!! tip "ポイント"
    - `is_socket(p)` は、`p` がソケット ファイルなら `true`
    - Windows の通常の環境では、ほぼ `false`（Windows のソケットは名前付きファイルではない）
    - 存在しないパスは `false`。リンクは先をたどって判定する
    - 判定は [`status`](status.md) の結果の種類（`file_type::socket`）の確認

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### is_socket {#is_socket}

<span class="ver ver-17">C++17</span>

```cpp
bool is_socket(const path& p);
bool is_socket(const path& p, std::error_code& ec) noexcept;
bool is_socket(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::socket` と同じ判定です。Unix ドメイン ソケットが対象で、TCP や UDP のソケットは、ファイルシステム上に名前を持たないので、対象外です。

Windows には、Unix ドメイン ソケットに当たる物（AF_UNIX）がありますが、Windows の C++ 標準ライブラリは、ふつう `socket` とは判定せず、`false` になります。マルチプラットフォームのコードでは、「Windows では常に `false`」と考えて作ります。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";
  fs::create_directory("folder");

  std::println("通常のファイル: {}", fs::is_socket("plain.txt"));
  std::println("フォルダー: {}", fs::is_socket("folder"));
  std::println("存在しない: {}", fs::is_socket("missing"));
}
```

```text title="実行結果"
通常のファイル: false
フォルダー: false
存在しない: false
```

## ゲームでの使いどころ

Linux や macOS 向けに、ゲーム サーバーを作るときに使います。サーバーを起動する前に、前回の実行で消し忘れたソケット ファイルが残っていないかを `is_socket` で確かめ、残っていれば `remove` してから `bind` します（残っていると `bind` が失敗するため）。

Windows 専用のクライアント ゲームでは、ほぼ出番がありません。

## よくあるミス

??? failure "ネットワーク ソケットを調べられると思う"
    対象は、ファイルシステム上の名前を持つ Unix ドメイン ソケットだけです。TCP のソケットは、パスで表せません。

??? failure "Windows で `true` になると期待して分岐を書く"
    Windows では `false` が返るのがふつうです。OS ごとの処理は、別に分けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_fifo`](is_fifo.md) | 名前付きパイプ（FIFO）か |
| [`is_other`](is_other.md) | 通常のファイル、フォルダー、リンクのどれでもないか |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] Unix ドメイン ソケットのファイルか
    - [x] Windows ではほぼ `false`
    - [x] 存在しなければ `false`

## 関連ページ

- [cpprefjp: std::filesystem::is_socket](https://cpprefjp.github.io/reference/filesystem/is_socket.html)
- [cppreference: std::filesystem::is_socket](https://en.cppreference.com/w/cpp/filesystem/is_socket)

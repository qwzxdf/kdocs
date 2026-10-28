---
title: std::filesystem::is_fifo
summary: "パスが名前つきパイプ（FIFO）かを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_fifo

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

別のプログラムと、ファイルのような名前を通してデータをやり取りしたい。それも、ファイルに書き溜めるのではなく、書いた分を相手がすぐ読める「管」のようにしたい。Unix 系の OS には、そのための名前付きパイプ（FIFO）があります。

`std::filesystem::is_fifo` は、<strong>パスが名前付きパイプか</strong>を調べます。

!!! tip "ポイント"
    - `is_fifo(p)` は、`p` が名前付きパイプ（FIFO）なら `true`
    - Windows の名前付きパイプ（`\\.\pipe\...`）は、ファイルシステムのパスではないので、対象外
    - 存在しないパスは `false`。リンクは先をたどって判定する
    - データの出入りは、ふつうのファイルと同じ `fstream` で行う

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### is_fifo {#is_fifo}

<span class="ver ver-17">C++17</span>

```cpp
bool is_fifo(const path& p);
bool is_fifo(const path& p, std::error_code& ec) noexcept;
bool is_fifo(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::fifo` と同じ判定です。FIFO は、`mkfifo` コマンドや関数で作ります。標準の `std::filesystem` には、FIFO を作る関数はありません。

FIFO は、書き込む側と読む側が両方そろわないと、`open` が止まることがあります。`is_fifo` で見分けておけば、通常のファイルのつもりで開いて固まる、という事故を避けられます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  std::println("通常のファイル: {}", fs::is_fifo("plain.txt"));
  std::println("カレント ディレクトリ: {}", fs::is_fifo("."));
  std::println("存在しない: {}", fs::is_fifo("missing"));
}
```

```text title="実行結果"
通常のファイル: false
カレント ディレクトリ: false
存在しない: false
```

## ゲームでの使いどころ

Linux や macOS で、ゲームと外部ツール（ログビューアーやデバッグ コンソール）をつなぐときに使います。ツールが作った FIFO にゲームがログを書き込む、という構成です。書き込む前に `is_fifo` で、相手が用意した管かを確かめます。

フォルダーの走査で、通常のファイル以外が混ざっていないか調べる処理でも、`is_regular_file` と組み合わせて使います。Windows 専用のゲームでは、出番はほとんどありません。

## よくあるミス

??? failure "FIFO を通常のファイルとして開いて、固まる"
    相手がつながっていない FIFO を開くと、`open` が待ち続けます。`is_regular_file` で通常のファイルだけを対象にするのが安全です。

??? failure "Windows の名前付きパイプも調べられると思う"
    `\\.\pipe\name` は、ファイルシステムのパスではありません。Windows API（`CreateNamedPipe`）で扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_socket`](is_socket.md) | ソケット ファイルか |
| [`is_other`](is_other.md) | 通常のファイル、フォルダー、リンクのどれでもないか |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 名前付きパイプ（FIFO）か
    - [x] Windows では対象外
    - [x] 通常のファイルのつもりで開かない

## 関連ページ

- [cpprefjp: std::filesystem::is_fifo](https://cpprefjp.github.io/reference/filesystem/is_fifo.html)
- [cppreference: std::filesystem::is_fifo](https://en.cppreference.com/w/cpp/filesystem/is_fifo)

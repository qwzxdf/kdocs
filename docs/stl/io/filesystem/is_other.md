---
title: std::filesystem::is_other
summary: "パスが通常ファイル・フォルダ・シンボリックリンク以外かを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_other

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

フォルダーを走査すると、通常のファイルやフォルダーに混じって、リンクや特殊なファイル（ソケット、パイプ、デバイス）が出てくることがあります。通常のファイル、フォルダー、シンボリックリンクのどれでもない物をまとめて除外したい、というとき、いくつも `is_xxx` を並べるのは面倒です。

`std::filesystem::is_other` は、<strong>存在するが、通常のファイル、フォルダー、シンボリックリンクのどれでもない</strong>とき `true` になります。

!!! tip "ポイント"
    - `is_other(p)` は、ソケット、FIFO、ブロック デバイス、文字デバイスなどのとき `true`
    - 存在しないパスは `false`。通常のファイル、フォルダー、リンクも `false`
    - リンクは先をたどって判定する。リンクの先が特殊なファイルなら `true`
    - 個別に知りたいときは、`is_socket` などを使う

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### is_other {#is_other}

<span class="ver ver-17">C++17</span>

```cpp
bool is_other(const path& p);
bool is_other(const path& p, std::error_code& ec) noexcept;
bool is_other(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`exists(s) && !is_regular_file(s) && !is_directory(s) && !is_symlink(s)` と同じです。ここで、`status` は通常、リンクをたどるので、`is_symlink` が `true` になる場面は少なく、実質は<strong>「通常のファイルでもフォルダーでもない、存在する物」</strong>です。

存在しないものが `false` なのは、「その他」の中に「無い」は含まれないからです。「通常のファイルとして読める」を確かめたいなら、`!is_other` ではなく、`is_regular_file` を使います。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";
  fs::create_directory("folder");

  std::println("通常のファイル: {}", fs::is_other("plain.txt"));
  std::println("フォルダー: {}", fs::is_other("folder"));
  std::println("存在しない: {}", fs::is_other("missing"));
}
```

```text title="実行結果"
通常のファイル: false
フォルダー: false
存在しない: false
```

## ゲームでの使いどころ

フォルダーを走査して、読み込み対象のファイルを集めるときに、特殊なファイルを除外する目的で使います。ただし、ふつうは `is_regular_file` が `true` のものだけを拾えば足ります。`is_other` は、除外した物を「警告として報告したい」ときに便利です。

ログに「特殊なファイル `...` はスキップしました」と出したい、といった診断用の使い方が主です。

## よくあるミス

??? failure "存在しないものも `true` になると思う"
    存在しないパスは `false` です。「通常のファイルではない」を調べるなら `!is_regular_file(p)` です。

??? failure "`!is_other` を「ふつうのファイル」の判定に使う"
    フォルダーも `!is_other` になります。ふつうのファイルは `is_regular_file` で判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_regular_file`](is_regular_file.md) | 通常のファイルか |
| [`is_socket`](is_socket.md) | ソケットか |
| [`is_fifo`](is_fifo.md) | 名前付きパイプか |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 特殊な存在するファイルか
    - [x] 通常のファイル、フォルダー、リンクは `false`
    - [x] 存在しなければ `false`

## 関連ページ

- [cpprefjp: std::filesystem::is_other](https://cpprefjp.github.io/reference/filesystem/is_other.html)
- [cppreference: std::filesystem::is_other](https://en.cppreference.com/w/cpp/filesystem/is_other)

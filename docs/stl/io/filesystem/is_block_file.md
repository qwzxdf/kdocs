---
title: std::filesystem::is_block_file
summary: "パスがブロックデバイスかを調べる。"
order: 900
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_block_file

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

Unix 系の OS では、ディスクのような「ブロック単位で読み書きする装置」にも、`/dev/sda` のようなファイルの名前が付きます。ふつうのファイルと同じように `open` できますが、扱いを間違えると、ディスクの中身を壊します。

`std::filesystem::is_block_file` は、<strong>パスがブロック デバイスか</strong>を調べます。

!!! tip "ポイント"
    - `is_block_file(p)` は、`p` がブロック デバイスなら `true`
    - Windows には、ブロック デバイスのファイルがないので、ふつう `false`
    - 存在しないパスは `false`。リンクは先をたどって判定する
    - キーボードなどの「1 文字ずつ」の装置は [`is_character_file`](is_character_file.md)

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要と、[`path`](path.md) を先に読んでください。

## 関数の詳しい説明

### is_block_file {#is_block_file}

<span class="ver ver-17">C++17</span>

```cpp
bool is_block_file(const path& p);
bool is_block_file(const path& p, std::error_code& ec) noexcept;
bool is_block_file(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::block` と同じ判定です。ハード ディスク、SSD、USB メモリ、ループバック デバイスなどが、ブロック デバイスの例です。

ゲームでこのファイルを直接開くことは、ほとんどありません。ユーザーが入力したパスを検査して、「ふつうのファイルでないものを開かない」ためのチェックの 1 つとして知っておきます。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("plain.txt") << "x";

  std::println("通常のファイル: {}", fs::is_block_file("plain.txt"));
  std::println("カレント ディレクトリ: {}", fs::is_block_file("."));
}
```

```text title="実行結果"
通常のファイル: false
カレント ディレクトリ: false
```

## ゲームでの使いどころ

ユーザーが指定したパスを開く前の検査で使います。MOD のフォルダーとして `/dev/sda` のような装置が指定されると、読み込み処理が意図しない動きをします。`is_regular_file` が `true` のものだけを開く、とすれば、ブロック デバイスも自然に除外されます。

`is_block_file` を単独で使うのは、ディスク ツールのような特殊なプログラムだけです。

## よくあるミス

??? failure "ブロック デバイスを通常のファイルとして書き込む"
    ディスクの中身を壊すおそれがあります。ユーザーの入力したパスに書き込む前に、`is_regular_file` で確かめます。

??? failure "Windows のドライブ（`C:\\`）が `true` になると思う"
    ドライブ文字は、ファイルシステムのブロック デバイスのファイルではなく、フォルダー（ルート）として扱われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_character_file`](is_character_file.md) | 文字デバイスか |
| [`is_regular_file`](is_regular_file.md) | 通常のファイルか |
| [`is_other`](is_other.md) | 通常のファイル、フォルダー、リンクのどれでもないか |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ブロック デバイスか
    - [x] Windows では `false`
    - [x] 通常のファイルだけ開くなら `is_regular_file`

## 関連ページ

- [cpprefjp: std::filesystem::is_block_file](https://cpprefjp.github.io/reference/filesystem/is_block_file.html)
- [cppreference: std::filesystem::is_block_file](https://en.cppreference.com/w/cpp/filesystem/is_block_file)

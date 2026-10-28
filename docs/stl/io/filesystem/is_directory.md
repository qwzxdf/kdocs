---
title: std::filesystem::is_directory
summary: "フォルダか調べる。"
order: 12
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::is_directory

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

ユーザーが指定したパスが、フォルダーなのか、ファイルなのか。ドラッグ アンド ドロップされたものがフォルダーなら、中身を取り込む。ファイルなら、そのまま開く。この分岐に使うのが、`std::filesystem::is_directory` です。

<strong>パスがフォルダー</strong>であるかを調べます。

!!! tip "ポイント"
    - `is_directory(p)` は、`p` がフォルダーなら `true`
    - 存在しないパスは `false`。例外にはならない
    - リンクは先をたどって判定する。フォルダーを指すシンボリックリンクは `true`
    - ファイルの判定は `is_regular_file`。ファイルでなければフォルダー、とは限らない

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### is_directory {#is_directory}

<span class="ver ver-17">C++17</span>

```cpp
bool is_directory(const path& p);
bool is_directory(const path& p, std::error_code& ec) noexcept;
bool is_directory(file_status s) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` | `const path&` | 調べるパス |
| `s` | `file_status` | すでに取得した状態 |
| `ec` | `std::error_code&` | 失敗の理由の受け取り先 |

`status(p).type() == file_type::directory` と同じです。存在しない、通常のファイル、デバイスなどのときは、`false` を返します。

ファイルかフォルダーかの 2 択で考えがちですが、現実のパスには、存在しない、デバイス、ソケット、といった第 3 の状態があります。`!is_directory(p)` を「ファイルである」と読み替えると、存在しないパスも「ファイル」になってしまいます。ファイルかどうかは、`is_regular_file` で直接調べます。

フォルダーを走査している途中の項目には、`directory_entry::is_directory()` を使うほうが速くなります。走査のときに得た情報を、そのまま使えるからです。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("file.txt") << "x";
  fs::create_directory("folder");

  for (const char* name : {"file.txt", "folder", "missing"}) {
    std::println("{}: フォルダー={} ファイル={}", name,
                 fs::is_directory(name), fs::is_regular_file(name));
  }
}
```

```text title="実行結果"
file.txt: フォルダー=false ファイル=true
folder: フォルダー=true ファイル=false
missing: フォルダー=false ファイル=false
```

## ゲームでの使いどころ

ドラッグ アンド ドロップされたパスの処理や、コマンドライン引数でフォルダーが渡されたときの分岐に使います。フォルダーなら中のファイルを走査して取り込み、ファイルなら 1 つだけ取り込む、という流れです。

保存先のフォルダーが存在するかの確認にも使います。`create_directories` を呼ぶ前に確認すれば、無駄な処理を避けられます（`create_directories` は、すでにあれば何もせず `false` を返すので、確認を省くこともできます）。

## よくあるミス

??? failure "`!is_directory` を「ファイルである」と読む"
    存在しないパスも `!is_directory` になります。ファイルかどうかは `is_regular_file` で調べます。

??? failure "走査の途中で、毎回 `is_directory(path)` を呼び、遅くなる"
    `directory_entry` の `is_directory()` なら、走査時の情報を使えて、追加の問い合わせが減ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_regular_file`](is_regular_file.md) | 通常のファイルか |
| [`exists`](exists.md) | 種類を問わず、存在するか |
| [`directory_entry`](directory_entry.md) | 走査の途中の項目。種類の判定を持っている |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] フォルダーか
    - [x] 存在しなければ `false`
    - [x] `!is_directory` はファイルの意味ではない

## 関連ページ

- [cpprefjp: std::filesystem::is_directory](https://cpprefjp.github.io/reference/filesystem/is_directory.html)
- [cppreference: std::filesystem::is_directory](https://en.cppreference.com/w/cpp/filesystem/is_directory)

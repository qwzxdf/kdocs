---
title: std::filesystem::file_size
summary: "ファイルの大きさ（バイト数）を取得する。"
order: 13
group: ファイル操作（std::filesystem）
tags:
  - 入出力・文字列
---

# std::filesystem::file_size

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-17">C++17</span>
`#include <filesystem>`
</div>

`std::filesystem::file_size` は、**ファイルの大きさをバイト数で返す**関数です。読み込む前にバッファを用意するときなどに使います。フォルダに使うとエラーです。

!!! tip "ポイント"
    - 戻り値は `std::uintmax_t`。
    - ファイルが無いと例外。`error_code` 版なら例外なし。

!!! info "このページを読む前に"
    [`std::filesystem`](../filesystem.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### file_size {#file_size}

```cpp
std::uintmax_t file_size(const path& p);
```

- ファイルの大きさ（バイト）。フォルダや存在しないファイルだと例外

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>

int main() {
  namespace fs = std::filesystem;
  std::ofstream("fs_demo.txt") << "hello";
  std::println("{}", fs::file_size("fs_demo.txt"));
  fs::remove("fs_demo.txt");
}
```

```text title="実行結果"
5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 読み込み用のバッファを確保する | `std::vector<char> buf(fs::file_size(p));` |

## よくあるミス

??? failure "フォルダに使う"
    エラーです。ファイルにだけ使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`space`](space.md) | ディスクの空き容量 |

## コンパイラ対応

C++17 の機能です。GCC 9 / Clang 9 / MSVC 19.14 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルのバイト数
    - [x] フォルダにはエラー
    - [x] バッファ確保に使う

## 関連ページ

- [cpprefjp: std::filesystem::file_size](https://cpprefjp.github.io/reference/filesystem/file_size.html)
- [cppreference: std::filesystem::file_size](https://en.cppreference.com/w/cpp/filesystem/file_size)

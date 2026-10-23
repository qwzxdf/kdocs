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

ファイルを読み込む前に、必要なバッファの大きさを知りたい。ファイルを開いて、最後まで読んで、数えるのは無駄です。`std::filesystem::file_size` は、ファイルの大きさをバイト数で返す関数です。読み込む前にバッファを用意する、ロードの進行度を計算する、といった用途に使います。フォルダに使うとエラーです。

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

バイナリのアセットを読み込む前に、バッファを `std::vector<char> buf(fs::file_size(path));` で確保します。大きさが分かっているので、再確保なしで読み込めます。

ロード画面で、全アセットの合計サイズを先に求め、読み終えたサイズとの比で進行度を出します。

ファイルが無いと例外です。`error_code` を渡す版なら、例外なしで結果を受け取れます。サイズが 0 のファイルと、エラーを区別するために、エラーコードで確かめます。

## よくあるミス

??? failure "フォルダに使う"
    エラーです。ファイルにだけ使います。

??? failure "存在しないファイルで例外が出る"
    ファイルが無いと `filesystem_error` を投げます。先に `exists` で確かめるか、`error_code` を渡す版を使います。

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

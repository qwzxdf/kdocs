---
title: std::print
summary: "書式に従って、そのまま画面（標準出力）に出す。println は末尾に改行を付ける。"
order: 46
tags:
  - ユーティリティ
---

# std::print

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
<span class="ver ver-23">C++23</span>
`#include <print>`
</div>

`std::println` と `std::print` は、**`{}` の場所に値を埋め込んで、そのまま画面（標準出力）に出す**関数です。`println` は最後に改行を付けます。`printf` の安全な後継で、書式と引数の型が合わないとコンパイルエラーになります。書式の書き方は [`std::format`](format.md) と同じです。

!!! tip "ポイント"
    - 普段は **`std::println("HP {}/{}", hp, max_hp);`** と書けばよい。改行が要らないときだけ `std::print`。
    - `std::println(stderr, ...)` で標準エラー出力に出せる。
    - 書式文字列は**コンパイル時に決まっている**必要がある（実行時に決めるなら [`std::vformat`](vformat.md)）。
    - Windows のコンソールでも、UTF-8 の文字列を正しく出せる（`/utf-8` が必要）。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) などは不要です。書式の指定は [std::format](format.md) のページにまとめてあります。

## 関数の詳しい説明

### std::println <span class="ver ver-23">C++23</span> {#println data-toc-label="std::println"}

```cpp
template <class... Args>
void println(std::format_string<Args...> fmt, Args&&... args);
template <class... Args>
void println(std::FILE* stream, std::format_string<Args...> fmt, Args&&... args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `std::FILE*` | 出力先。省略すると `stdout`。`stderr` も指定できる |
| `fmt` | 書式文字列 | `{}` を含む文字列。**コンパイル時の定数** |
| `args` | 何個でも | `{}` に順番に埋め込む値 |

- 出力して最後に改行します。UTF-8 の日本語も正しく出ます（Windows のコンソールでも）

```cpp
#include <cstdio>
#include <print>

int main() {
  std::println("通常の出力");
  std::println(stderr, "エラー出力: {}", 404);  // stderr は実行結果欄には出ないことがある
}
```

```text title="実行結果"
通常の出力
```

### std::print <span class="ver ver-23">C++23</span> {#print data-toc-label="std::print"}

```cpp
template <class... Args>
void print(std::format_string<Args...> fmt, Args&&... args);
```

- `println` の改行なし版です

```cpp
#include <print>

int main() {
  for (int i = 0; i < 3; ++i) {
    std::print("{} ", i);
  }
  std::print("\n");
}
```

```text title="実行結果"
0 1 2 
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| デバッグ表示・ログ | `std::println("{} HP {}/{}", name, hp, max_hp);` |
| エラーを標準エラー出力へ | `std::println(stderr, "エラー: {}", code);` |

## よくあるミス

??? failure "古いコンパイラで使えない"
    `<print>` は C++23 で、GCC 14 / MSVC 19.37 / Clang 18 以降です。使えないときは `std::cout << std::format(...) << "\n"` で代用できます。

??? failure "書式文字列を変数にする"
    `std::println(fmt, x)` の `fmt` は定数でなければなりません。実行時の文字列には `std::vformat` を使います。

??? failure "波かっこそのものを出す"
    `{` と `}` そのものは `{{` と `}}` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](format.md) | 文字列を作る（出力はしない） |
| [`std::cout`](../io/cout.md) | 従来の出力。`<<` でつなぐ |
| `printf` | C 由来。型の安全がない |

## コンパイラ対応

C++23 の機能です。GCC 14 / Clang 18 / MSVC 19.37（VS 2022 17.7）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 表示は `std::println("...{}", x);`
    - [x] 書式は `std::format` と同じ
    - [x] C++23（`<print>`）

## 関連ページ

- [cpprefjp: std::println](https://cpprefjp.github.io/reference/print/println.html)
- [cppreference: std::println](https://en.cppreference.com/w/cpp/io/println)

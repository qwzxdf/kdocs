---
title: std::fprintf
summary: "書式を指定して、ファイルに出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::fprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`printf` は標準出力に出しますが、`fprintf` は出力先の `FILE*` を指定できます。ファイルにも `stdout` にも `stderr` にも、同じ書式で書けます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fprintf {#fprintf}

```cpp
int fprintf(std::FILE* stream, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 出力先 |
| `format` | const char* | 書式文字列（`%d` `%s` など） |
| `...` | 可変引数 | 書式に対応する値 |

- 戻り値: 書き込んだ文字数。失敗したら負の値
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  std::fprintf(stdout, "%d-%s\n", 1, "a");
}
```

```text title="実行結果"
1-a
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ログファイルに書式つきで書く |

## よくあるミス

??? failure "書式と型が合わない"
    `%d` に `double` を渡すなど、型が合わないと未定義動作です。新しいコードでは型安全な `std::print` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`printf`](printf.md) | 標準出力へ |
| [`sprintf`](sprintf.md) | バッファへ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式を指定して、ファイルに出力する
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fprintf](https://cpprefjp.github.io/reference/cstdio/fprintf.html)
- [cppreference: std::fprintf](https://en.cppreference.com/w/cpp/io/c/fprintf)

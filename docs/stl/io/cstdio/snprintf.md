---
title: std::snprintf
summary: "書式を指定して、大きさを決めた文字配列に書き込む（あふれない）。"
order: 900
tags:
  - 入出力・文字列
---

# std::snprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cstdio>`
</div>

`sprintf` は配列の大きさを確かめないため、あふれる危険があります。`snprintf` は、書き込む最大のバイト数を指定でき、あふれた分は切り捨てて、必ず終端文字を付けます。戻り値は「切り捨てなければ書けたはずの長さ」なので、`nullptr` と 0 を渡して、必要な大きさを先に調べる使い方もできます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::snprintf {#snprintf}

```cpp
int snprintf(char* buffer, std::size_t bufsz, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | char* | 書き込み先（`nullptr` も可） |
| `bufsz` | size_t | 書き込める最大のバイト数（終端を含む） |
| `format` | const char* | 書式文字列 |

- 戻り値: 書けたはずの文字数（終端を除く）
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  char buf[8];
  int n = std::snprintf(buf, sizeof buf, "%d-%s", 12, "abcdefgh");
  std::println("{} {}", buf, n);
}
```

```text title="実行結果"
12-abcd 11
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 固定長のバッファに、安全に文字列を組み立てる |

## よくあるミス

??? failure "戻り値を書き込んだ長さと思う"
    戻り値は、切り捨てがなかった場合の長さです。`n >= bufsz` なら、切り捨てられています。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sprintf`](sprintf.md) | 大きさを確かめない |
| [`std::format_to_n`](../../utilities/format_to.md) | 型安全な書き方 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式を指定して、大きさを決めた文字配列に書き込む（あふれない）
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::snprintf](https://cpprefjp.github.io/reference/cstdio/snprintf.html)
- [cppreference: std::snprintf](https://en.cppreference.com/w/cpp/io/c/snprintf)

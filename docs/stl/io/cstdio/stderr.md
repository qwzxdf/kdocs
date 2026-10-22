---
title: std::stderr
summary: "標準エラー出力を表す FILE*。"
order: 900
tags:
  - 入出力・文字列
---

# std::stderr

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

エラーメッセージ用の出力です。バッファなしで、すぐに書き出されます。普通の出力（`stdout`）と分けられるので、リダイレクトしても画面に出せます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::stderr {#stderr}

```cpp
extern std::FILE* stderr;
```

- 戻り値: 標準エラー出力の `FILE*`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  std::fputs("error\n", stderr);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | エラーメッセージの出力 |

## よくあるミス

??? failure "`stdout` と順序が混ざる"
    `stdout` はバッファされるため、`stderr` と出力順が前後することがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`stdout`](stdout.md) | 標準出力 |
| [`std::cerr`](../cerr.md) | C++ の標準エラー出力 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準エラー出力を表す FILE*
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::stderr](https://cpprefjp.github.io/reference/cstdio/stderr.html)
- [cppreference: std::stderr](https://en.cppreference.com/w/cpp/io/c/stderr)

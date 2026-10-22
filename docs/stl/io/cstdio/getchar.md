---
title: std::getchar
summary: "標準入力から 1 文字を読む。"
order: 900
tags:
  - 入出力・文字列
---

# std::getchar

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`getc(stdin)` と同じです。ゲームでは使わず、コンソールの簡単な入力待ちで使われます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::getchar {#getchar}

```cpp
int getchar();
```

- 戻り値: 読んだ文字。終端やエラーなら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  int c = std::getchar();
  std::println("{}", c != EOF);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | コンソールで Enter 待ち |

## よくあるミス

??? failure "改行が残る"
    `scanf` の後の改行が残ることがあります。`getchar` で捨てます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetc`](fgetc.md) | ファイルから |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準入力から 1 文字を読む
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::getchar](https://cpprefjp.github.io/reference/cstdio/getchar.html)
- [cppreference: std::getchar](https://en.cppreference.com/w/cpp/io/c/getchar)

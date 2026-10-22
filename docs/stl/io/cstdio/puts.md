---
title: std::puts
summary: "標準出力に文字列と改行を書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::puts

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

文字列を標準出力に書き、最後に改行を付けます。書式を使わない単純な出力に便利です。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::puts {#puts}

```cpp
int puts(const char* str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const char* | 書く文字列 |

- 戻り値: 成功なら負でない値、失敗なら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  std::puts("hello");
}
```

```text title="実行結果"
hello
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | デバッグメッセージを 1 行出す |

## よくあるミス

??? failure "`fputs` と取り違える"
    `puts` は改行を付け、`fputs` は付けません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputs`](fputs.md) | 改行なし |
| [`printf`](printf.md) | 書式つき |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準出力に文字列と改行を書く
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::puts](https://cpprefjp.github.io/reference/cstdio/puts.html)
- [cppreference: std::puts](https://en.cppreference.com/w/cpp/io/c/puts)

---
title: BUFSIZ
summary: "標準のバッファの大きさ（バイト）。"
order: 900
tags:
  - 入出力・文字列
---

# BUFSIZ

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`setbuf` に渡す配列の、必要な大きさです。実装ごとに違いますが、最低 256 です。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### BUFSIZ {#bufsiz}

```cpp
#define BUFSIZ /* 実装定義（256 以上） */
```

- 戻り値: バッファの大きさ
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::println("{}", BUFSIZ >= 256);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `setbuf` のバッファを用意する |

## よくあるミス

??? failure "固定値を決め打ちする"
    実装ごとに値が違います。`BUFSIZ` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setbuf`](setbuf.md) | バッファを設定する |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準のバッファの大きさ（バイト）
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: BUFSIZ](https://cpprefjp.github.io/reference/cstdio/bufsiz.html)
- [cppreference: BUFSIZ](https://en.cppreference.com/w/cpp/io/c/BUFSIZ)

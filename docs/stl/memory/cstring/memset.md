---
title: memset
summary: "メモリの範囲を、同じバイト値で埋める。"
order: 2
group: C の文字列・メモリ関数（<cstring>）
tags:
  - メモリ
---

# memset

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cstring>`
</div>

`memset` は、**メモリの範囲を、1 バイトの値で埋める**関数です。構造体を 0 で初期化するときによく使います。`int` の配列を `1` で埋める用途には使えません（1 バイトごとに埋めるため）。

!!! tip "ポイント"
    - 0 で埋めるのが主な用途。
    - `float` を 0 で埋めるのは OK（全ビット 0 が 0.0）。
    - C++ では `T x{};` の値初期化が安全。

!!! info "このページを読む前に"
    [ポインタ](../../../basics/pointer.md) が分かると読みやすいです。

## 関数の詳しい説明

### memset {#memset}

```cpp
void* memset(void* dest, int ch, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | `void*` | 埋める先頭 |
| `ch` | `int` | 埋めるバイトの値（`unsigned char` に変換される） |
| `count` | `std::size_t` | 埋める**バイト数** |

- 戻り値: `dest`
- **1 バイトずつ**同じ値で埋めます。`memset(a, 1, sizeof(a))` で `int` の配列を埋めると、各要素は `1` ではなく `0x01010101` になります。**0 で埋めるとき以外は、基本使いません**（`std::fill` を使う）
- 浮動小数点やポインタを 0 で埋めると、環境によっては 0.0 や `nullptr` にならないことがあります（実際のゲーム機・PC ではなります）
- クラスのオブジェクトに使うと、中身（ポインタや仮想関数テーブル）を壊します。**`std::string` や仮想関数を持つクラスに `memset` してはいけません**

## 実際に動かしてみる

```cpp
#include <cstring>
#include <print>

int main() {
  char buf[4];
  std::memset(buf, 'x', 3);
  buf[3] = '\0';
  std::println("{}", buf);
}
```

```text title="実行結果"
xxx
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パケット構造体を 0 で初期化する | `memset(&packet, 0, sizeof(packet))` |

## よくあるミス

??? failure "int 配列を 1 で埋める"
    バイトごとに 1 で埋まるので、各要素は 0x01010101 になります。`std::fill` を使います。

??? failure "非トリビアルな型に使う"
    コンストラクタを破壊します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::fill`](../../algorithms/fill.md) | 型を意識して埋める |

## コンパイラ対応

C 由来の関数です。C++ のどの版でも使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バイト値で埋める
    - [x] 0 初期化が主な用途
    - [x] `T x{}` のほうが安全

## 関連ページ

- [cpprefjp: memset](https://cpprefjp.github.io/reference/cstring/memset.html)
- [cppreference: memset](https://en.cppreference.com/w/cpp/string/byte/memset)

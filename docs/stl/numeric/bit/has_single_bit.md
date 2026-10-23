---
title: std::has_single_bit
summary: "ビットが 1 つだけ立っているか（2 のべき乗か）を調べる。"
order: 2
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::has_single_bit

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

バッファの大きさが 2 の累乗か。ハッシュテーブルやリング バッファは、大きさが 2 の累乗だと、剰余を `& (n - 1)` で速く計算できるので、その前提を守っているか検査したくなります。

`std::has_single_bit` は、<strong>値が 2 の累乗か</strong>（1 のビットがちょうど 1 つか）を返します。

!!! tip "ポイント"
    - `std::has_single_bit(64u)` は `true`、`(100u)` は `false`
    - 0 は 2 の累乗ではないので `false`
    - 符号なし整数型だけが対象
    - `popcount(x) == 1` と同じ意味

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::has_single_bit {#has_single_bit}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr bool has_single_bit(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 対象の値 |

戻り値は、`x` の 1 のビットがちょうど 1 つなら `true`、そうでなければ `false` です。1、2、4、8、16 …がそれにあたります。0 は 1 のビットが 0 個なので `false` です。

古くから知られた書き方 `(x & (x - 1)) == 0` は、0 のときも `true` になる落とし穴がありました。`has_single_bit` はこの点を正しく扱います。

符号なし整数型だけを受け取ります。

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("64  -> {}", std::has_single_bit(64u));
  std::println("100 -> {}", std::has_single_bit(100u));
  std::println("0   -> {}", std::has_single_bit(0u));
}
```

```text title="実行結果"
64  -> true
100 -> false
0   -> false
```

## ゲームでの使いどころ

2 の累乗の大きさが前提のデータ構造で、引数を検査します。

```cpp
assert(std::has_single_bit(capacity));   // リング バッファの容量は 2 の累乗
const std::size_t index = position & (capacity - 1);   // 剰余をビット演算で
```

## よくあるミス

??? failure "0 を 2 の累乗と扱ってしまう"
    `has_single_bit(0)` は `false` です。

??? failure "符号つき整数を渡してコンパイルエラーになる"
    符号なしにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_ceil`](bit_ceil.md) | 以上で最小の 2 の累乗 |
| [`bit_floor`](bit_floor.md) | 以下で最大の 2 の累乗 |
| [`popcount`](popcount.md) | 1 のビットの数 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `has_single_bit(x)` は 2 の累乗か
    - [x] 0 は `false`
    - [x] `popcount(x) == 1` と同じ

## 関連ページ

- [cpprefjp: std::has_single_bit](https://cpprefjp.github.io/reference/bit/has_single_bit.html)
- [cppreference: std::has_single_bit](https://en.cppreference.com/w/cpp/numeric/has_single_bit)

---
title: std::countl_zero
summary: "上位（左）から数えて、連続する 0 のビット数を数える。"
order: 7
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::countl_zero

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

整数の上位から数えて、0 のビットが何個続いているか。値の「桁数」に近い情報で、2 進数での桁（ビット幅）を求める、最上位ビットの位置を探す、といった処理の土台になります。

!!! tip "ポイント"
    - `std::countl_zero(1u)` は、32 ビット整数で 31
    - 0 を渡すと型のビット幅（32 ビットなら 32）
    - 符号なし整数型だけが対象
    - `bit_width` の補数にあたる

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::countl_zero {#countl_zero}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr int countl_zero(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 対象の値 |

`std::countl_zero(x)` は、`x` の最上位ビットから見て、連続する 0 の数を返します（leading zero count）。`x` が 0 なら、型のビット幅（`uint32_t` なら 32）を返します。最上位ビットが 1 なら 0 です。

`std::bit_width(x)` は、`型の幅 − countl_zero(x)` と同じ値です。最上位の 1 のビットの位置を知りたいなら、`bit_width(x) - 1` が使えます。

CPU の `lzcnt` 命令や、同様の命令に直接対応するので速いです。

符号なし整数型だけが対象です。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::println("countl_zero(1) = {}", std::countl_zero(std::uint32_t{1}));
  std::println("countl_zero(0) = {}", std::countl_zero(std::uint32_t{0}));
  std::println("countl_zero(0x80000000) = {}", std::countl_zero(std::uint32_t{0x80000000}));
}
```

```text title="実行結果"
countl_zero(1) = 31
countl_zero(0) = 32
countl_zero(0x80000000) = 0
```

## ゲームでの使いどころ

最上位ビットの位置を探すのに使います。

```cpp
// 32 ビット値 x (x != 0) の最上位の 1 の位置
const int top_bit = 31 - std::countl_zero(x);
```

## よくあるミス

??? failure "0 のときの戻り値を忘れる"
    0 を渡すと型のビット幅を返します。0 の場合は別に扱うか、`bit_width` を使います。

??? failure "符号つき整数を渡してコンパイルエラーになる"
    符号なしに直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`countl_one`](countl_one.md) | 上位の 1 の連続数 |
| [`bit_width`](bit_width.md) | 値を表すのに必要なビット数 |
| [`countr_zero`](countr_zero.md) | 下位の 0 の連続数 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `countl_zero(x)` は上位から続く 0 の数
    - [x] 0 なら型のビット幅
    - [x] `bit_width` と補数の関係

## 関連ページ

- [cpprefjp: std::countl_zero](https://cpprefjp.github.io/reference/bit/countl_zero.html)
- [cppreference: std::countl_zero](https://en.cppreference.com/w/cpp/numeric/countl_zero)

---
title: std::bit_width
summary: "値を表すのに必要なビット数を返す。"
order: 5
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::bit_width

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`std::bit_width` は、**値を表すのに必要なビット数**を返す関数です。`bit_width(5)`（`101`）は 3、`bit_width(0)` は 0 です。「2 を底とする対数（切り捨て）+ 1」にあたり、整数の `log2` として使えます。

!!! tip "ポイント"
    - 整数の `floor(log2(x)) + 1`。
    - `std::log2` より正確で速い。
    - ミップマップの段数などに。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::bit_width {#bit_width}

```cpp
template <class T>
constexpr int bit_width(T x) noexcept;
```

- `x` を表すのに必要なビット数（0 なら 0）。`bit_width(x) - 1` が「2 を底とする対数（切り捨て）」

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{} {}", std::bit_width(5u), std::bit_width(0u));
}
```

```text title="実行結果"
3 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ミップマップの段数 | `std::bit_width(std::max(w, h))` |

## よくあるミス

??? failure "0 の結果"
    0 を渡すと 0 を返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log2`](../cmath/log2.md) | 小数の対数 |
| [`countl_zero`](countl_zero.md) | 上位の 0 の数 |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 必要なビット数
    - [x] 整数の log2
    - [x] 0 は 0

## 関連ページ

- [cpprefjp: std::bit_width](https://cpprefjp.github.io/reference/bit/bit_width.html)
- [cppreference: std::bit_width](https://en.cppreference.com/w/cpp/numeric/bit_width)

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

`std::countl_zero` は、**最上位のビットから数えて、連続している 0 の数**を返す関数です。値の大きさ（何ビット目まであるか）を調べるのに使えます。`countl_zero(1u)`（32 ビット）は 31 です。

!!! tip "ポイント"
    - `bit_width(x) = 型のビット数 − countl_zero(x)`。
    - 0 を渡すと、型のビット数全部。
    - 最上位の立っているビットの位置を探すのに使う。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::countl_zero {#countl_zero}

```cpp
template <class T>
constexpr int countl_zero(T x) noexcept;
```

- 一番上の位から続く 0 の数

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{} {}", std::countl_zero(1u), std::countl_zero(0u));  // 32 ビットの unsigned の場合
}
```

```text title="実行結果"
31 32
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 最上位のビットの位置 | `31 - std::countl_zero(x)` |

## よくあるミス

??? failure "型のビット数を忘れる"
    `uint8_t` と `uint32_t` で結果が違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`countr_zero`](countr_zero.md) | 下位から数える |
| [`countl_one`](countl_one.md) | 1 を数える |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 上位から連続する 0 の数
    - [x] 0 を渡すと全ビット数
    - [x] 最上位ビットの位置を探せる

## 関連ページ

- [cpprefjp: std::countl_zero](https://cpprefjp.github.io/reference/bit/countl_zero.html)
- [cppreference: std::countl_zero](https://en.cppreference.com/w/cpp/numeric/countl_zero)

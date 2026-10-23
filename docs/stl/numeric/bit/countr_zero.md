---
title: std::countr_zero
summary: "下位（右）から数えて、連続する 0 のビット数を数える。"
order: 8
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::countr_zero

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

2 進数で、下位から数えて 0 が何個続くか。これは、「2 で何回割り切れるか」と同じ意味です。ビットマスクで立っている最も下位のビットの位置を探す、アドレスが何バイトに揃っているか調べる、といった処理に使います。

!!! tip "ポイント"
    - `std::countr_zero(8u)` は 3（下位の 0 が 3 個）
    - 0 を渡すと型のビット幅
    - `x` が 2 で何回割り切れるかに等しい
    - 立っているビットを順に取り出すループに使える

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::countr_zero {#countr_zero}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr int countr_zero(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 符号なし整数型 | 対象の値 |

`std::countr_zero(x)` は、`x` の最下位ビットから見て、連続する 0 の数を返します（trailing zero count）。`x` が 0 なら、型のビット幅を返します。`x` が奇数なら 0 です。

`x` が 0 でないとき、これは `x` に含まれる 2 の因数の個数です。8（`0b1000`）は 3、12（`0b1100`）は 2 です。

最も下位の 1 のビットの位置が分かるので、ビットマスクで管理した集合から、要素を 1 つずつ取り出すループに使えます。

## 実際に動かしてみる

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::println("countr_zero(8) = {}", std::countr_zero(std::uint32_t{8}));
  std::println("countr_zero(1) = {}", std::countr_zero(std::uint32_t{1}));
  std::println("countr_zero(0) = {}", std::countr_zero(std::uint32_t{0}));
}
```

```text title="実行結果"
countr_zero(8) = 3
countr_zero(1) = 0
countr_zero(0) = 32
```

## ゲームでの使いどころ

ビットマスクで表した集合から、立っているビットの位置を順に取り出すときに使います。

```cpp
std::uint32_t mask = 0b101000;
while (mask != 0) {
  const int index = std::countr_zero(mask);   // 最も下位の 1 の位置
  Process(index);
  mask &= mask - 1;                           // その 1 を消す
}
```

## よくあるミス

??? failure "0 のときの戻り値を忘れて、無限ループになる"
    0 を渡すと型のビット幅を返します。ループでは、0 になったら終わりにします。

??? failure "符号つき整数を渡してコンパイルエラーになる"
    符号なしに直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`countr_one`](countr_one.md) | 下位の 1 の連続数 |
| [`countl_zero`](countl_zero.md) | 上位の 0 の連続数 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 9 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `countr_zero(x)` は下位から続く 0 の数
    - [x] 0 なら型のビット幅
    - [x] 最下位の 1 の位置を得て、順に取り出せる

## 関連ページ

- [cpprefjp: std::countr_zero](https://cpprefjp.github.io/reference/bit/countr_zero.html)
- [cppreference: std::countr_zero](https://en.cppreference.com/w/cpp/numeric/countr_zero)

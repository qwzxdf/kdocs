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

`std::countr_zero` は、**最下位のビットから数えて、連続している 0 の数**を返す関数です。**最初に立っているビットの位置（番号）**を求めるのに便利です。`countr_zero(8u)`（`1000`）は 3 です。

!!! tip "ポイント"
    - 最初に立っているビットの番号を取れる。
    - 0 を渡すと、型のビット数全部。
    - ビットマスクの中の要素を順に取り出すループで使う。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::countr_zero {#countr_zero}

```cpp
template <class T>
constexpr int countr_zero(T x) noexcept;
```

- 一番下の位から続く 0 の数 = 一番下にある 1 の位置。フラグの中から「次に立っているビット」を探すのに使えます

<div class="anim" data-label="std::countr_zero(0b1000u)">
1 0 0 0 # ビット列
1 *0 *0 *0 # 右から続く 0 を数える（3）
</div>

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::uint32_t pending = 0b0010'1000;  // 3 番と 5 番の処理が残っている
  while (pending != 0) {
    int index = std::countr_zero(pending);  // 一番下の 1 の位置
    std::print("{} ", index);
    pending &= pending - 1;                 // 一番下の 1 を消す
  }
  std::println("");
}
```

```text title="実行結果"
3 5 
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ビットマスクの、立っているビットを順に処理する | `i = std::countr_zero(mask); mask &= mask - 1;` |

## よくあるミス

??? failure "0 を渡して無限ループ"
    `mask != 0` を確かめてから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`countl_zero`](countl_zero.md) | 上位から数える |
| [`popcount`](popcount.md) | 立っている数 |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 下位から連続する 0 の数
    - [x] 最初に立つビットの番号
    - [x] マスクの走査に使う

## 関連ページ

- [cpprefjp: std::countr_zero](https://cpprefjp.github.io/reference/bit/countr_zero.html)
- [cppreference: std::countr_zero](https://en.cppreference.com/w/cpp/numeric/countr_zero)

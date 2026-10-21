---
title: std::popcount
summary: "立っているビット（1）の数を数える。"
order: 1
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::popcount

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`std::popcount` は、**整数の中で 1 になっているビットの数**を返す関数です。フラグがいくつ立っているか、ビットマスクの要素数を数えるときに使います。CPU の専用命令で速く動きます。

!!! tip "ポイント"
    - 符号なし整数だけに使える（`uint32_t` など）。
    - `std::bitset::count` と同じ。
    - 1 命令で動く環境が多く、非常に速い。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::popcount {#popcount}

```cpp
template <class T>
constexpr int popcount(T x) noexcept;  // T は符号なし整数
```

- 1 になっているビットの数

<div class="anim" data-label="std::popcount(0b1011u)">
1 0 1 1 # ビット列
*1 0 1 1 # 1 のビットを数える
*1 0 *1 1 # 2 つ目
*1 0 *1 *1 # 3 つ。結果は 3
</div>

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{}", std::popcount(0b1011u));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| フラグのうち立っているものの数 | `std::popcount(mask)` |
| レイヤーマスクに該当するものの数 | `std::popcount(layers & filter)` |

## よくあるミス

??? failure "符号つき整数に使う"
    コンパイルエラーです。`static_cast<unsigned>` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::bitset`](../../containers/bitset.md) | `count()` で同じ |
| [`has_single_bit`](has_single_bit.md) | 1 つだけ立っているか |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 立っているビットの数
    - [x] 符号なし整数だけ
    - [x] CPU 命令で速い

## 関連ページ

- [cpprefjp: std::popcount](https://cpprefjp.github.io/reference/bit/popcount.html)
- [cppreference: std::popcount](https://en.cppreference.com/w/cpp/numeric/popcount)

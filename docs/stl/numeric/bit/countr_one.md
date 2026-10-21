---
title: std::countr_one
summary: "下位（右）から数えて、連続する 1 のビット数を数える。"
order: 10
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::countr_one

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`std::countr_one` は、**最下位のビットから数えて、連続している 1 の数**を返す関数です。「最初に 0 になっているビット（空きの番号）」を探すときに使えます。`countr_one(0b0111)` は 3 です。

!!! tip "ポイント"
    - 最初の空き（0 のビット）の番号が分かる。
    - `countr_zero(~x)` と同じ。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::countr_one {#countr_one}

```cpp
template <class T>
constexpr int countr_one(T x) noexcept;
```

- 一番下の位から続く 1 の数

```cpp
#include <bit>
#include <cstdint>
#include <print>

int main() {
  std::uint8_t x = 0b0001'0111;
  std::println("floor {} / width {} / countl_zero {} / countr_one {} / countl_one {}",
               std::bit_floor(x), std::bit_width(x), std::countl_zero(x), std::countr_one(x),
               std::countl_one(static_cast<std::uint8_t>(0b1110'0000)));
}
```

```text title="実行結果"
floor 16 / width 5 / countl_zero 3 / countr_one 3 / countl_one 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使用中フラグのビットマスクから、最初の空きスロットを探す | `slot = std::countr_one(used_mask);` |

## よくあるミス

??? failure "すべて使用中のとき"
    全ビット 1 なら、型のビット数が返ります。範囲外のスロット番号になるので確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`countr_zero`](countr_zero.md) | 0 を数える |
| [`countl_one`](countl_one.md) | 上位から数える |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 下位から連続する 1 の数
    - [x] 最初の空きを探す
    - [x] 全部 1 なら全ビット数

## 関連ページ

- [cpprefjp: std::countr_one](https://cpprefjp.github.io/reference/bit/countr_one.html)
- [cppreference: std::countr_one](https://en.cppreference.com/w/cpp/numeric/countr_one)

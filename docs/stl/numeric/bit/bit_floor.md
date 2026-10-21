---
title: std::bit_floor
summary: "自分以下で最大の、2 のべき乗に切り捨てる。"
order: 4
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::bit_floor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`std::bit_floor` は、**値以下で最大の 2 のべき乗に切り捨てる**関数です。`bit_floor(5)` は 4、`bit_floor(8)` は 8 です。0 を渡すと 0 を返します。

!!! tip "ポイント"
    - `bit_ceil` の反対。
    - 0 は 0。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::bit_floor {#bit_floor}

```cpp
template <class T>
constexpr T bit_floor(T x) noexcept;
```

- `x` 以下で一番大きい 2 のべき乗（0 なら 0）

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{} {}", std::bit_floor(5u), std::bit_floor(8u));
}
```

```text title="実行結果"
4 8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使える最大の 2 のべき乗サイズを選ぶ | `std::bit_floor(available)` |

## よくあるミス

??? failure "0 の結果を忘れる"
    0 を渡すと 0 が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_ceil`](bit_ceil.md) | 切り上げ |
| [`bit_width`](bit_width.md) | ビット幅 |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 のべき乗に切り捨て
    - [x] 0 は 0
    - [x] 切り上げは bit_ceil

## 関連ページ

- [cpprefjp: std::bit_floor](https://cpprefjp.github.io/reference/bit/bit_floor.html)
- [cppreference: std::bit_floor](https://en.cppreference.com/w/cpp/numeric/bit_floor)

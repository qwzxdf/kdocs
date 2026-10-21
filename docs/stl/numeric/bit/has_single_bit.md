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

`std::has_single_bit` は、**ビットがちょうど 1 つだけ立っているか（= 2 のべき乗か）**を調べる関数です。テクスチャの大きさや、バッファのアラインメントが 2 のべき乗かの確認に使います。

!!! tip "ポイント"
    - 0 は `false`（立っているビットがない）。
    - `(x & (x - 1)) == 0` と同じ意味だが、0 の扱いが正しい。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::has_single_bit {#has_single_bit}

```cpp
template <class T>
constexpr bool has_single_bit(T x) noexcept;
```

- 1 のビットがちょうど 1 つ（= 2 のべき乗）なら `true`。0 は `false`

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{} {}", std::has_single_bit(8u), std::has_single_bit(6u));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テクスチャの幅が 2 のべき乗か | `std::has_single_bit(width)` |

## よくあるミス

??? failure "0 を 2 のべき乗と判定する"
    古い書き方 `(x & (x - 1)) == 0` は 0 でも真になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_ceil`](bit_ceil.md) | 次の 2 のべき乗へ切り上げ |
| [`popcount`](popcount.md) | 立っているビットの数 |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 のべき乗かを調べる
    - [x] 0 は false
    - [x] 符号なし整数だけ

## 関連ページ

- [cpprefjp: std::has_single_bit](https://cpprefjp.github.io/reference/bit/has_single_bit.html)
- [cppreference: std::has_single_bit](https://en.cppreference.com/w/cpp/numeric/has_single_bit)

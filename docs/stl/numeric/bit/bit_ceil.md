---
title: std::bit_ceil
summary: "自分以上で最小の、2 のべき乗に切り上げる。"
order: 3
group: ビット操作（<bit>）
tags:
  - 数値
---

# std::bit_ceil

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <bit>`
</div>

`std::bit_ceil` は、**値以上で最小の 2 のべき乗に切り上げる**関数です。バッファの大きさを 2 のべき乗にそろえる、ハッシュ表の大きさを決める、テクスチャの大きさを丸める、といった処理に使います。

!!! tip "ポイント"
    - `bit_ceil(5)` は 8、`bit_ceil(8)` は 8。
    - 結果が型に収まらないと未定義動作。
    - 切り捨ては `bit_floor`。

!!! info "このページを読む前に"
    [`<bit>`](../bit.md) の概要を先に読むと分かりやすいです。符号なし整数（`uint32_t` など）にだけ使えます。

## 関数の詳しい説明

### std::bit_ceil {#bit_ceil}

```cpp
template <class T>
constexpr T bit_ceil(T x);
```

- `x` 以上で一番小さい 2 のべき乗。テクスチャやバッファの大きさを 2 のべき乗にそろえるのに使います

## 実際に動かしてみる

```cpp
#include <bit>
#include <print>

int main() {
  std::println("{} {}", std::bit_ceil(5u), std::bit_ceil(8u));
}
```

```text title="実行結果"
8 8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テクスチャのサイズを 2 のべき乗にそろえる | `std::bit_ceil(width)` |
| ハッシュ表の容量 | `std::bit_ceil(count * 2)` |

## よくあるミス

??? failure "結果が型に収まらない"
    `uint8_t` の 200 → 256 は収まりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bit_floor`](bit_floor.md) | 切り捨て |
| [`has_single_bit`](has_single_bit.md) | 2 のべき乗か |

## コンパイラ対応

C++20 の機能です。GCC 9 / Clang 9 / MSVC 19.25 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 のべき乗に切り上げ
    - [x] 切り捨ては bit_floor
    - [x] 型に収まること

## 関連ページ

- [cpprefjp: std::bit_ceil](https://cpprefjp.github.io/reference/bit/bit_ceil.html)
- [cppreference: std::bit_ceil](https://en.cppreference.com/w/cpp/numeric/bit_ceil)

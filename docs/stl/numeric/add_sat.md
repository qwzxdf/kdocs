---
title: std::add_sat
summary: "足し算。範囲を超えたら最大・最小値に張り付く。"
order: 10
group: 飽和演算（<numeric>）
tags:
  - 数値
---

# std::add_sat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <numeric>`
</div>

`std::add_sat` は、**足し算で、結果が型の範囲を超えたときに、最大値（または最小値）に張り付く**関数です。普通の足し算は桁あふれして値が一周しますが、これは一周しません。`uint8_t` のダメージ値、HP の加算に便利です。

!!! tip "ポイント"
    - 結果が型の範囲を超えるとき、**最大値（または最小値）に張り付く**。桁あふれ（ラップアラウンド）しない。
    - 符号つき・符号なしの両方で使える。
    - C++26 の機能。

## 関数の詳しい説明

### std::add_sat {#add_sat}

```cpp
template <class T>
constexpr T add_sat(T x, T y) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x`, `y` | 整数 | 計算する 2 つ |

- 戻り値: x + y。範囲を超えたら最大値・最小値に張り付く
- 計算量: O(1)

```cpp
#include <cstdint>
#include <numeric>
#include <print>

int main() {
  std::uint8_t a = 200;
  std::uint8_t b = 100;
  std::println("{} {}", static_cast<int>(static_cast<std::uint8_t>(a + b)), static_cast<int>(std::add_sat(a, b)));  // 普通の足し算は一周する
}
```

```text title="実行結果"
44 255
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| HP・所持金・ダメージの計算で、型の範囲を超えないようにする | `std::add_sat(a, b)` |

## よくあるミス

??? failure "古い環境で使えない"
    C++26 の機能です。使えないときは、条件を書いて自分で判定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::clamp`](../algorithms/clamp.md) | 範囲に収める |
| [`std::cmp_less`](../support/cmp_less.md) | 符号の混ざった比較 |

## コンパイラ対応

C++26 の機能です。GCC 14 / Clang 18 / MSVC 19.40 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲を超えたら張り付く
    - [x] ラップアラウンドしない
    - [x] C++26

## 関連ページ

- [cpprefjp: std::add_sat](https://cpprefjp.github.io/reference/numeric/add_sat.html)
- [cppreference: std::add_sat](https://en.cppreference.com/w/cpp/numeric/add_sat)

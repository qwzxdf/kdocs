---
title: std::div_sat
summary: "割り算。範囲を超える唯一の場合（最小値 ÷ −1）で張り付く。"
order: 13
group: 飽和演算（<numeric>）
tags:
  - 数値
---

# std::div_sat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <numeric>`
</div>

`std::div_sat` は、**割り算で、結果が型の範囲を超える場合に張り付く**関数です。符号つきの整数では、「最小値 ÷ −1」だけが範囲を超えます（普通は未定義動作）。それを最大値に張り付けて、安全にします。0 での割り算は、今まで通り未定義動作です。

!!! tip "ポイント"
    - 結果が型の範囲を超えるとき、**最大値（または最小値）に張り付く**。桁あふれ（ラップアラウンド）しない。
    - 符号つき・符号なしの両方で使える。
    - C++26 の機能。

!!! info "このページを読む前に"
    - [stl/index.md](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::div_sat {#div_sat}

```cpp
template <class T>
constexpr T div_sat(T x, T y) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x`, `y` | 整数 | 計算する 2 つ |

- 戻り値: x / y。範囲を超えたら最大値・最小値に張り付く
- 計算量: O(1)

```cpp
#include <cstdint>
#include <numeric>
#include <print>

int main() {
  std::int8_t lowest = -128;
  std::println("{}", static_cast<int>(std::div_sat<std::int8_t>(lowest, std::int8_t{-1})));  // 128 → 127
}
```

```text title="実行結果"
127
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| HP・所持金・ダメージの計算で、型の範囲を超えないようにする | `std::div_sat(a, b)` |

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

- [cpprefjp: std::div_sat](https://cpprefjp.github.io/reference/numeric/div_sat.html)
- [cppreference: std::div_sat](https://en.cppreference.com/w/cpp/numeric/div_sat)

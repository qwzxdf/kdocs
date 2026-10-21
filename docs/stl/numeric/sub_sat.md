---
title: std::sub_sat
summary: "引き算。範囲を超えたら最大・最小値に張り付く。"
order: 11
group: 飽和演算（<numeric>）
tags:
  - 数値
---

# std::sub_sat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <numeric>`
</div>

`std::sub_sat` は、**引き算で、結果が型の範囲を超えたときに張り付く**関数です。符号なし整数の引き算で、0 を下回ると一周して巨大な値になる事故を防ぎます。HP や所持金の減算に使います。

!!! tip "ポイント"
    - 結果が型の範囲を超えるとき、**最大値（または最小値）に張り付く**。桁あふれ（ラップアラウンド）しない。
    - 符号つき・符号なしの両方で使える。
    - C++26 の機能。

## 関数の詳しい説明

### std::sub_sat {#sub_sat}

```cpp
template <class T>
constexpr T sub_sat(T x, T y) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x`, `y` | 整数 | 計算する 2 つ |

- 戻り値: x - y。範囲を超えたら最大値・最小値に張り付く
- 計算量: O(1)

```cpp
#include <cstdint>
#include <numeric>
#include <print>

int main() {
  std::uint8_t hp = 30;
  std::uint8_t damage = 50;
  std::println("{}", static_cast<int>(std::sub_sat(hp, damage)));  // 0 で止まる
}
```

```text title="実行結果"
0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| HP・所持金・ダメージの計算で、型の範囲を超えないようにする | `std::sub_sat(a, b)` |

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

- [cpprefjp: std::sub_sat](https://cpprefjp.github.io/reference/numeric/sub_sat.html)
- [cppreference: std::sub_sat](https://en.cppreference.com/w/cpp/numeric/sub_sat)

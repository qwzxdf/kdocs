---
title: std::saturate_cast
summary: "整数を別の整数型に変換する。範囲を超えたら張り付く。"
order: 14
group: 飽和演算（<numeric>）
tags:
  - 数値
---

# std::saturate_cast

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <numeric>`
</div>

`std::saturate_cast<T>(x)` は、**整数を別の整数型 `T` に変換するときに、`T` の範囲を超えていれば最大値（最小値）に張り付ける**関数です。`static_cast` は範囲外だと値が壊れますが、これは安全です。画像の色（0〜255）への変換などに便利です。

!!! tip "ポイント"
    - `saturate_cast<uint8_t>(300)` は 255、`saturate_cast<uint8_t>(-5)` は 0。
    - `static_cast` の範囲外は、値が壊れる（またはオーバーフロー）。
    - C++26 の機能。

## 関数の詳しい説明

### std::saturate_cast {#saturate_cast}

```cpp
template <class R, class T>
constexpr R saturate_cast(T x) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | テンプレート引数 | 変換先の整数型 |
| `x` | 整数 | 変換する値 |

- 戻り値: `R` の範囲に収めた値
- 計算量: O(1)

```cpp
#include <cstdint>
#include <numeric>
#include <print>

int main() {
  std::println("{} {} {}", static_cast<int>(std::saturate_cast<std::uint8_t>(300)),
               static_cast<int>(std::saturate_cast<std::uint8_t>(-5)),
               static_cast<int>(std::saturate_cast<std::uint8_t>(100)));
}
```

```text title="実行結果"
255 0 100
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 色の計算結果を 0〜255 に収めて uint8_t にする | `std::saturate_cast<std::uint8_t>(value)` |

## よくあるミス

??? failure "小数に使う"
    整数専用です。小数は `std::clamp` してから変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::clamp`](../algorithms/clamp.md) | 範囲に収める（型は変えない） |
| [`add_sat`](add_sat.md) | 足し算で張り付く |

## コンパイラ対応

C++26 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲を超えたら張り付く変換
    - [x] `static_cast` は壊れる
    - [x] C++26

## 関連ページ

- [cpprefjp: std::saturate_cast](https://cpprefjp.github.io/reference/numeric/saturate_cast.html)
- [cppreference: std::saturate_cast](https://en.cppreference.com/w/cpp/numeric/saturate_cast)

---
title: std::fmax
summary: "2 つの小数の大きいほうを返す（NaN は無視する）。"
order: 36
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fmax

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::fmax` は、**2 つの小数のうち大きいほうを返す**関数で、**片方が NaN ならもう片方を返します**。`std::max` は NaN があると結果が不定になりますが、`fmax` は NaN を無視します。

!!! tip "ポイント"
    - NaN を含む可能性があるデータの最大値に。
    - 通常の比較には `std::max`（型が同じなら）。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fmax {#fmax}

```cpp
double fmax(double x, double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x`, `y` | 浮動小数点 | 比べる 2 つ |

- 戻り値: 大きいほう（NaN は無視）
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  double nan = std::nan("");
  std::println("{} {}", std::fmax(1.5, 2.5), std::fmax(nan, 1.0));
}
```

```text title="実行結果"
2.5 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 欠損値（NaN）を含むデータの最大値 | `fmax(a, b)` |

## よくあるミス

??? failure "std::max で NaN を含むデータを扱う"
    結果が不定になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fmin`](fmin.md) | 小さいほう |
| [`std::max`](../../algorithms/max.md) | 汎用 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きいほう。NaN は無視
    - [x] `std::max` との違いは NaN
    - [x] `fmin` と対

## 関連ページ

- [cpprefjp: std::fmax](https://cpprefjp.github.io/reference/cmath/fmax.html)
- [cppreference: std::fmax](https://en.cppreference.com/w/cpp/numeric/math/fmax)

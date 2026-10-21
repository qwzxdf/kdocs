---
title: std::fmin
summary: "2 つの小数の小さいほうを返す（NaN は無視する）。"
order: 37
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fmin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::fmin` は、**2 つの小数のうち小さいほうを返す**関数で、**片方が NaN ならもう片方を返します**。

!!! tip "ポイント"
    - NaN を含む可能性があるデータの最小値に。
    - 通常の比較には `std::min`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fmin {#fmin}

```cpp
double fmin(double x, double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x`, `y` | 浮動小数点 | 比べる 2 つ |

- 戻り値: 小さいほう（NaN は無視）
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  double nan = std::nan("");
  std::println("{} {}", std::fmin(1.5, 2.5), std::fmin(nan, 1.0));
}
```

```text title="実行結果"
1.5 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 欠損値を含むデータの最小値 | `fmin(a, b)` |

## よくあるミス

??? failure "std::min で NaN を含むデータを扱う"
    結果が不定になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fmax`](fmax.md) | 大きいほう |
| [`std::min`](../../algorithms/min.md) | 汎用 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小さいほう。NaN は無視
    - [x] `fmax` と対
    - [x] 通常は std::min

## 関連ページ

- [cpprefjp: std::fmin](https://cpprefjp.github.io/reference/cmath/fmin.html)
- [cppreference: std::fmin](https://en.cppreference.com/w/cpp/numeric/math/fmin)

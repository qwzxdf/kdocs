---
title: std::chi_squared_distribution
summary: "カイ二乗分布。統計の検定に使われる。"
order: 24
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::chi_squared_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::chi_squared_distribution` は、**統計の検定でよく使われる**乱数（カイ二乗分布）を出します。「n 個の標準正規乱数の 2 乗の合計」が従う分布です。ゲームでの出番はほとんどありません。

!!! tip "ポイント"
    - `n` は自由度（正の数）。
    - [`gamma_distribution`](gamma_distribution.md) の特別な場合（`alpha = n/2`、`beta = 2`）。
    - 統計用。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::chi_squared_distribution {#chi_squared_distribution}

```cpp
explicit chi_squared_distribution(double n = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `n` | `double` | 自由度（正の数） | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::chi_squared_distribution<double> d(4.0);
  std::println("自由度 {} / 最小 {}", d.n(), d.min());
}
```

```text title="実行結果"
自由度 4 / 最小 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 統計処理（ゲームでは不要） | `chi_squared_distribution<double> d(4.0);` |

## よくあるミス

??? failure "標準偏差と取り違える"
    `n` は自由度です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gamma_distribution`](gamma_distribution.md) | 一般化した分布 |
| [`student_t_distribution`](student_t_distribution.md) | 関連する統計の分布 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 統計の検定に使われる分布
    - [x] n は自由度
    - [x] ゲームではほぼ使わない

## 関連ページ

- [cpprefjp: std::chi_squared_distribution](https://cpprefjp.github.io/reference/random/chi_squared_distribution.html)
- [cppreference: std::chi_squared_distribution](https://en.cppreference.com/w/cpp/numeric/random/chi_squared_distribution)

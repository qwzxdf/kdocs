---
title: std::exponential_distribution
summary: "「出来事と出来事の間隔」を出す。"
order: 19
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::exponential_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::exponential_distribution` は、**ランダムに起きる出来事の「間隔」**の乱数を出します。小さい値ほど出やすく、長い間隔はまれです。敵が現れる間隔、イベントの待ち時間などに使います。`lambda` は「1 単位あたりの平均回数」です。

!!! tip "ポイント"
    - 平均の間隔は `1 / lambda`。
    - 戻り値は 0 以上の小数。
    - 回数のほうなら [`poisson_distribution`](poisson_distribution.md)。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exponential_distribution {#exponential_distribution}

```cpp
explicit exponential_distribution(double lambda = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `lambda` | `double` | 1 単位あたりの平均回数（正の数） | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::exponential_distribution<double> d(2.0);
  std::println("lambda {} / 最小 {}", d.lambda(), d.min());
}
```

```text title="実行結果"
lambda 2 / 最小 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 敵が現れる間隔（秒） | `exponential_distribution<float> gap(0.5f);` |

## よくあるミス

??? failure "lambda を平均の間隔だと思う"
    `lambda` は「回数」で、間隔の平均は `1 / lambda` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`poisson_distribution`](poisson_distribution.md) | 回数 |
| [`uniform_real_distribution`](uniform_real_distribution.md) | 間隔を均等に |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出来事の間隔の分布
    - [x] 平均は 1 / lambda
    - [x] 回数は poisson

## 関連ページ

- [cpprefjp: std::exponential_distribution](https://cpprefjp.github.io/reference/random/exponential_distribution.html)
- [cppreference: std::exponential_distribution](https://en.cppreference.com/w/cpp/numeric/random/exponential_distribution)

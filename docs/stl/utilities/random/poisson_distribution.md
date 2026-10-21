---
title: std::poisson_distribution
summary: "「一定時間に起きる出来事の回数」を出す。"
order: 18
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::poisson_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::poisson_distribution` は、**「一定の時間や範囲の中で、まれな出来事が何回起きるか」**の乱数を出します。「1 分間に現れる敵の数」「1 フレームに降る雨粒の数」のように、**ランダムなタイミングで起きる出来事の数**に使います。

!!! tip "ポイント"
    - 平均（`mean`）だけを指定する。
    - 戻り値は 0 以上の整数。
    - 出来事の間隔なら [`exponential_distribution`](exponential_distribution.md)。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::poisson_distribution {#poisson_distribution}

```cpp
explicit poisson_distribution(double mean = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `mean` | `double` | 平均の回数 | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::poisson_distribution<int> d(4.0);
  std::println("平均 {} / 最小 {}", d.mean(), d.min());
}
```

```text title="実行結果"
平均 4 / 最小 0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 分間に現れる敵の数 | `poisson_distribution<int> spawn(4.0);` |
| 1 フレームに発生するパーティクルの数 | `poisson_distribution<int> emit(2.5);` |

## よくあるミス

??? failure "平均を整数で渡す"
    `double` で渡します（`4` でも `4.0` でも可）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exponential_distribution`](exponential_distribution.md) | 出来事と出来事の間隔 |
| [`binomial_distribution`](binomial_distribution.md) | 決まった回数の中での成功 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一定時間の出来事の回数
    - [x] 平均だけ指定
    - [x] 間隔は exponential

## 関連ページ

- [cpprefjp: std::poisson_distribution](https://cpprefjp.github.io/reference/random/poisson_distribution.html)
- [cppreference: std::poisson_distribution](https://en.cppreference.com/w/cpp/numeric/random/poisson_distribution)

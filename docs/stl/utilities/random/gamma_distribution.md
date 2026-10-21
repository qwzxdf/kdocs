---
title: std::gamma_distribution
summary: "ガンマ分布。待ち時間の合計や、偏った正の値に。"
order: 20
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::gamma_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::gamma_distribution` は、**正の値で、右に裾が長い**乱数（ガンマ分布）を出します。「α 個の出来事が起きるまでの待ち時間の合計」や、偏りのある正の値（ダメージのばらつきなど）を作るのに使えます。`alpha` が形、`beta` が尺度です。

!!! tip "ポイント"
    - `alpha = 1` なら [`exponential_distribution`](exponential_distribution.md) と同じ。
    - ほかの分布（カイ二乗など）の部品になっている。
    - 使う場面は少ない。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::gamma_distribution {#gamma_distribution}

```cpp
explicit gamma_distribution(double alpha = 1.0, double beta = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `alpha` | `double` | 形（正の数） | `1.0` |
| `beta` | `double` | 尺度（正の数） | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::gamma_distribution<double> d(2.0, 3.0);
  std::println("alpha {} / beta {}", d.alpha(), d.beta());
}
```

```text title="実行結果"
alpha 2 / beta 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 右に裾が長いダメージのばらつき | `gamma_distribution<float> dmg(2.0f, 5.0f);` |

## よくあるミス

??? failure "alpha と beta の役割を取り違える"
    `alpha` が形、`beta` が尺度です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exponential_distribution`](exponential_distribution.md) | alpha = 1 の特別な場合 |
| [`chi_squared_distribution`](chi_squared_distribution.md) | ガンマ分布の特別な場合 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正の値で、右に裾が長い
    - [x] alpha が形、beta が尺度
    - [x] 使う場面は少ない

## 関連ページ

- [cpprefjp: std::gamma_distribution](https://cpprefjp.github.io/reference/random/gamma_distribution.html)
- [cppreference: std::gamma_distribution](https://en.cppreference.com/w/cpp/numeric/random/gamma_distribution)

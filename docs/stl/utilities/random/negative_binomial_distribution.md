---
title: std::negative_binomial_distribution
summary: "「k 回成功するまでに、失敗した回数」を出す。"
order: 16
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::negative_binomial_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::negative_binomial_distribution` は、**「成功確率 p の試行を、k 回成功するまで繰り返したとき、それまでに失敗した回数」**の乱数を出します。「レアが 3 個出るまでに何回ハズレるか」のような、待ち時間の分布です。

!!! tip "ポイント"
    - 戻り値は失敗の回数（0 以上）。
    - `k = 1` なら [`geometric_distribution`](geometric_distribution.md)。
    - 使う場面は少ない。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::negative_binomial_distribution {#negative_binomial_distribution}

```cpp
explicit negative_binomial_distribution(IntType k = 1, double p = 0.5);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `k` | 整数 | 必要な成功の回数 | `1` |
| `p` | `double` | 1 回あたりの成功確率 | `0.5` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::negative_binomial_distribution<int> d(3, 0.5);
  std::println("成功 {} 回まで / 確率 {} / 最小 {}", d.k(), d.p(), d.min());
}
```

```text title="実行結果"
成功 3 回まで / 確率 0.5 / 最小 0
```

### operator() {#op_call}

```cpp
template <class Generator>
result_type operator()(Generator& g);
```

- 計算量: 定数（アルゴリズムによる）

乱数エンジン `g` から乱数を取って、この分布に従う値を 1 つ返します。

### reset {#reset}

```cpp
void reset();
```

- 計算量: 定数

分布の内部状態を初期化します。直前の呼び出しで持ち越している値（正規分布の「余り」の値）を捨てます。

### param {#param}

```cpp
param_type param() const;
void param(const param_type& p);
```

- 計算量: 定数

分布のパラメータ一式を取り出す、または設定します。

### min {#min}

```cpp
result_type min() const;
```

- 計算量: 定数

この分布が返しうる最小値。

### max {#max}

```cpp
result_type max() const;
```

- 計算量: 定数

この分布が返しうる最大値。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| レアが 3 個出るまでの外れの回数 | `negative_binomial_distribution<int> misses(3, 0.05);` |

## よくあるミス

??? failure "成功の回数を戻り値だと思う"
    戻り値は**失敗**の回数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`geometric_distribution`](geometric_distribution.md) | 1 回成功するまで |
| [`binomial_distribution`](binomial_distribution.md) | 決まった回数の中での成功 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] k 回成功するまでの失敗回数
    - [x] `k = 1` なら geometric
    - [x] 待ち時間の分布

## 関連ページ

- [cpprefjp: std::negative_binomial_distribution](https://cpprefjp.github.io/reference/random/negative_binomial_distribution.html)
- [cppreference: std::negative_binomial_distribution](https://en.cppreference.com/w/cpp/numeric/random/negative_binomial_distribution)

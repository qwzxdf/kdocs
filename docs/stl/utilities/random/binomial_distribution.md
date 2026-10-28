---
title: std::binomial_distribution
summary: "「確率 p の試行を t 回やったとき、成功した回数」を出す。"
order: 15
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::binomial_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::binomial_distribution` は、**「成功確率 p の試行を t 回行ったとき、成功した回数」**の乱数を出します。「10 回攻撃して、命中率 50% で何回当たるか」のような計算をループを書かずに 1 回で求められます。

!!! tip "ポイント"
    - 戻り値は 0〜t の整数。
    - 1 回だけの判定なら [`bernoulli_distribution`](bernoulli_distribution.md)。
    - 平均は `t × p`。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::binomial_distribution {#binomial_distribution}

```cpp
explicit binomial_distribution(IntType t = 1, double p = 0.5);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `t` | 整数 | 試行の回数 | `1` |
| `p` | `double` | 1 回あたりの成功確率 | `0.5` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::binomial_distribution<int> d(10, 0.5);
  std::println("試行 {} 回 / 確率 {} / 出る値 {} 〜 {}", d.t(), d.p(), d.min(), d.max());
}
```

```text title="実行結果"
試行 10 回 / 確率 0.5 / 出る値 0 〜 10
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
| 連続攻撃の命中回数を一度に決める | `binomial_distribution<int> hits(10, 0.5);` |

## よくあるミス

??? failure "p と t の順番を逆にする"
    先に回数 `t`、次に確率 `p` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bernoulli_distribution`](bernoulli_distribution.md) | 1 回だけ |
| [`poisson_distribution`](poisson_distribution.md) | 回数が多く、確率が小さいときの近似 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 試行回数と成功確率から、成功回数を出す
    - [x] 戻り値は 0〜t
    - [x] 平均は t × p

## 関連ページ

- [cpprefjp: std::binomial_distribution](https://cpprefjp.github.io/reference/random/binomial_distribution.html)
- [cppreference: std::binomial_distribution](https://en.cppreference.com/w/cpp/numeric/random/binomial_distribution)

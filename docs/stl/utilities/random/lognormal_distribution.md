---
title: std::lognormal_distribution
summary: "対数正規分布。正の値で、右に裾が長い。"
order: 23
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::lognormal_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::lognormal_distribution` は、**「値の対数が正規分布になる」乱数**を出します。常に正で、右に裾が長い形になります。ダメージ、アイテムの価格、レベルごとの経験値の個体差など、「大きく外れることもあるが、負にならない」値に使えます。

!!! tip "ポイント"
    - 値は常に正（0 より大きい）。
    - `m` と `s` は、**対数の**平均と標準偏差（元の値の平均ではない）。
    - 中央値は `exp(m)`。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lognormal_distribution {#lognormal_distribution}

```cpp
explicit lognormal_distribution(double m = 0.0, double s = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `m` | `double` | 対数の平均 | `0.0` |
| `s` | `double` | 対数の標準偏差 | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::lognormal_distribution<double> d(0.0, 1.0);
  std::println("m {} / s {} / 最小 {}", d.m(), d.s(), d.min());
}
```

```text title="実行結果"
m 0 / s 1 / 最小 0
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
| 裾が長いダメージ・価格の個体差 | `lognormal_distribution<float> price(3.0f, 0.4f);` |

## よくあるミス

??? failure "m を元の値の平均だと思う"
    `m` は対数の平均です。中央値が 100 くらいにしたいなら `m = std::log(100)` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`normal_distribution`](normal_distribution.md) | 対称 |
| [`gamma_distribution`](gamma_distribution.md) | 似た形 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 常に正で右に裾が長い
    - [x] m と s は対数の値
    - [x] 中央値は exp(m)

## 関連ページ

- [cpprefjp: std::lognormal_distribution](https://cpprefjp.github.io/reference/random/lognormal_distribution.html)
- [cppreference: std::lognormal_distribution](https://en.cppreference.com/w/cpp/numeric/random/lognormal_distribution)

---
title: std::fisher_f_distribution
summary: "F 分布。分散の比の検定に使われる。"
order: 26
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::fisher_f_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::fisher_f_distribution` は、**2 つの分散の比を検定するのに使われる**乱数（F 分布）を出します。統計用で、ゲームでの出番はほとんどありません。

!!! tip "ポイント"
    - `m` と `n` は、それぞれ自由度。
    - 2 つの [`chi_squared_distribution`](chi_squared_distribution.md) の比に由来する。
    - 統計用。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fisher_f_distribution {#fisher_f_distribution}

```cpp
explicit fisher_f_distribution(double m = 1.0, double n = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `m` | `double` | 分子の自由度 | `1.0` |
| `n` | `double` | 分母の自由度 | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::fisher_f_distribution<double> d(3.0, 5.0);
  std::println("m {} / n {}", d.m(), d.n());
}
```

```text title="実行結果"
m 3 / n 5
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
| 統計処理（ゲームでは不要） | `fisher_f_distribution<double> d(3.0, 5.0);` |

## よくあるミス

??? failure "自由度を整数だけだと思う"
    `double` で渡せます（整数でなくてもよい）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`chi_squared_distribution`](chi_squared_distribution.md) | F 分布の元になる分布 |
| [`student_t_distribution`](student_t_distribution.md) | もう 1 つの検定用の分布 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 分散の比の検定に使われる
    - [x] m と n は自由度
    - [x] ゲームではほぼ使わない

## 関連ページ

- [cpprefjp: std::fisher_f_distribution](https://cpprefjp.github.io/reference/random/fisher_f_distribution.html)
- [cppreference: std::fisher_f_distribution](https://en.cppreference.com/w/cpp/numeric/random/fisher_f_distribution)

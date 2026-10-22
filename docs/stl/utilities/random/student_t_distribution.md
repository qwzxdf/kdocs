---
title: std::student_t_distribution
summary: "スチューデントの t 分布。少ないデータでの平均の検定に使う。"
order: 27
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::student_t_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::student_t_distribution` は、**標本が少ないときの平均の検定に使われる**乱数（t 分布）を出します。正規分布に似ていますが、自由度が小さいと裾が長くなります。統計用で、ゲームではほとんど使いません。

!!! tip "ポイント"
    - `n` は自由度。大きくなると正規分布に近づく。
    - `n = 1` は [`cauchy_distribution`](cauchy_distribution.md) と同じ。
    - 統計用。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::student_t_distribution {#student_t_distribution}

```cpp
explicit student_t_distribution(double n = 1.0);
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
  std::student_t_distribution<double> d(5.0);
  std::println("自由度 {}", d.n());
}
```

```text title="実行結果"
自由度 5
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
| 統計処理（ゲームでは不要） | `student_t_distribution<double> d(5.0);` |

## よくあるミス

??? failure "標準偏差と取り違える"
    `n` は自由度です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`normal_distribution`](normal_distribution.md) | n が大きいとき近づく |
| [`cauchy_distribution`](cauchy_distribution.md) | n = 1 の場合 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 少ないデータの平均の検定
    - [x] n は自由度
    - [x] ゲームではほぼ使わない

## 関連ページ

- [cpprefjp: std::student_t_distribution](https://cpprefjp.github.io/reference/random/student_t_distribution.html)
- [cppreference: std::student_t_distribution](https://en.cppreference.com/w/cpp/numeric/random/student_t_distribution)

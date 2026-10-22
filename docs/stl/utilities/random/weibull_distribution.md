---
title: std::weibull_distribution
summary: "ワイブル分布。故障までの時間などに使う。"
order: 21
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::weibull_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::weibull_distribution` は、**「ものが壊れるまでの時間」**などをモデルにする乱数（ワイブル分布）を出します。`a` が形、`b` が尺度です。ゲームでは、耐久度の減り方のランダムさ、故障の発生などに使えます。

!!! tip "ポイント"
    - `a = 1` なら [`exponential_distribution`](exponential_distribution.md) と同じ。
    - a が 1 より大きいと、時間が経つほど壊れやすくなる。
    - 使う場面は少ない。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::weibull_distribution {#weibull_distribution}

```cpp
explicit weibull_distribution(double a = 1.0, double b = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `a` | `double` | 形（正の数） | `1.0` |
| `b` | `double` | 尺度（正の数） | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::weibull_distribution<double> d(1.5, 2.0);
  std::println("a {} / b {}", d.a(), d.b());
}
```

```text title="実行結果"
a 1.5 / b 2
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
| 装備が壊れるまでの時間 | `weibull_distribution<float> life(2.0f, 100.0f);` |

## よくあるミス

??? failure "形と尺度を逆にする"
    先が形 `a`、後が尺度 `b` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exponential_distribution`](exponential_distribution.md) | a = 1 の特別な場合 |
| [`gamma_distribution`](gamma_distribution.md) | 似た形の分布 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 故障までの時間などの分布
    - [x] a が形、b が尺度
    - [x] 使う場面は少ない

## 関連ページ

- [cpprefjp: std::weibull_distribution](https://cpprefjp.github.io/reference/random/weibull_distribution.html)
- [cppreference: std::weibull_distribution](https://en.cppreference.com/w/cpp/numeric/random/weibull_distribution)

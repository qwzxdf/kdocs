---
title: std::geometric_distribution
summary: "「最初に成功するまでに、失敗した回数」を出す。"
order: 17
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::geometric_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::geometric_distribution` は、<strong>「成功確率 p の試行を最初に成功するまで繰り返したとき、それまでに失敗した回数」</strong>の乱数を出します。「ドロップするまで何回倒すか」の待ち回数を作るときに使えます。

!!! tip "ポイント"
    - 戻り値は失敗の回数（0 以上）。成功した回は数えない。
    - p が小さいほど、回数が大きくなりやすい。
    - 平均は `(1 - p) / p`。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::geometric_distribution {#geometric_distribution}

```cpp
explicit geometric_distribution(double p = 0.5);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `p` | `double` | 1 回あたりの成功確率 | `0.5` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::geometric_distribution<int> d(0.25);
  std::println("確率 {} / 最小 {}", d.p(), d.min());
}
```

```text title="実行結果"
確率 0.25 / 最小 0
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
| レアドロップまでに倒す回数 | `geometric_distribution<int> kills(0.05);` |

## よくあるミス

??? failure "0 から始まることを忘れる"
    最初の試行で成功すると 0 が出ます。「何回目で成功したか」にしたいなら +1 します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`negative_binomial_distribution`](negative_binomial_distribution.md) | k 回成功するまで |
| [`bernoulli_distribution`](bernoulli_distribution.md) | 1 回の判定 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最初に成功するまでの失敗回数
    - [x] 0 から始まる
    - [x] 平均は (1 - p) / p

## 関連ページ

- [cpprefjp: std::geometric_distribution](https://cpprefjp.github.io/reference/random/geometric_distribution.html)
- [cppreference: std::geometric_distribution](https://en.cppreference.com/w/cpp/numeric/random/geometric_distribution)

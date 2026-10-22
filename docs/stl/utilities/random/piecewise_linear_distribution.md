---
title: std::piecewise_linear_distribution
summary: "境界点の重みを直線でつないだ、連続値の乱数。"
order: 29
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::piecewise_linear_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::piecewise_linear_distribution` は、**境界点ごとに重みを決め、その間を直線でつないだ形の確率**で連続値を出す乱数です。「中央ほど出やすい三角形」のような、なめらかに変わる分布を作れます。

!!! tip "ポイント"
    - 境界点 `b0, b1, …` と、**境界点ごとの**重み `w0, w1, …`（境界と同じ数）を渡す。
    - [`piecewise_constant_distribution`](piecewise_constant_distribution.md) は階段状、こちらは直線でつなぐ。
    - 三角形の分布は `{0, 1, 0}` の重みで作れる。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::piecewise_linear_distribution {#piecewise_linear_distribution}

```cpp
template <class InputIt1, class InputIt2>
piecewise_linear_distribution(InputIt1 first_b, InputIt1 last_b, InputIt2 first_w);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first_b, last_b` | イテレータ | 境界点の並び |
| `first_w` | イテレータ | 境界点ごとの重み（境界と同じ数） |

- 戻り値: `operator()` で小数を 1 つ返す
- 計算量: O(log n)

```cpp
#include <print>
#include <random>
#include <vector>

int main() {
  std::vector<double> bounds = {0.0, 5.0, 10.0};
  std::vector<double> weights = {0.0, 1.0, 0.0};  // 真ん中が一番出やすい三角形

  std::piecewise_linear_distribution<double> d(bounds.begin(), bounds.end(), weights.begin());
  std::println("{}", d.intervals());
}
```

```text title="実行結果"
[0, 5, 10]
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
| 中央が出やすい、三角形のばらつき | 重みを `{0, 1, 0}` |
| なめらかに変化する出現頻度 | 境界点ごとの重みを決める |

## よくあるミス

??? failure "重みの数を境界より 1 つ少なくする"
    直線でつなぐ版は、境界と同じ数の重みです（`constant` 版との違い）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`piecewise_constant_distribution`](piecewise_constant_distribution.md) | 階段状 |
| [`normal_distribution`](normal_distribution.md) | 釣り鐘型（範囲の制限なし） |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 境界点の重みを直線でつなぐ
    - [x] 重みは境界と同じ数
    - [x] 三角形の分布が作れる

## 関連ページ

- [cpprefjp: std::piecewise_linear_distribution](https://cpprefjp.github.io/reference/random/piecewise_linear_distribution.html)
- [cppreference: std::piecewise_linear_distribution](https://en.cppreference.com/w/cpp/numeric/random/piecewise_linear_distribution)

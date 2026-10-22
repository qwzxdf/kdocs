---
title: std::extreme_value_distribution
summary: "極値分布（ガンベル分布）。最大値・最小値のばらつきに。"
order: 22
group: 乱数の分布（std::xxx_distribution）
tags:
  - ユーティリティ
---

# std::extreme_value_distribution

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <random>`
</div>

`std::extreme_value_distribution` は、**たくさんの値の「最大値」がどうばらつくか**を表す乱数（極値分布）を出します。「1 年間の最大の洪水」のような、極端な値の統計に使われます。ゲームではほとんど使いません。

!!! tip "ポイント"
    - `a` が位置、`b` が尺度。
    - ゲームではほぼ出番がない。
    - 知識として名前だけ覚えておく。

!!! info "このページを読む前に"
    [`<random>`](../random.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::extreme_value_distribution {#extreme_value_distribution}

```cpp
explicit extreme_value_distribution(double a = 0.0, double b = 1.0);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `a` | `double` | 位置 | `0.0` |
| `b` | `double` | 尺度（正の数） | `1.0` |

- 戻り値: `operator()` で、乱数を 1 つ返す
- 計算量: O(1)（平均）

```cpp
#include <print>
#include <random>

int main() {
  std::extreme_value_distribution<double> d(0.0, 1.0);
  std::println("a {} / b {}", d.a(), d.b());
}
```

```text title="実行結果"
a 0 / b 1
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
| 極端な値の統計（ゲームでは不要） | `extreme_value_distribution<double> d;` |

## よくあるミス

??? failure "正規分布と取り違える"
    裾が非対称です。右（大きいほう）に長く伸びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`normal_distribution`](normal_distribution.md) | 対称な釣り鐘型 |
| [`weibull_distribution`](weibull_distribution.md) | 近い仲間 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大値のばらつきの分布
    - [x] ゲームではほぼ使わない
    - [x] a が位置、b が尺度

## 関連ページ

- [cpprefjp: std::extreme_value_distribution](https://cpprefjp.github.io/reference/random/extreme_value_distribution.html)
- [cppreference: std::extreme_value_distribution](https://en.cppreference.com/w/cpp/numeric/random/extreme_value_distribution)

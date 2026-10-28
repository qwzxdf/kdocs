---
title: std::log1p
summary: "log(1 + x) を、x が 0 に近くても精度よく求める。"
order: 35
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::log1p

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`log(1 + x)` は、`x` が 0 に近いと、`1 + x` の足し算で小さな `x` の桁が丸めて落とされてしまいます。`1 + 1e-17` は `double` では 1 と区別できません。

`std::log1p` は、<strong>`log(1 + x)` を `x` が小さくても桁を失わずに</strong>求めます。

!!! tip "ポイント"
    - `std::log1p(x)` は `log(1 + x)` と同じ値
    - `x` が 0 に近いほど、`log(1 + x)` との差が出る
    - `x` が −1 のとき −∞、−1 より小さいと NaN
    - 逆の関数は `expm1`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::log1p {#log1p}

<span class="ver ver-11">C++11</span>

```cpp
float log1p(float x);
double log1p(double x);
long double log1p(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | −1 より大きい値。0 に近いほど精度の差が出る |

戻り値は `log(1 + x)` です。`x` が −1 のときは −∞、−1 より小さいと NaN になります。

`x` が小さいと、`1 + x` を計算する時点で `x` の下位の桁が失われます。`log1p` は、`1 + x` を作らずに、小さな `x` に適した計算で結果を出すので、精度が保たれます。`x` が大きいときは、どちらでも変わりません。

ゲームの通常の計算では、桁落ちを気にする場面はほとんどありません。確率の対数をとって足す計算（対数尤度）や、金利のような小さな値の積み重ねで、`log1p` が使われます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("log1p(0) = {}", std::log1p(0.0));
  std::println("log1p(1) = {}", std::log1p(1.0));      // log(2)
  std::println("log1p(-1) の符号: {}", std::log1p(-1.0) < 0.0);   // -inf
}
```

```text title="実行結果"
log1p(0) = 0
log1p(1) = 0.6931471805599453
log1p(-1) の符号: true
```

## ゲームでの使いどころ

確率の対数を扱う計算で、`log(1 - p)` が必要になることがあります。`p` が小さいときは `log1p(-p)` と書くほうが正確です。

```cpp
// 「1 回で当たらない確率」(1 - p) の対数。p が極端に小さくても正確
const double log_miss = std::log1p(-p);
```

## よくあるミス

??? failure "−1 以下を渡して −∞ や NaN になる"
    `x > -1` であることを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log`](log.md) | 自然対数 |
| [`expm1`](expm1.md) | `exp(x) - 1` を正確に求める（逆の関数） |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `log1p(x)` は `log(1 + x)`
    - [x] `x` が小さいときの桁落ちを防ぐ
    - [x] −1 は −∞、−1 未満は NaN

## 関連ページ

- [`std::expm1`](expm1.md)
- [cpprefjp: std::log1p](https://cpprefjp.github.io/reference/cmath/log1p.html)
- [cppreference: std::log1p](https://en.cppreference.com/w/cpp/numeric/math/log1p)

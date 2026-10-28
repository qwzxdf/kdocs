---
title: std::expm1
summary: "e^x − 1 を、x が 0 に近くても精度よく求める。"
order: 34
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::expm1

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`exp(x) - 1` は、`x` が 0 に近いと、とても小さな値どうしの引き算になります。`exp(x)` はほぼ 1 で、そこから 1 を引くと、有効な桁のほとんどが消えます（桁落ち）。

`std::expm1` は、<strong>`exp(x) - 1` を `x` が小さくても桁を失わずに</strong>求めます。

!!! tip "ポイント"
    - `std::expm1(x)` は `exp(x) - 1` と同じ値
    - `x` が 0 に近いほど、`exp(x) - 1` と差が出る（桁落ちを防ぐ）
    - `expm1(0)` は 0
    - 逆の関数は `log1p`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::expm1 {#expm1}

<span class="ver ver-11">C++11</span>

```cpp
float expm1(float x);
double expm1(double x);
long double expm1(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 指数。0 に近いほど `exp(x) - 1` との差が大きくなる |

戻り値は e の `x` 乗から 1 を引いた値です。数学的には `exp(x) - 1` と同じですが、`x` が小さいときの精度が違います。

例えば `x = 1e-15` のとき、`exp(x)` は 1.000000000000001 に近い値ですが、`double` では有効な桁の最後の数桁しか残りません。そこから 1 を引くと、結果は数桁分の精度しかなく、正しい値 `1e-15` から大きくずれます。`expm1(x)` は内部で、小さな `x` に適した級数展開を使うため、ほぼ全桁の精度を保てます。

`x` が大きいときは、`exp(x) - 1` と差が出ないので、どちらを使っても構いません。

ゲームの通常の計算では、桁落ちが問題になる場面はまれです。金利や減衰を長い時間にわたって積み重ねるシミュレーション、あるいは極端に細かい時間刻みの積分で効いてきます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("expm1(0) = {}", std::expm1(0.0));
  std::println("expm1(1) = {}", std::expm1(1.0));      // e - 1
  // 小さな x でも expm1 は桁を保つ。ここでは両者の差が 1e-18 を超えないことだけ確認
  const double x = 1e-10;
  std::println("近い値: {}", std::abs(std::expm1(x) - x) < 1e-18);
}
```

```text title="実行結果"
expm1(0) = 0
expm1(1) = 1.718281828459045
近い値: true
```

## ゲームでの使いどころ

微小な時間刻みで増減を積み重ねるシミュレーションで使います。たとえば、1 ステップあたりの減衰率がゼロに近いとき、1 − exp(−rate × dt) は、`-expm1(-rate * dt)` と書くと正確です。

```cpp
// 1 ステップで失われる割合（dt が極端に小さくても正確）
const double lost = -std::expm1(-rate * dt);
```

## よくあるミス

??? failure "小さい `x` で `exp(x) - 1` を使って、結果が 0 になる"
    `std::expm1` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exp`](exp.md) | 指数関数 |
| [`log1p`](log1p.md) | `log(1 + x)` を正確に求める |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `expm1(x)` は `exp(x) - 1`
    - [x] `x` が小さいときの桁落ちを防ぐ
    - [x] 逆の関数は `log1p`

## 関連ページ

- [`std::log1p`](log1p.md)
- [cpprefjp: std::expm1](https://cpprefjp.github.io/reference/cmath/expm1.html)
- [cppreference: std::expm1](https://en.cppreference.com/w/cpp/numeric/math/expm1)

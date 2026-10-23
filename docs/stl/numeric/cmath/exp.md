---
title: std::exp
summary: "e の x 乗（指数関数）を求める。"
order: 17
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::exp

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

キャラクターの速度を、時間とともに滑らかに減らしたい。体力の回復量を、時間に対して減衰させたい。こうした「だんだん小さくなる」動きの土台が、指数関数です。

`std::exp(x)` は、ネイピア数 e（約 2.718）の `x` 乗を返します。ゲームでは、フレーム時間に依存しない減衰（`exp(-k * dt)`）を書くために使います。

!!! tip "ポイント"
    - `std::exp(0.0)` は 1、`std::exp(1.0)` は e（約 2.71828）
    - `x` が大きいと急激に増え、オーバーフローで無限大になる
    - `exp(-k * dt)` は、フレームレートに依存しない減衰の係数
    - 2 の累乗は `exp2`、10 の累乗は `pow(10, x)`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exp {#exp}

```cpp
float exp(float x);
double exp(double x);
long double exp(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 指数。e の何乗かを指定する |

戻り値は e の `x` 乗です。`x` が 0 なら 1、正なら 1 より大きく、負なら 0 と 1 の間の値になります。`x` が −∞ に近づくと 0 に近づきます。

`x` が大きいと、結果が型の範囲を超えます。`double` では `x` が約 709.78 を超えると無限大になり、`float` では約 88.72 を超えると無限大です。これはオーバーフローとして扱われ、`HUGE_VAL` が返ります。逆に `x` がとても小さい負の値だと、結果は 0 に潰れます。

性質として、`exp(a + b) = exp(a) * exp(b)` が成り立ちます。この性質のおかげで、時間 `dt` ごとの減衰を、フレームが何回に分かれても同じ結果になる形で書けます。

落とし穴は、減衰を「毎フレーム 0.9 倍」のように書くと、フレームレートが変わったときに減衰の速さが変わってしまうことです。`exp(-k * dt)` を使えば、時間に対して一定になります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("exp(0) = {}", std::exp(0.0));
  std::println("exp(1) = {}", std::exp(1.0));      // ネイピア数 e

  // フレームレートに依存しない減衰（k=2.0、1 秒分）
  const double k = 2.0;
  double v60 = 10.0;                               // 60 FPS で 60 回に分ける
  for (int i = 0; i < 60; ++i) v60 *= std::exp(-k / 60.0);
  double v10 = 10.0;                               // 10 FPS で 10 回に分ける
  for (int i = 0; i < 10; ++i) v10 *= std::exp(-k / 10.0);
  std::println("同じ値になる: {}", std::abs(v60 - v10) < 1e-9);
}
```

```text title="実行結果"
exp(0) = 1
exp(1) = 2.718281828459045
同じ値になる: true
```

## ゲームでの使いどころ

速度やカメラの追従を、フレームレートに関係なく同じ速さで滑らかに減衰させるために使います。

```cpp
// 現在値を目標値に近づける。dt が変わっても結果が揃う
float Damp(float current, float target, float rate, float dt) {
  return target + (current - target) * std::exp(-rate * dt);
}
```

`rate` が大きいほど素早く追いつきます。`current += (target - current) * 0.1f;` のような書き方は、フレームレートで速さが変わるので、この形に置き換えると安定します。

## よくあるミス

??? failure "大きな値を渡して無限大になる"
    `double` で約 709、`float` で約 88 を超えないよう、入力を制限します。

??? failure "毎フレーム固定の倍率で減衰させて、フレームレートで挙動が変わる"
    `exp(-k * dt)` の形に直します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log`](log.md) | 自然対数。`exp` の逆 |
| [`exp2`](exp2.md) | 2 の `x` 乗 |
| [`pow`](pow.md) | 任意の底の累乗 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `exp(x)` は e の `x` 乗。`exp(0)` は 1
    - [x] 大きな `x` でオーバーフロー（double で約 709 超）
    - [x] `exp(-k * dt)` で、フレームレートに依存しない減衰

## 関連ページ

- [`std::log`](log.md)
- [cpprefjp: std::exp](https://cpprefjp.github.io/reference/cmath/exp.html)
- [cppreference: std::exp](https://en.cppreference.com/w/cpp/numeric/math/exp)

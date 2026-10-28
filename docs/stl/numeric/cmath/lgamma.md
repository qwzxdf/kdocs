---
title: std::lgamma
summary: "ガンマ関数の自然対数を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::lgamma

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

階乗やガンマ関数は、値が急激に大きくなります。組み合わせの数 C(100, 50) のような計算をそのまま階乗で書くと、途中でオーバーフローします。対数を取った値を足し引きするのが定石で、そのために使うのが `std::lgamma` です。

!!! tip "ポイント"
    - `std::lgamma(5.0)` は `log(24)` ≈ 3.178（4! の対数）
    - `log(tgamma(x))` と同じだが、大きな `x` でもオーバーフローしない
    - 符号は、グローバル変数 `signgam` に入る（スレッドセーフではない）
    - 組み合わせの数、確率の計算で使う

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lgamma {#lgamma}

<span class="ver ver-11">C++11</span>

```cpp
float lgamma(float x);
double lgamma(double x);
long double lgamma(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 入力。0 と負の整数は不可 |

戻り値は `log(|Γ(x)|)` です。`Γ(x)` が極端に大きくなる `x` でも、値は穏やかな範囲に収まります。

ガンマ関数が負になる `x`（負の非整数の一部）では、絶対値の対数が返り、符号は処理系のグローバル変数 `signgam`（POSIX）に入ります。この仕組みは、複数のスレッドから同時に呼ぶと干渉するため、符号が必要なら `lgamma_r` のような別の API を使います。

階乗の対数は `lgamma(n + 1)` で求まります。組み合わせの数 C(n, k) の対数は `lgamma(n + 1) - lgamma(k + 1) - lgamma(n - k + 1)` です。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("lgamma(1) = {}", std::lgamma(1.0));
  std::println("lgamma(5) = {:.4f}", std::lgamma(5.0));     // log(4!)
  // 100 の階乗の対数（直接の階乗は double を超える）
  std::println("log(100!) = {:.2f}", std::lgamma(101.0));
}
```

```text title="実行結果"
lgamma(1) = 0
lgamma(5) = 3.1781
log(100!) = 363.74
```

## ゲームでの使いどころ

組み合わせの数を桁あふれなしに扱います。

```cpp
// C(n, k) の対数。大きな n でもあふれない
const double log_c = std::lgamma(n + 1.0) - std::lgamma(k + 1.0) - std::lgamma(n - k + 1.0);
const double c = std::exp(log_c);
```

## よくあるミス

??? failure "スレッドから同時に呼び、`signgam` が壊れる"
    符号が必要な場合は、スレッドセーフな別の関数を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tgamma`](tgamma.md) | ガンマ関数そのもの |
| [`log`](log.md) | 自然対数 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `lgamma(x)` は `log(|Γ(x)|)`
    - [x] 大きな値でもオーバーフローしない
    - [x] 符号は `signgam`（スレッドセーフでない）

## 関連ページ

- [cpprefjp: std::lgamma](https://cpprefjp.github.io/reference/cmath/lgamma.html)
- [cppreference: std::lgamma](https://en.cppreference.com/w/cpp/numeric/math/lgamma)

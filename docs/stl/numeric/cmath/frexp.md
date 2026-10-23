---
title: std::frexp
summary: "小数を、仮数（0.5〜1）と 2 の指数に分ける。"
order: 42
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::frexp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

浮動小数点数を、「0.5 以上 1 未満の仮数」と「2 の累乗の指数」に分解したいことがあります。値の大きさ（桁数）を調べる、あるいは丸めを自分で制御する数値計算です。

`std::frexp` は、<strong>値を仮数と指数に分解して</strong>返します。

!!! tip "ポイント"
    - `std::frexp(12.0, &e)` は 0.75 を返し、`e` に 4 が入る（12 = 0.75 × 2⁴）
    - 仮数の絶対値は 0.5 以上 1 未満（0 は例外）
    - 逆の組み立ては `ldexp`
    - 値の大きさ（2 の何乗の桁か）を調べるのに使える

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::frexp {#frexp}

```cpp
float frexp(float x, int* exp);
double frexp(double x, int* exp);
long double frexp(long double x, int* exp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 分解したい値 |
| `exp` | `int` のポインタ | 指数の書き込み先 |

戻り値は仮数 `m`、`*exp` に指数 `e` が入り、`x = m * 2^e` が成り立ちます。仮数の絶対値は 0.5 以上 1 未満で、符号は `x` に従います。

`x` が 0 なら仮数も指数も 0 です。無限大と NaN では、`*exp` の値は不定で、戻り値が `x` そのものです。

`exp` に `nullptr` を渡すと未定義動作です。

用途は主に数値計算ライブラリですが、「この値は 2 の何乗くらいの大きさか」を調べるのに使えます。`log2` の切り捨て（`floor(log2(x))`）と同様の情報が、誤差なく得られます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  int e;
  const double m = std::frexp(12.0, &e);
  std::println("12 = {} * 2^{}", m, e);           // 0.75 * 16
  std::println("元に戻す: {}", std::ldexp(m, e));
}
```

```text title="実行結果"
12 = 0.75 * 2^4
元に戻す: 12
```

## ゲームでの使いどころ

値のおおよその桁（2 の何乗か）を調べるときに使います。ゲームの通常のコードで登場することは少なく、数値計算の補助として知っておく程度で足ります。

## よくあるミス

??? failure "`exp` の `nullptr` を渡して落ちる"
    指数用の変数を用意して、アドレスを渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ldexp`](ldexp.md) | 仮数と指数から値を組み立てる（逆の操作） |
| [`ilogb`](ilogb.md) | 指数を整数で返す |
| [`log2`](log2.md) | 底 2 の対数 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `frexp(x, &e)` は `x = m * 2^e` に分解する
    - [x] 仮数 `m` は 0.5 以上 1 未満
    - [x] 組み立てるには `ldexp`

## 関連ページ

- [`std::ldexp`](ldexp.md)
- [cpprefjp: std::frexp](https://cpprefjp.github.io/reference/cmath/frexp.html)
- [cppreference: std::frexp](https://en.cppreference.com/w/cpp/numeric/math/frexp)

---
title: std::tgamma
summary: "ガンマ関数（階乗の一般化）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::tgamma

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

階乗 n! は、整数にしか定義されません。5! は 120、5.5! はどうなるのか。ガンマ関数は、階乗を実数に広げた関数で、`Γ(n) = (n-1)!` という関係があります。

`std::tgamma` は、ガンマ関数 Γ(x) を計算します。確率分布や組み合わせの計算で使われます。

!!! tip "ポイント"
    - `std::tgamma(5.0)` は 24（4!）。`Γ(n) = (n−1)!`
    - `x` が 0 や負の整数では定義されない（NaN か極）
    - 値が非常に速く増える。`x` が約 171 を超えると `double` でオーバーフロー
    - 大きな値には対数を取った `lgamma` を使う

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::tgamma {#tgamma}

<span class="ver ver-11">C++11</span>

```cpp
float tgamma(float x);
double tgamma(double x);
long double tgamma(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 入力。0 と負の整数は不可 |

戻り値は Γ(x) です。正の整数 n に対しては (n−1)! に一致します。`tgamma(1)` は 1、`tgamma(2)` は 1、`tgamma(5)` は 24 です。

`x` が 0 のとき、極となって ±∞ を返し、負の整数では NaN を返します。

値の増え方が階乗並みに速いので、`double` では約 171.6 を超えるとオーバーフローします。大きな引数では、`lgamma`（Γ の対数）を使い、対数のまま足し算・引き算します。

名前の `t` は「true gamma」で、`lgamma` との区別です。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("tgamma(1) = {}", std::tgamma(1.0));
  std::println("tgamma(5) = {}", std::tgamma(5.0));    // 4! = 24
  std::println("tgamma(6) = {}", std::tgamma(6.0));    // 5! = 120
}
```

```text title="実行結果"
tgamma(1) = 1
tgamma(5) = 24
tgamma(6) = 120
```

## ゲームでの使いどころ

組み合わせの数や、確率分布（ポアソン分布、ガンマ分布）の計算に使います。ゲームのバランス調整のためのシミュレーションなど、確率を扱う場面で出てきます。

```cpp
// 5 個から 2 個を選ぶ組み合わせ数 C(5, 2) = 5! / (2! * 3!)
const double c = std::tgamma(6.0) / (std::tgamma(3.0) * std::tgamma(4.0));  // 10
```

整数の階乗なら、自分で整数のループで計算するほうが正確で速いです。

## よくあるミス

??? failure "大きな引数でオーバーフローする"
    `lgamma` で対数のまま計算します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lgamma`](lgamma.md) | ガンマ関数の対数 |
| [`erf`](erf.md) | 誤差関数 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `tgamma(x)` はガンマ関数。`Γ(n) = (n−1)!`
    - [x] 0 と負の整数は定義されない
    - [x] 大きな値は `lgamma`（対数）を使う

## 関連ページ

- [`std::lgamma`](lgamma.md)
- [cpprefjp: std::tgamma](https://cpprefjp.github.io/reference/cmath/tgamma.html)
- [cppreference: std::tgamma](https://en.cppreference.com/w/cpp/numeric/math/tgamma)

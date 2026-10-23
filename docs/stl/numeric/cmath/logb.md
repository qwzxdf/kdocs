---
title: std::logb
summary: "x の指数部を、浮動小数点で返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::logb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::ilogb` が指数を `int` で返すのに対し、`std::logb` は、<strong>指数を浮動小数点数で返し</strong>ます。非正規化数でも正しい指数を返す点が、`frexp` などと違います。

!!! tip "ポイント"
    - `std::logb(8.0)` は 3.0、`std::logb(10.0)` も 3.0
    - 戻り値は浮動小数点数
    - 0 は −∞、無限大は +∞を返す
    - `ilogb` は整数で返す

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logb {#logb}

<span class="ver ver-11">C++11</span>

```cpp
float logb(float x);
double logb(double x);
long double logb(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 指数を調べたい値 |

戻り値は、`floor(log2(|x|))` に相当する指数を浮動小数点数で返したものです。`logb(8.0)` は 3、`logb(0.5)` は −1 です。

`x` が 0 のときは −∞（極のエラーとして扱われる）、無限大のときは +∞、NaN のときは NaN を返します。`ilogb` と違って、特別な値も浮動小数点数の範囲で表現できます。

非正規化数に対しても、正規化したときの指数を返します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("logb(8)   = {}", std::logb(8.0));
  std::println("logb(10)  = {}", std::logb(10.0));
  std::println("logb(0.5) = {}", std::logb(0.5));
}
```

```text title="実行結果"
logb(8)   = 3
logb(10)  = 3
logb(0.5) = -1
```

## ゲームでの使いどころ

指数を浮動小数点数のまま、そのあとの計算（`scalbn` など）に渡したいときに使います。ゲームのコードで使う場面はまれです。

## よくあるミス

??? failure "0 を渡して −∞が返る"
    0 は別に扱います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ilogb`](ilogb.md) | 指数を整数で返す |
| [`scalbn`](scalbn.md) | 2 の累乗を掛ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `logb(x)` は指数を浮動小数点数で返す
    - [x] 0 は −∞
    - [x] 整数が欲しいなら `ilogb`

## 関連ページ

- [cpprefjp: std::logb](https://cpprefjp.github.io/reference/cmath/logb.html)
- [cppreference: std::logb](https://en.cppreference.com/w/cpp/numeric/math/logb)

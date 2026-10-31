---
title: std::expint
summary: "指数積分 Ei(x) を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::expint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

光や熱が、煙や霧の中で弱まる様子を計算していくと、指数積分という関数が出てきます。`std::expint` は、その `Ei(x)` を返します。

!!! tip "ポイント"
    - `std::expint(1.0)` は約 1.8951
    - `x` が 0 のとき −∞
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - `Ei(x)`。`E1(x)` は `-expint(-x)` で求める

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::expint {#expint}

<span class="ver ver-17">C++17</span>

```cpp
double expint(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | `double` | 評価する位置 |

指数積分 Ei(x) の値を返します。放射伝達や、熱伝導の方程式の解に現れる関数です。

`std::expint(x)` は指数積分 `Ei(x)` を返します。`x > 0` では `Ei(x) = −∫_{−x}^{∞} e^(−t)/t dt`（主値）で、`x` が大きいと `e^x / x` に近づきます。`x < 0` では、`−E1(−x)`（`E1` は別の定義の指数積分）の値になるので、`E1(x) = −Ei(−x)` で求められます。

`x = 0` では、`−∞` を返します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  // Ei(x)
  std::println("Ei(1) = {:.4f}", std::expint(1.0));
  std::println("Ei(2) = {:.4f}", std::expint(2.0));

  // 負の引数からは、E1(x) = -Ei(-x) が求められる
  double x = 1.0;
  std::println("E1(1) = -Ei(-1) = {:.4f}", -std::expint(-x));

  // x が大きいと Ei(x) は e^x / x に近づく
  double big = 10.0;
  std::println("Ei(10) = {:.1f}, e^10 / 10 = {:.1f}", std::expint(big), std::exp(big) / big);
}
```

```text title="実行結果"
Ei(1) = 1.8951
Ei(2) = 4.9542
E1(1) = -Ei(-1) = 0.2194
Ei(10) = 2492.2, e^10 / 10 = 2202.6
```

`Ei(10)` は約 2492 で、`e^10 / 10` は約 2203 です。`x` が大きくなるほど、比が 1 に近づきます。

## ゲームでの使いどころ

放射伝達（光が媒質の中で弱まる様子）や、熱伝導の方程式の解に出てきます。霧や雲の描画の理論（大気散乱）の計算で、式変形のなかに現れます。ゲームで実時間に計算することはありません。

## よくあるミス

??? failure "x = 0 を渡す"
    負の無限大が返ります。`E1` を求めたいときは、符号と引数の向きを間違えないようにします。

??? failure "E1 と Ei を取り違える"
    `std::expint(x)` は `Ei(x)` です。`E1(x)` は `-std::expint(-x)` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tgamma`](tgamma.md) | ガンマ関数 |
| [`erf`](erf.md) | 誤差関数 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::expint` は指数積分
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::expint](https://cpprefjp.github.io/reference/cmath/expint.html)
- [cppreference: std::expint](https://en.cppreference.com/w/cpp/numeric/math/expint)

---
title: std::cyl_bessel_k
summary: "第 2 種変形ベッセル関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cyl_bessel_k

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

変形ベッセル関数のもう一方の解が、指数関数的に減衰する `K_ν(x)` です。`std::cyl_bessel_k` が返します。中心から離れると急速に弱まる、影響の範囲を表します。

!!! tip "ポイント"
    - `std::cyl_bessel_k(0.0, 1.0)` は約 0.4210
    - `x` は正の値
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 指数的に減衰する解。原点で発散する

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cyl_bessel_k {#cyl_bessel_k}

<span class="ver ver-17">C++17</span>

```cpp
double cyl_bessel_k(double nu, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `nu` | `double` | 次数 |
| `x` | `double` | 評価する位置（正の値） |

第 2 種変形ベッセル関数 K_ν(x) の値を返します。変形ベッセル関数のもう一方の解で、x が大きいと指数的に減衰します。

`nu` は次数、`x` は正の値です。`K_ν(x)` は、変形ベッセルの方程式の、減衰する解です。`x` が 0 に近づくと発散し、`x` が大きいと `√(π / 2x) · e^(−x)` に近づいて、指数的に 0 になります。

`x = 0` では発散するので使えません。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  // K_0(r): 中心から離れると急速に弱まる(湯川型の場など)
  for (double r : {0.1, 0.5, 1.0, 2.0, 4.0}) {
    std::println("K_0({}) = {:.5f}", r, std::cyl_bessel_k(0.0, r));
  }
}
```

```text title="実行結果"
K_0(0.1) = 2.42707
K_0(0.5) = 0.92442
K_0(1) = 0.42102
K_0(2) = 0.11389
K_0(4) = 0.01116
```

`r` が小さい所では急に大きく、遠くでは 0 に近づく様子が分かります。

## ゲームでの使いどころ

距離に応じて急速に弱まる影響範囲（力の場）を、物理的な根拠のある形で作りたいときに使えます。ゲームでは、単純な指数関数や、距離の逆 2 乗で済ませるのが普通です。

## よくあるミス

??? failure "x = 0 を渡す"
    発散します。

??? failure "I と取り違える"
    `cyl_bessel_i` は増加、`cyl_bessel_k` は減衰する解です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cyl_bessel_i`](cyl_bessel_i.md) | 増加する解 |
| [`cyl_bessel_j`](cyl_bessel_j.md) | 振動する解 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::cyl_bessel_k` は第 2 種変形ベッセル関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::cyl_bessel_k](https://cpprefjp.github.io/reference/cmath/cyl_bessel_k.html)
- [cppreference: std::cyl_bessel_k](https://en.cppreference.com/w/cpp/numeric/math/cyl_bessel_k)

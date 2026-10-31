---
title: std::cyl_neumann
summary: "ノイマン関数（第 2 種ベッセル関数）を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cyl_neumann

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

ベッセルの方程式には、中心で有限の解 `J_ν` のほかに、中心で発散する解があります。第 2 種ベッセル関数（ノイマン関数）`Y_ν(x)` で、`std::cyl_neumann` が返します。

!!! tip "ポイント"
    - `std::cyl_neumann(0.0, 1.0)` は約 0.0883
    - `x` は正の値（0 は発散する）
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 原点で発散する第 2 種。`J_ν` とペアで使う

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cyl_neumann {#cyl_neumann}

<span class="ver ver-17">C++17</span>

```cpp
double cyl_neumann(double nu, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `nu` | `double` | 次数（0 以上） |
| `x` | `double` | 評価する位置（正の値） |

第 2 種ベッセル関数 Y_ν(x)（ノイマン関数）の値を返します。第 1 種とともに、波動方程式の解を作ります。

`nu` は次数（0 以上）、`x` は正の値です。`Y_ν(x)` は、ベッセルの微分方程式の第 2 の解で、`x` が 0 に近づくと `−∞` に発散します。`x` が大きいと、`J_ν` と同じように振動し、`J_ν(x)² + Y_ν(x)² ≈ 2 / (π x)` が成り立ちます。

`x = 0` では、発散するので使えません。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;

  // x が小さいと、強く負に発散する
  for (double x : {0.01, 0.1, 1.0}) {
    std::println("Y_0({}) = {:.4f}", x, std::cyl_neumann(0.0, x));
  }

  // 大きい x では J^2 + Y^2 ≈ 2 / (π x)
  double x = 10.0;
  double j = std::cyl_bessel_j(0.0, x);
  double y = std::cyl_neumann(0.0, x);
  std::println("J_0(10)^2 + Y_0(10)^2 = {:.5f}", j * j + y * y);
  std::println("2 / (π × 10)          = {:.5f}", 2.0 / (kPi * x));
}
```

```text title="実行結果"
Y_0(0.01) = -3.0055
Y_0(0.1) = -1.5342
Y_0(1) = 0.0883
J_0(10)^2 + Y_0(10)^2 = 0.06358
2 / (π × 10)          = 0.06366
```

小さい `x` では対数的に負へ発散し、大きい `x` では、`J` と合わせた 2 乗和が `2/(πx)` に近づきます。

## ゲームでの使いどころ

中心に穴のある円形の領域（輪の形の太鼓、円筒の導波管）の波を扱うとき、`J_ν` と組み合わせて使います。ゲームで使う場面は、ほとんどありません。

## よくあるミス

??? failure "x = 0 を渡す"
    `−∞` に発散します。中心の穴がない問題では、`J_ν` だけを使います。

??? failure "J と取り違える"
    `cyl_bessel_j` が第 1 種（原点で有限）、`cyl_neumann` が第 2 種（原点で発散）です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cyl_bessel_j`](cyl_bessel_j.md) | 第 1 種。原点で有限 |
| [`sph_neumann`](sph_neumann.md) | 球面版 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::cyl_neumann` は第 2 種ベッセル関数（ノイマン関数）
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::cyl_neumann](https://cpprefjp.github.io/reference/cmath/cyl_neumann.html)
- [cppreference: std::cyl_neumann](https://en.cppreference.com/w/cpp/numeric/math/cyl_neumann)

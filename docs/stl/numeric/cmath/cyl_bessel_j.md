---
title: std::cyl_bessel_j
summary: "第 1 種ベッセル関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cyl_bessel_j

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

水面に石を落としたときの波紋や、円形の太鼓の膜の振動は、中心からの距離に対して、振動しながら弱まっていきます。この形を表すのが第 1 種ベッセル関数 `J_ν(x)` で、`std::cyl_bessel_j` が返します。

!!! tip "ポイント"
    - `std::cyl_bessel_j(0.0, 1.0)` は約 0.7652
    - `nu` と `x` は 0 以上
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 円形の波紋や膜の振動の形を表す

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cyl_bessel_j {#cyl_bessel_j}

<span class="ver ver-17">C++17</span>

```cpp
double cyl_bessel_j(double nu, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `nu` | `double` | 次数（0 以上） |
| `x` | `double` | 評価する位置（0 以上） |

第 1 種ベッセル関数 J_ν(x) の値を返します。円形の膜の振動、波の伝わり方などに現れます。

`nu` は次数（0 以上）、`x` は 0 以上の位置です。`J_0(0) = 1` で、`J_ν(0) = 0`（`ν > 0`）です。`x` が大きくなると、振幅がゆっくり小さくなりながら、符号を変えて振動します。`J_0` が 0 を横切る最初の位置は、約 2.4048 です。

円形の太鼓の膜の振動や、水面の波紋の形が、この関数で表されます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  // 中心からの距離 r に応じた、水面の波紋の高さ: J_0(k r)
  double k = 2.0;   // 波数
  for (double r : {0.0, 0.5, 1.0, 1.5, 2.0, 3.0}) {
    std::println("r = {:.1f}: 高さ {:+.4f}", r, std::cyl_bessel_j(0.0, k * r));
  }

  // J_0 の最初の零点(約 2.4048)では、ほぼ 0
  std::println("J_0(2.4048) = {:.6f}", std::cyl_bessel_j(0.0, 2.4048));
}
```

```text title="実行結果"
r = 0.0: 高さ +1.0000
r = 0.5: 高さ +0.7652
r = 1.0: 高さ +0.2239
r = 1.5: 高さ -0.2601
r = 2.0: 高さ -0.3971
r = 3.0: 高さ +0.1506
J_0(2.4048) = 0.000013
```

中心 `r = 0` で最大の 1 になり、外側へ向かって、符号を変えながら小さくなる波紋が得られます。2.4048 付近では、ほぼ 0 です。

## ゲームでの使いどころ

円形の波紋（水面の波）を、頂点シェーダーで動かすときの高さ関数に使えます。`sin` を使った単純な波よりも、中心から広がるにつれて弱まる自然な形になります。リアルタイムでは、事前に計算した表を引くのが普通です。

## よくあるミス

??? failure "x に負の値を渡す"
    `x` は 0 以上です。

??? failure "nu に整数以外を渡して驚く"
    `nu` は実数で構いません。`nu` が半整数のときは、球ベッセル関数と関係します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cyl_neumann`](cyl_neumann.md) | 第 2 種。0 で発散する解 |
| [`cyl_bessel_i`](cyl_bessel_i.md) | 変形ベッセル関数。振動しない |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::cyl_bessel_j` は第 1 種ベッセル関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::cyl_bessel_j](https://cpprefjp.github.io/reference/cmath/cyl_bessel_j.html)
- [cppreference: std::cyl_bessel_j](https://en.cppreference.com/w/cpp/numeric/math/cyl_bessel_j)

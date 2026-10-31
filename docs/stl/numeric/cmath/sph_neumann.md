---
title: std::sph_neumann
summary: "球ノイマン関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sph_neumann

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

球ベッセル関数と対になる、中心で発散する解が、球ノイマン関数 `n_n(x)` です。`std::sph_neumann` が返します。

!!! tip "ポイント"
    - `std::sph_neumann(0, 1.0)` は −cos(1) / 1 ≈ −0.5403
    - `x` は正の値
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 原点で発散する球面波の解

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sph_neumann {#sph_neumann}

<span class="ver ver-17">C++17</span>

```cpp
double sph_neumann(unsigned int n, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `unsigned int` | 次数 |
| `x` | `double` | 評価する位置（正の値） |

球ノイマン関数 n_n(x) の値を返します。球ベッセル関数と対になる、第 2 種の解です。

`n` は次数（0 以上の整数）、`x` は正の値です。`n_n(x)` は球ノイマン関数で、`n_0(x) = −cos x / x`、`n_1(x) = −cos x / x² − sin x / x` と、初等関数で書けます。`x` が 0 に近づくと、発散します。

球ベッセル関数 `j_n` とペアで、球対称な波の方程式の一般解を作ります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double x = 1.0;

  // n_0(x) = -cos(x) / x
  std::println("n_0(1) = {:.4f}, -cos(x)/x = {:.4f}", std::sph_neumann(0, x), -std::cos(x) / x);

  // n_1(x) = -cos(x)/x^2 - sin(x)/x
  std::println("n_1(1) = {:.4f}, 式 = {:.4f}", std::sph_neumann(1, x), -std::cos(x) / (x * x) - std::sin(x) / x);
}
```

```text title="実行結果"
n_0(1) = -0.5403, -cos(x)/x = -0.5403
n_1(1) = -1.3818, 式 = -1.3818
```

低い次数は、式どおりの値になります。

## ゲームでの使いどころ

中心に近い所で発散するので、球の中心を含む問題では使えません。外側からの波を扱う、散乱の理論の計算に出てきます。ゲームで使うことは、ほとんどありません。

## よくあるミス

??? failure "x = 0 を渡す"
    発散します。

??? failure "sph_bessel と取り違える"
    `sph_bessel` は原点で有限、`sph_neumann` は原点で発散する解です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sph_bessel`](sph_bessel.md) | 第 1 種。原点で有限 |
| [`cyl_neumann`](cyl_neumann.md) | 円柱版 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::sph_neumann` は球ノイマン関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::sph_neumann](https://cpprefjp.github.io/reference/cmath/sph_neumann.html)
- [cppreference: std::sph_neumann](https://en.cppreference.com/w/cpp/numeric/math/sph_neumann)

---
title: std::legendre
summary: "ルジャンドル多項式を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::legendre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

球の形をした問題（球対称な重力の場、球面上の光の分布）を扱うと、角度に対して決まった形の波が出てきます。`std::legendre` は、その基になるルジャンドル多項式 `P_l(x)` を返します。

!!! tip "ポイント"
    - `std::legendre(2, 0.5)` は −0.125（(3 × 0.25 − 1) / 2）
    - `x` は −1 〜 1 の範囲を想定する
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - ルジャンドル多項式は球面調和関数の元になる。SH ライティングの基礎

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::legendre {#legendre}

<span class="ver ver-17">C++17</span>

```cpp
double legendre(unsigned int l, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `l` | `unsigned int` | 次数 |
| `x` | `double` | 評価する位置（−1 〜 1） |

ルジャンドル多項式 P_l(x) の値を返します。球対称な問題（重力、静電場）の展開に現れる、次数 l の多項式です。x は −1 〜 1 の範囲を想定します。

次数 `l` は 0 以上の整数で、`x` は −1 から 1 の範囲です。`P_0(x) = 1`、`P_1(x) = x`、`P_2(x) = (3x² − 1) / 2` と続き、`l` が大きくなるほど、符号が入れ替わる回数が増えます。次の漸化式で、次数を 1 つずつ上げられます。

`(l + 1) P_{l+1}(x) = (2l + 1) x P_l(x) − l P_{l−1}(x)`

`std::legendre` は、この漸化式と同等の計算を内部で行います。範囲外の `x`（絶対値が 1 を超える値）を渡すと、結果は規格では定まらず、NaN などが返ります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double x = 0.5;
  // P_0 .. P_3 を標準ライブラリで求める
  for (unsigned int l = 0; l <= 3; ++l) {
    std::println("P_{}(0.5) = {:.4f}", l, std::legendre(l, x));
  }

  // 漸化式で P_3 を求めて、答え合わせをする
  double p0 = 1.0;
  double p1 = x;
  double p2 = (3 * x * p1 - 1 * p0) / 2;        // (l+1) P_{l+1} = (2l+1) x P_l - l P_{l-1}, l = 1
  double p3 = (5 * x * p2 - 2 * p1) / 3;        // l = 2
  std::println("漸化式の P_3 = {:.4f}", p3);
}
```

```text title="実行結果"
P_0(0.5) = 1.0000
P_1(0.5) = 0.5000
P_2(0.5) = -0.1250
P_3(0.5) = -0.4375
漸化式の P_3 = -0.4375
```

標準ライブラリの値と、漸化式で自分で求めた値が一致します。次数が低いうちは、多項式を直接書いたほうが速いので、`std::legendre` は、次数を実行時に変えたいときに使います。

## ゲームでの使いどころ

球面調和関数ライティング（SH ライティング）の基礎になる関数です。環境光を、球面上の関数として、少ない係数で近似する手法で、その基底は、ルジャンドル関数から作られます。ただし、ゲームのコードでは、低次（2 次まで）の基底を、定数として直接書くのが普通です。

## よくあるミス

??? failure "x の範囲を超える値を渡す"
    `x` は −1 から 1 です。角度 θ から使うなら、`std::cos(theta)` を渡します。

??? failure "次数を引数の最初と思い違える"
    第 1 引数が次数 `l`、第 2 引数が `x` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`assoc_legendre`](assoc_legendre.md) | 陪ルジャンドル関数。次数 `m` が加わる |
| [`sph_legendre`](sph_legendre.md) | 球面調和関数の θ 方向の部分 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::legendre` はルジャンドル多項式
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::legendre](https://cpprefjp.github.io/reference/cmath/legendre.html)
- [cppreference: std::legendre](https://en.cppreference.com/w/cpp/numeric/math/legendre)

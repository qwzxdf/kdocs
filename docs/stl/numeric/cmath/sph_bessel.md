---
title: std::sph_bessel
summary: "球ベッセル関数（第 1 種）を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sph_bessel

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

点から 3 次元に広がる波の、中心からの距離に応じた形を表すのが、球ベッセル関数 `j_n(x)` です。最低次の `j_0(x)` は `sin x / x` で、`std::sph_bessel` が返します。

!!! tip "ポイント"
    - `std::sph_bessel(0, 1.0)` は sin(1) / 1 ≈ 0.8415
    - `x` は 0 以上
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - `j_0(x)` は `sin(x)/x`（sinc 関数）

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sph_bessel {#sph_bessel}

<span class="ver ver-17">C++17</span>

```cpp
double sph_bessel(unsigned int n, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `unsigned int` | 次数 |
| `x` | `double` | 評価する位置（0 以上） |

球ベッセル関数 j_n(x) の値を返します。球対称な波動の問題（球面上での波の散乱）で使われます。

`n` は次数（0 以上の整数）、`x` は 0 以上です。`j_n(x)` は球ベッセル関数で、`j_0(x) = sin x / x`、`j_1(x) = (sin x − x cos x) / x²` と、初等関数で書けます。`x = 0` では、`j_0(0) = 1`、`j_n(0) = 0`（`n > 0`）です。

3 次元の球対称な波の、中心から広がる方向の部分に出てきます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double x = 1.0;

  // j_0(x) = sin(x) / x
  std::println("j_0(1) = {:.4f}, sin(x)/x = {:.4f}", std::sph_bessel(0, x), std::sin(x) / x);

  // j_1(x) = (sin(x) - x cos(x)) / x^2
  std::println("j_1(1) = {:.4f}, 式 = {:.4f}", std::sph_bessel(1, x), (std::sin(x) - x * std::cos(x)) / (x * x));

  // x = 0 では j_0 だけが 1
  std::println("j_0(0) = {}, j_1(0) = {}", std::sph_bessel(0, 0.0), std::sph_bessel(1, 0.0));
}
```

```text title="実行結果"
j_0(1) = 0.8415, sin(x)/x = 0.8415
j_1(1) = 0.3012, 式 = 0.3012
j_0(0) = 1, j_1(0) = 0
```

初等関数で書ける低い次数は、式どおりの値になります。

## ゲームでの使いどころ

3 次元の球面波（点光源から広がる音や光の波）の、理論的な計算に出てきます。`sinc` 関数（`sin x / x`）としては、画像のリサンプリングで見かけます。

## よくあるミス

??? failure "x に負の値を渡す"
    `x` は 0 以上です。

??? failure "円柱版と取り違える"
    `cyl_bessel_j` は円柱座標、`sph_bessel` は球座標の関数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cyl_bessel_j`](cyl_bessel_j.md) | 円柱座標版 |
| [`sph_neumann`](sph_neumann.md) | 球面の第 2 種 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::sph_bessel` は球ベッセル関数（第 1 種）
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::sph_bessel](https://cpprefjp.github.io/reference/cmath/sph_bessel.html)
- [cppreference: std::sph_bessel](https://en.cppreference.com/w/cpp/numeric/math/sph_bessel)

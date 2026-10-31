---
title: std::cyl_bessel_i
summary: "第 1 種変形ベッセル関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cyl_bessel_i

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

ベッセル関数の引数を虚数にすると、振動せず、指数関数的に増える関数になります。変形ベッセル関数 `I_ν(x)` で、`std::cyl_bessel_i` が返します。オーディオの窓関数にも使われます。

!!! tip "ポイント"
    - `std::cyl_bessel_i(0.0, 1.0)` は約 1.2661
    - `nu` と `x` は 0 以上
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - Kaiser 窓の計算に使える。指数的に増える

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cyl_bessel_i {#cyl_bessel_i}

<span class="ver ver-17">C++17</span>

```cpp
double cyl_bessel_i(double nu, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `nu` | `double` | 次数（0 以上） |
| `x` | `double` | 評価する位置（0 以上） |

第 1 種変形ベッセル関数 I_ν(x) の値を返します。ベッセル関数の虚数引数版で、振動せず指数的に増えます。熱伝導や、Kaiser 窓などの信号処理に出てきます。

`nu` は次数（0 以上）、`x` は 0 以上です。`I_ν(x)` は、ベッセル関数の引数が虚数になった版で、振動せず、`x` が大きいと指数的に増えます。`I_0(0) = 1` です。

デジタル信号処理で使う、Kaiser 窓は、`I_0` を使って作ります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  // Kaiser 窓: w[n] = I_0(β sqrt(1 - (2n/(N-1) - 1)^2)) / I_0(β)
  constexpr int kN = 9;
  double beta = 5.0;
  for (int n = 0; n < kN; ++n) {
    double r = 2.0 * n / (kN - 1) - 1.0;   // -1 〜 1
    double w = std::cyl_bessel_i(0.0, beta * std::sqrt(1.0 - r * r)) / std::cyl_bessel_i(0.0, beta);
    std::println("w[{}] = {:.4f}", n, w);
  }
}
```

```text title="実行結果"
w[0] = 0.0367
w[1] = 0.2305
w[2] = 0.5529
w[3] = 0.8680
w[4] = 1.0000
w[5] = 0.8680
w[6] = 0.5529
w[7] = 0.2305
w[8] = 0.0367
```

窓の中心が 1、端が 0 に近い、ベル型の窓になります。`beta` を大きくすると、端が絞られて細くなります。

## ゲームでの使いどころ

オーディオのリサンプリングや、フィルターの設計に使う Kaiser 窓の計算で出てきます。サウンドシステムの自作や、音声の事前処理のツールを作るときに使えます。

## よくあるミス

??? failure "x に負の値を渡す"
    `x` は 0 以上です。

??? failure "x が大きいときの桁あふれ"
    指数的に増えるので、`x` が数百になると桁あふれします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cyl_bessel_j`](cyl_bessel_j.md) | 引数が実数のベッセル関数。振動する |
| [`cyl_bessel_k`](cyl_bessel_k.md) | 変形ベッセル関数の、減衰する解 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::cyl_bessel_i` は第 1 種変形ベッセル関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::cyl_bessel_i](https://cpprefjp.github.io/reference/cmath/cyl_bessel_i.html)
- [cppreference: std::cyl_bessel_i](https://en.cppreference.com/w/cpp/numeric/math/cyl_bessel_i)

---
title: std::assoc_legendre
summary: "ルジャンドル陪関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::assoc_legendre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

球の表面に広がる波の形を表すには、ルジャンドル多項式に、東西方向の変化を表す次数 `m` を加えた「陪ルジャンドル関数」が必要になります。`std::assoc_legendre` は、その値を返します。

!!! tip "ポイント"
    - `std::assoc_legendre(1, 1, 0.5)` は約 0.8660（√0.75）
    - `m` は `l` 以下、`x` は −1 〜 1
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 位相因子 (−1)^m を含まない定義。他のライブラリの値と符号が違うことがある

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::assoc_legendre {#assoc_legendre}

<span class="ver ver-17">C++17</span>

```cpp
double assoc_legendre(unsigned int l, unsigned int m, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `l` | `unsigned int` | 次数 |
| `m` | `unsigned int` | 補助の次数（l 以下） |
| `x` | `double` | 評価する位置（−1 〜 1） |

陪ルジャンドル関数 P_l^m(x) の値を返します。球面調和関数の元になる関数です。C++ の定義には、Condon–Shortley の位相因子 (−1)^m が含まれません。

次数 `l` と `m` は 0 以上の整数で、`m ≤ l` でなければなりません。`x` は −1 から 1 の範囲です。`m = 0` のときは、ルジャンドル多項式 `P_l(x)` と同じです。

C++ の `std::assoc_legendre` は、位相因子 `(−1)^m`（Condon–Shortley の位相）を含みません。数学の教科書や、他のライブラリの値と、`m` が奇数のときに符号が逆になることがあります。比べるときは、定義を確かめます。

`m ≤ l` を満たさない値を渡すと、結果は 0 になります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double x = 0.5;
  // P_1^0 は x、P_1^1 は sqrt(1 - x^2)
  std::println("P_1^0(0.5) = {:.4f}", std::assoc_legendre(1, 0, x));
  std::println("P_1^1(0.5) = {:.4f}", std::assoc_legendre(1, 1, x));
  std::println("sqrt(1 - x^2) = {:.4f}", std::sqrt(1 - x * x));

  // P_2^1 = 3 x sqrt(1 - x^2)
  std::println("P_2^1(0.5) = {:.4f}", std::assoc_legendre(2, 1, x));
  std::println("3 x sqrt(1 - x^2) = {:.4f}", 3 * x * std::sqrt(1 - x * x));

  // m が l より大きいと 0
  std::println("P_1^2(0.5) = {}", std::assoc_legendre(1, 2, x));
}
```

```text title="実行結果"
P_1^0(0.5) = 0.5000
P_1^1(0.5) = 0.8660
sqrt(1 - x^2) = 0.8660
P_2^1(0.5) = 1.2990
3 x sqrt(1 - x^2) = 1.2990
P_1^2(0.5) = 0
```

`P_1^1` は `√(1 − x²)`、`P_2^1` は `3x√(1 − x²)` と、式どおりの値になります。C++ の定義は、`(−1)^m` を含まないので、符号が正のままです。

## ゲームでの使いどころ

球面調和関数 `Y_l^m(θ, φ)` を自分で組み立てるときの部品です。ただし、必要な次数は少ないので、`sph_legendre` や定数で済ませるのが普通です。

## よくあるミス

??? failure "位相因子の有無を気にしない"
    `m` が奇数のとき、他のライブラリの値と符号が逆になります。Boost などと比べるときは、定義を確かめます。

??? failure "m が l より大きい値を渡す"
    結果は 0 になります。エラーにはなりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`legendre`](legendre.md) | `m = 0` の場合 |
| [`sph_legendre`](sph_legendre.md) | 正規化と位相を含めた球面調和関数の θ 部分 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::assoc_legendre` は陪ルジャンドル関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::assoc_legendre](https://cpprefjp.github.io/reference/cmath/assoc_legendre.html)
- [cppreference: std::assoc_legendre](https://en.cppreference.com/w/cpp/numeric/math/assoc_legendre)

---
title: std::sph_legendre
summary: "球面調和関数の θ 部分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sph_legendre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

空からの光を方向ごとの明るさで表した環境光は、球の表面に広がる関数です。これを少ない係数で近似するのが球面調和関数ライティングで、その北極から南極へ向かう方向（極角 θ）の形が、`std::sph_legendre` で求まります。

!!! tip "ポイント"
    - `std::sph_legendre(0, 0, θ)` は定数 1 / (2√π) ≈ 0.2821
    - `theta` はラジアン
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 環境光を球面調和関数で表す SH ライティングの基底。ふつうは低次を定数で書く

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sph_legendre {#sph_legendre}

<span class="ver ver-17">C++17</span>

```cpp
double sph_legendre(unsigned int l, unsigned int m, double theta);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `l` | `unsigned int` | 次数 |
| `m` | `unsigned int` | 補助の次数（l 以下） |
| `theta` | `double` | 極角（ラジアン） |

球面調和関数の θ 方向の部分 Y_l^m(θ, 0) の値を返します。球面上の関数の展開（環境光の球面調和関数ライティングなど）の基礎になります。

`l`・`m` は 0 以上の整数で `m ≤ l`、`theta` は極角（ラジアン、0 から π）です。戻り値は、球面調和関数の θ 方向の部分 `Y_l^m(θ, 0)` で、球面全体で 2 乗して積分すると 1 になるように、正規化されています。

`std::assoc_legendre` に正規化の係数を掛けたものですが、C++ の `sph_legendre` は、`(−1)^m` の位相因子を含みません。

球面調和関数の `φ` 方向は、`cos(mφ)` などの周期関数なので、必要なら自分で掛けます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;

  // Y_0^0 は定数 1 / (2 sqrt(pi))
  std::println("Y_0^0 = {:.4f}", std::sph_legendre(0, 0, 0.0));
  std::println("1 / (2 sqrt(pi)) = {:.4f}", 1.0 / (2.0 * std::sqrt(kPi)));

  // Y_1^0 は sqrt(3 / (4 pi)) * cos(theta)。真上 (theta = 0) で最大
  double c = std::sqrt(3.0 / (4.0 * kPi));
  for (double deg : {0.0, 60.0, 90.0}) {
    double theta = deg * kPi / 180.0;
    std::println("theta = {:>3} 度: Y_1^0 = {:.4f} (式: {:.4f})", deg, std::sph_legendre(1, 0, theta), c * std::cos(theta));
  }
}
```

```text title="実行結果"
Y_0^0 = 0.2821
1 / (2 sqrt(pi)) = 0.2821
theta =   0 度: Y_1^0 = 0.4886 (式: 0.4886)
theta =  60 度: Y_1^0 = 0.2443 (式: 0.2443)
theta =  90 度: Y_1^0 = 0.0000 (式: 0.0000)
```

`Y_0^0` は方向によらない定数で、`Y_1^0` は `cos θ` に比例します（真上で最大、真横で 0）。環境光を表す SH の、1 次までの基底が、この形です。

## ゲームでの使いどころ

球面調和関数ライティング（SH ライティング）で、環境光を係数で圧縮するときの基底です。実際のゲームでは、2 次までの 9 係数の基底を、定数としてシェーダーに直接書きます。この関数は、高い次数の基底を作る、事前計算のツールで使います。

## よくあるミス

??? failure "極角を度のまま渡す"
    `theta` はラジアンです。度から変換してから渡します。

??? failure "φ 方向の部分も含まれると思う"
    `φ = 0` の値だけです。経度の方向は、`cos(mφ)` などを自分で掛けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`assoc_legendre`](assoc_legendre.md) | 正規化なしの陪ルジャンドル関数 |
| [`legendre`](legendre.md) | `m = 0` で正規化なしの多項式 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::sph_legendre` は球面調和関数のルジャンドル部分
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::sph_legendre](https://cpprefjp.github.io/reference/cmath/sph_legendre.html)
- [cppreference: std::sph_legendre](https://en.cppreference.com/w/cpp/numeric/math/sph_legendre)

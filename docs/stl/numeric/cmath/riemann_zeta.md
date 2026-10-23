---
title: std::riemann_zeta
summary: "リーマンのゼータ関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::riemann_zeta

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

`std::riemann_zeta` は、数学の特殊関数の 1 つ、リーマンのゼータ関数を計算します。物理や信号処理、統計の計算に使われる関数で、ゲームのコードで直接使う機会は、ほとんどありません。C++17 で標準に加わったものの 1 つとして、存在と使い方を知っておけば足ります。

!!! tip "ポイント"
    - `std::riemann_zeta(2.0)` は π² / 6 ≈ 1.6449
    - `x` が 1 のとき発散する
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - ゲームでの出番はほぼない。物理シミュレーションや信号処理のツールで使う

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::riemann_zeta {#riemann_zeta}

<span class="ver ver-17">C++17</span>

```cpp
double riemann_zeta(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | `double` | 評価する位置（1 以外） |

リーマンのゼータ関数 ζ(s) の値を返します。数論や、統計力学に現れる関数です。

ζ(2) = π² / 6 ≈ 1.6449。

数値の精度は実装依存です。結果を比べるときは、`==` ではなく、許容誤差を使います。引数が定義域を外れた場合は、NaN を返し、`errno` に `EDOM` が設定されることがあります。

使う分野は、数論、統計力学です。ゲームでは、このような関数が必要になる計算は、通常、既存のライブラリ（物理エンジンや信号処理のライブラリ）の内部に隠れています。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("ζ(2) = {:.4f}", std::riemann_zeta(2.0));
}
```

```text title="実行結果"
1.6449
```

## ゲームでの使いどころ

ゲームのコードで使う場面はほとんどありません。用途は数論、統計力学です。必要になったら、ここで関数の名前と引数の並びを確かめてください。

## よくあるミス

??? failure "引数の順序を取り違える"
    各引数の意味は、上の表で確かめます。

??? failure "`==` で結果を比べる"
    許容誤差を使って比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<cmath>`](../cmath.md) | 数学関数の一覧 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::riemann_zeta` はリーマンのゼータ関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::riemann_zeta](https://cpprefjp.github.io/reference/cmath/riemann_zeta.html)
- [cppreference: std::riemann_zeta](https://en.cppreference.com/w/cpp/numeric/math/riemann_zeta)

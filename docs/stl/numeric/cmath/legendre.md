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

`std::legendre` は、数学の特殊関数の 1 つ、ルジャンドル多項式を計算します。物理や信号処理、統計の計算に使われる関数で、ゲームのコードで直接使う機会は、ほとんどありません。C++17 で標準に加わったものの 1 つとして、存在と使い方を知っておけば足ります。

!!! tip "ポイント"
    - `std::legendre(2, 0.5)` は −0.125（(3 × 0.25 − 1) / 2）
    - `x` は −1 〜 1 の範囲を想定する
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - ゲームでの出番はほぼない。物理シミュレーションや信号処理のツールで使う

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

P_0(x) = 1、P_1(x) = x、P_2(x) = (3x² − 1) / 2、…と続きます。

数値の精度は実装依存です。結果を比べるときは、`==` ではなく、許容誤差を使います。引数が定義域を外れた場合は、NaN を返し、`errno` に `EDOM` が設定されることがあります。

使う分野は、球対称な場の展開です。ゲームでは、このような関数が必要になる計算は、通常、既存のライブラリ（物理エンジンや信号処理のライブラリ）の内部に隠れています。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("P_2(0.5) = {}", std::legendre(2, 0.5));
}
```

```text title="実行結果"
P_2(0.5) = -0.125
```

## ゲームでの使いどころ

ゲームのコードで使う場面はほとんどありません。用途は球対称な場の展開です。必要になったら、ここで関数の名前と引数の並びを確かめてください。

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
    - [x] `std::legendre` はルジャンドル多項式
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::legendre](https://cpprefjp.github.io/reference/cmath/legendre.html)
- [cppreference: std::legendre](https://en.cppreference.com/w/cpp/numeric/math/legendre)

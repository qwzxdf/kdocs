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

`std::assoc_legendre` は、数学の特殊関数の 1 つ、陪ルジャンドル関数を計算します。物理や信号処理、統計の計算に使われる関数で、ゲームのコードで直接使う機会は、ほとんどありません。C++17 で標準に加わったものの 1 つとして、存在と使い方を知っておけば足ります。

!!! tip "ポイント"
    - `std::assoc_legendre(1, 1, 0.5)` は約 0.8660（√0.75）
    - `m` は `l` 以下、`x` は −1 〜 1
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - ゲームでの出番はほぼない。物理シミュレーションや信号処理のツールで使う

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

P_1^1(x) = √(1 − x²) など。m = 0 のとき、普通のルジャンドル多項式になります。

数値の精度は実装依存です。結果を比べるときは、`==` ではなく、許容誤差を使います。引数が定義域を外れた場合は、NaN を返し、`errno` に `EDOM` が設定されることがあります。

使う分野は、球面調和関数の計算です。ゲームでは、このような関数が必要になる計算は、通常、既存のライブラリ（物理エンジンや信号処理のライブラリ）の内部に隠れています。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("P_1^1(0.5) = {:.4f}", std::assoc_legendre(1, 1, 0.5));
}
```

```text title="実行結果"
P_1^1(0.5) = 0.8660
```

## ゲームでの使いどころ

ゲームのコードで使う場面はほとんどありません。用途は球面調和関数の計算です。必要になったら、ここで関数の名前と引数の並びを確かめてください。

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
    - [x] `std::assoc_legendre` は陪ルジャンドル関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::assoc_legendre](https://cpprefjp.github.io/reference/cmath/assoc_legendre.html)
- [cppreference: std::assoc_legendre](https://en.cppreference.com/w/cpp/numeric/math/assoc_legendre)

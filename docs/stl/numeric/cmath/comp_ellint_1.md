---
title: std::comp_ellint_1
summary: "第 1 種完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::comp_ellint_1

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

`std::comp_ellint_1` は、数学の特殊関数の 1 つ、第 1 種完全楕円積分を計算します。物理や信号処理、統計の計算に使われる関数で、ゲームのコードで直接使う機会は、ほとんどありません。C++17 で標準に加わったものの 1 つとして、存在と使い方を知っておけば足ります。

!!! tip "ポイント"
    - `std::comp_ellint_1(0.0)` は π/2 ≈ 1.5708
    - `|k|` は 1 以下
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - ゲームでの出番はほぼない。物理シミュレーションや信号処理のツールで使う

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::comp_ellint_1 {#comp_ellint_1}

<span class="ver ver-17">C++17</span>

```cpp
double comp_ellint_1(double k);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | `double` | 離心率（|k| ≤ 1） |

第 1 種完全楕円積分 K(k) の値を返します。振り子の周期（大きな振幅）などの計算に現れます。

K(0) = π/2 ≈ 1.5708。

数値の精度は実装依存です。結果を比べるときは、`==` ではなく、許容誤差を使います。引数が定義域を外れた場合は、NaN を返し、`errno` に `EDOM` が設定されることがあります。

使う分野は、振り子の周期、楕円の周長です。ゲームでは、このような関数が必要になる計算は、通常、既存のライブラリ（物理エンジンや信号処理のライブラリ）の内部に隠れています。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("K(0) = {:.4f}", std::comp_ellint_1(0.0));
}
```

```text title="実行結果"
1.5708
```

## ゲームでの使いどころ

ゲームのコードで使う場面はほとんどありません。用途は振り子の周期、楕円の周長です。必要になったら、ここで関数の名前と引数の並びを確かめてください。

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
    - [x] `std::comp_ellint_1` は第 1 種完全楕円積分
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::comp_ellint_1](https://cpprefjp.github.io/reference/cmath/comp_ellint_1.html)
- [cppreference: std::comp_ellint_1](https://en.cppreference.com/w/cpp/numeric/math/comp_ellint_1)

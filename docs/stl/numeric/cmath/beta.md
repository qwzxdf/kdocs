---
title: std::beta
summary: "ベータ関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::beta

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

「成功の確率が 0 から 1 のどのあたりに偏りやすいか」を、山の形で表す分布に、ベータ分布があります。その山の面積を 1 にそろえる係数が、ベータ関数 `B(x, y)` で、`std::beta` が返します。

!!! tip "ポイント"
    - `std::beta(2.0, 3.0)` は 1/12 ≈ 0.0833
    - `x` と `y` は正の値
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - ベータ分布の正規化に出てくる。`B(x, y) = Γ(x)Γ(y)/Γ(x+y)`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::beta {#beta}

<span class="ver ver-17">C++17</span>

```cpp
double beta(double x, double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | `double` | 1 つ目の値（正） |
| `y` | `double` | 2 つ目の値（正） |

ベータ関数 B(x, y) = Γ(x)Γ(y) / Γ(x + y) の値を返します。確率分布（ベータ分布）の正規化に使われます。

`x` と `y` は正の値です。`B(x, y) = Γ(x) Γ(y) / Γ(x + y)` で、ガンマ関数（`std::tgamma`）から計算できます。大きな引数では、`tgamma` の値が桁あふれするので、自分で `tgamma` を掛け割りするより、`std::beta` を使うほうが無難です。

ベータ分布（`x^(a−1) (1−x)^(b−1) / B(a, b)`）の正規化定数として、一番よく登場します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  // ガンマ関数との関係
  double a = 2.0;
  double b = 5.0;
  std::println("B(2, 5) = {:.6f}", std::beta(a, b));
  std::println("Γ(2)Γ(5)/Γ(7) = {:.6f}", std::tgamma(a) * std::tgamma(b) / std::tgamma(a + b));

  // ベータ分布の確率密度 (a = 2, b = 5) の x = 0.5 での値
  double x = 0.5;
  double pdf = std::pow(x, a - 1) * std::pow(1 - x, b - 1) / std::beta(a, b);
  std::println("ベータ分布の密度 f(0.5) = {:.4f}", pdf);
}
```

```text title="実行結果"
B(2, 5) = 0.033333
Γ(2)Γ(5)/Γ(7) = 0.033333
ベータ分布の密度 f(0.5) = 0.9375
```

`B(2, 5) = 1!·4!/6! = 1/30` です。ベータ分布の密度は、`0.5 × 0.0625 × 30 = 0.9375` と計算できます。

## ゲームでの使いどころ

ガチャの排出率や、パラメーターの揺らぎを、`[0, 1]` の値で、山の形を変えながら作りたいときの分布（ベータ分布）で使います。`a` と `b` を変えると、左寄りや右寄りの山になります。乱数の標準ライブラリ（`<random>`）には、ベータ分布がないので、密度の計算や、棄却法の自作で `std::beta` が使えます。

## よくあるミス

??? failure "x や y に 0 以下の値を渡す"
    定義域の外で、結果は定まりません。

??? failure "大きな引数を tgamma で計算する"
    `std::tgamma(200)` は桁あふれします。`std::beta` なら、内部でそれを避けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tgamma`](tgamma.md) | ガンマ関数そのもの |
| [`lgamma`](lgamma.md) | ガンマ関数の対数 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::beta` はベータ関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::beta](https://cpprefjp.github.io/reference/cmath/beta.html)
- [cppreference: std::beta](https://en.cppreference.com/w/cpp/numeric/math/beta)

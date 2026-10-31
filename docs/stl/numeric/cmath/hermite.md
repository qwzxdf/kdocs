---
title: std::hermite
summary: "エルミート多項式を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::hermite

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

ひもの定常波のように、ガウス関数と掛け合わせて波の形を作る多項式があります。それがエルミート多項式で、`std::hermite` が次数 `n` の値を返します。

!!! tip "ポイント"
    - `std::hermite(3, 2.0)` は 40（8 × 8 − 12 × 2）
    - 次数が大きいと値が急激に増える
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 物理学者の定義。確率論の Hermite 多項式とは係数が違う

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::hermite {#hermite}

<span class="ver ver-17">C++17</span>

```cpp
double hermite(unsigned int n, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `unsigned int` | 次数 |
| `x` | `double` | 評価する位置 |

エルミート多項式 H_n(x)（物理学者の定義）の値を返します。量子力学の調和振動子の波動関数に現れる多項式です。

次数 `n` は 0 以上の整数です。`std::hermite` は、物理学者のエルミート多項式 `H_n(x)` を返します。`H_0 = 1`、`H_1 = 2x`、`H_2 = 4x² − 2`、`H_3 = 8x³ − 12x` と続きます。確率論で使う、別の定義の多項式（`He_n`）とは、係数が違います。

漸化式は `H_{n+1}(x) = 2x H_n(x) − 2n H_{n−1}(x)` です。

`x` の範囲に制限はありません。ただし、`n` が大きく `x` も大きいと、値が桁あふれすることがあります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double x = 1.0;
  for (unsigned int n = 0; n <= 4; ++n) {
    std::println("H_{}(1.0) = {}", n, std::hermite(n, x));
  }

  // 漸化式 H_{n+1} = 2x H_n - 2n H_{n-1} で H_4 を求める
  double h0 = 1.0;
  double h1 = 2 * x;
  double h2 = 2 * x * h1 - 2 * 1 * h0;
  double h3 = 2 * x * h2 - 2 * 2 * h1;
  double h4 = 2 * x * h3 - 2 * 3 * h2;
  std::println("漸化式の H_4 = {}", h4);
}
```

```text title="実行結果"
H_0(1.0) = 1
H_1(1.0) = 2
H_2(1.0) = 2
H_3(1.0) = -4
H_4(1.0) = -20
漸化式の H_4 = -20
```

`H_4(1) = 16 − 48 + 12 = −20` です。標準ライブラリの値と、漸化式の値が一致します。

## ゲームでの使いどころ

量子力学の調和振動子の波動関数に出てくる多項式です。ガウス関数と掛けて、`H_n(x) e^(−x²/2)` の形にすると、ひもや弾性体の定常波のような形になります。ゲームの計算で使う場面は限られ、ガウス分布の展開を扱う、一部の信号処理に出てくる程度です。

## よくあるミス

??? failure "確率論の定義と取り違える"
    `std::hermite` は物理学者の定義です。確率論の `He_n` は、`H_n(x / √2) / 2^(n/2)` の関係で、係数が違います。

??? failure "大きな n と x で桁あふれ"
    値が急激に大きくなります。`double` の範囲を超えると無限大になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`laguerre`](laguerre.md) | 別の直交多項式 |
| [`legendre`](legendre.md) | 別の直交多項式（球対称な問題） |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::hermite` はエルミート多項式
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::hermite](https://cpprefjp.github.io/reference/cmath/hermite.html)
- [cppreference: std::hermite](https://en.cppreference.com/w/cpp/numeric/math/hermite)

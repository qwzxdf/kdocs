---
title: std::laguerre
summary: "ラゲール多項式を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::laguerre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

指数関数的に減る関数と組み合わせて、原子の電子の広がりを表すときに使う多項式があります。ラゲール多項式で、`std::laguerre` が次数 `n` の値を返します。

!!! tip "ポイント"
    - `std::laguerre(2, 1.0)` は −0.5
    - `x` は 0 以上を想定する
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 水素原子の波動関数に出る。ゲームで使う場面は稀

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::laguerre {#laguerre}

<span class="ver ver-17">C++17</span>

```cpp
double laguerre(unsigned int n, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `unsigned int` | 次数 |
| `x` | `double` | 評価する位置（0 以上） |

ラゲール多項式 L_n(x) の値を返します。水素原子の波動関数などに現れる多項式です。x は 0 以上を想定します。

次数 `n` は 0 以上の整数で、`x` は 0 以上です。`L_0 = 1`、`L_1 = 1 − x`、`L_2 = (x² − 4x + 2) / 2`、`L_3 = (−x³ + 9x² − 18x + 6) / 6` と続きます。`L_n(0)` は、すべての `n` で 1 です。

漸化式は `(n + 1) L_{n+1}(x) = (2n + 1 − x) L_n(x) − n L_{n−1}(x)` です。

`x` が負の値のとき、結果は規格では定まらず、NaN などが返ります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double x = 1.0;
  for (unsigned int n = 0; n <= 3; ++n) {
    std::println("L_{}(1.0) = {:.4f}", n, std::laguerre(n, x));
  }

  // x = 0 では、どの次数も 1
  std::println("L_3(0) = {}", std::laguerre(3, 0.0));

  // 漸化式で L_3 を求める: (n+1) L_{n+1} = (2n+1-x) L_n - n L_{n-1}
  double l0 = 1.0;
  double l1 = 1.0 - x;
  double l2 = ((2 * 1 + 1 - x) * l1 - 1 * l0) / 2;
  double l3 = ((2 * 2 + 1 - x) * l2 - 2 * l1) / 3;
  std::println("漸化式の L_3 = {:.4f}", l3);
}
```

```text title="実行結果"
L_0(1.0) = 1.0000
L_1(1.0) = 0.0000
L_2(1.0) = -0.5000
L_3(1.0) = -0.6667
L_3(0) = 1
漸化式の L_3 = -0.6667
```

`L_3(1) = (−1 + 9 − 18 + 6) / 6 = −2/3` です。標準ライブラリと漸化式で、同じ値が出ます。

## ゲームでの使いどころ

水素原子の波動関数など、量子力学の動径方向の部分に出てくる多項式です。ゲームで使う場面は、ほとんどありません。名前を知っておけば足ります。

## よくあるミス

??? failure "x に負の値を渡す"
    `x` は 0 以上を前提にしています。負の値の結果は、規格では定まりません。

??? failure "陪ラゲールと取り違える"
    次数 `m` を持つ版は `assoc_laguerre` です。`m = 0` なら、この関数と同じです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`assoc_laguerre`](assoc_laguerre.md) | 次数 `m` を加えた陪ラゲール多項式 |
| [`hermite`](hermite.md) | 別の直交多項式 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::laguerre` はラゲール多項式
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::laguerre](https://cpprefjp.github.io/reference/cmath/laguerre.html)
- [cppreference: std::laguerre](https://en.cppreference.com/w/cpp/numeric/math/laguerre)

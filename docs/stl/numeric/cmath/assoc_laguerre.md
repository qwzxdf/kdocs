---
title: std::assoc_laguerre
summary: "ラゲール陪多項式を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::assoc_laguerre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

ラゲール多項式に、もう 1 つの次数 `m` を加えたものが陪ラゲール多項式で、水素原子の電子の広がりの表現に使われます。`std::assoc_laguerre` が値を返します。

!!! tip "ポイント"
    - `std::assoc_laguerre(1, 1, 1.0)` は 1（−1 + 2）
    - `x` は 0 以上を想定する
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - `m = 0` なら普通のラゲール多項式と同じ

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::assoc_laguerre {#assoc_laguerre}

<span class="ver ver-17">C++17</span>

```cpp
double assoc_laguerre(unsigned int n, unsigned int m, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `unsigned int` | 次数 |
| `m` | `unsigned int` | 補助の次数 |
| `x` | `double` | 評価する位置（0 以上） |

陪ラゲール多項式 L_n^m(x) の値を返します。水素原子の動径方向の波動関数に現れます。

次数 `n` と `m` は 0 以上の整数、`x` は 0 以上です。`m = 0` のときは、普通のラゲール多項式 `L_n(x)` と同じです。`L_0^m = 1`、`L_1^m(x) = −x + m + 1`、`L_2^m(x) = (x² − 2(m + 2)x + (m + 1)(m + 2)) / 2` と続きます。

`x` が負の値のとき、結果は規格では定まりません。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double x = 1.5;
  // L_1^m(x) = -x + m + 1
  for (unsigned int m = 0; m <= 2; ++m) {
    std::println("L_1^{}(1.5) = {:.4f} (式: {:.4f})", m, std::assoc_laguerre(1, m, x), -x + m + 1);
  }

  // m = 0 は、普通のラゲール多項式と同じ
  std::println("L_2^0(1.5) = {:.4f}, L_2(1.5) = {:.4f}", std::assoc_laguerre(2, 0, x), std::laguerre(2, x));
}
```

```text title="実行結果"
L_1^0(1.5) = -0.5000 (式: -0.5000)
L_1^1(1.5) = 0.5000 (式: 0.5000)
L_1^2(1.5) = 1.5000 (式: 1.5000)
L_2^0(1.5) = -0.8750, L_2(1.5) = -0.8750
```

`m` が 1 増えるごとに、`L_1^m` が 1 ずつ増えます。`m = 0` では、普通のラゲール多項式と一致します。

## ゲームでの使いどころ

水素原子の動径方向の波動関数に出てくる関数です。ゲームの計算で直接使うことはほとんどありません。

## よくあるミス

??? failure "n と m を逆に渡す"
    第 1 引数が `n`（次数）、第 2 引数が `m` です。逆にすると別の関数になります。

??? failure "x に負の値を渡す"
    `x` は 0 以上です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`laguerre`](laguerre.md) | `m = 0` の場合 |
| [`hermite`](hermite.md) | 別の直交多項式 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::assoc_laguerre` は陪ラゲール多項式
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::assoc_laguerre](https://cpprefjp.github.io/reference/cmath/assoc_laguerre.html)
- [cppreference: std::assoc_laguerre](https://en.cppreference.com/w/cpp/numeric/math/assoc_laguerre)

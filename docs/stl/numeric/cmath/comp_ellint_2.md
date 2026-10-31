---
title: std::comp_ellint_2
summary: "第 2 種完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::comp_ellint_2

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

楕円の周の長さは、円のような簡単な式では求まりません。その正確な値を与えるのが第 2 種完全楕円積分 `E(k)` で、`std::comp_ellint_2` が返します。

!!! tip "ポイント"
    - `std::comp_ellint_2(0.0)` は π/2 ≈ 1.5708
    - `|k|` は 1 以下
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 楕円の周の長さ `4a·E(e)` に使える

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::comp_ellint_2 {#comp_ellint_2}

<span class="ver ver-17">C++17</span>

```cpp
double comp_ellint_2(double k);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | `double` | 離心率（|k| ≤ 1） |

第 2 種完全楕円積分 E(k) の値を返します。楕円の周の長さの計算に現れます。

`k` は −1 から 1 の範囲の離心率です。`E(k) = ∫_0^{π/2} √(1 − k² sin²θ) dθ` で、`E(0) = π/2`、`E(1) = 1` です。

長半径 `a`、短半径 `b` の楕円の周の長さは、`4a · E(e)`（`e = √(1 − b²/a²)` が離心率）で求まります。円（`e = 0`）では `4a · π/2 = 2πa` になります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;
  double a = 5.0;   // 長半径
  double b = 3.0;   // 短半径

  // 楕円の周の長さ = 4a E(e)
  double e = std::sqrt(1 - (b * b) / (a * a));
  double perimeter = 4 * a * std::comp_ellint_2(e);
  std::println("離心率 e = {:.3f}", e);
  std::println("周の長さ: {:.4f}", perimeter);

  // ラマヌジャンの近似式と比べる
  double approx = kPi * (3 * (a + b) - std::sqrt((3 * a + b) * (a + 3 * b)));
  std::println("ラマヌジャンの近似: {:.4f}", approx);
}
```

```text title="実行結果"
離心率 e = 0.800
周の長さ: 25.5270
ラマヌジャンの近似: 25.5270
```

長半径 5、短半径 3 の楕円の周は約 25.53 です。ラマヌジャンの近似式でも、小数第 4 位まで近い値が出ます。

## ゲームでの使いどころ

楕円軌道を動くオブジェクト（衛星や、周回する敵）の、軌道 1 周の長さを知りたいときに使えます。一定の速さで動かすなら、周の長さから、1 周にかかる時間を決められます。

## よくあるミス

??? failure "k に離心率ではなく、短半径と長半径の比を渡す"
    `k` は離心率 `√(1 − b²/a²)` です。`b/a` ではありません。

??? failure "周の長さに π をかけて求められると思う"
    円と違い、楕円の周は、単純な式では求まりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`comp_ellint_1`](comp_ellint_1.md) | 第 1 種。振り子の周期 |
| [`ellint_2`](ellint_2.md) | 弧の一部の長さ（不完全積分） |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::comp_ellint_2` は第 2 種完全楕円積分
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::comp_ellint_2](https://cpprefjp.github.io/reference/cmath/comp_ellint_2.html)
- [cppreference: std::comp_ellint_2](https://en.cppreference.com/w/cpp/numeric/math/comp_ellint_2)

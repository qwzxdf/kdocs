---
title: std::ellint_2
summary: "第 2 種不完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::ellint_2

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

楕円の弧の、端から途中までの長さを知りたいとき、完全積分では 1/4 周までしか求まりません。途中の角度 `φ` までの長さを求めるのが、第 2 種の不完全楕円積分 `std::ellint_2` です。

!!! tip "ポイント"
    - `std::ellint_2(0.0, 1.0)` は 1（k = 0 なら φ そのもの）
    - `phi` はラジアン
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 楕円の弧の一部の長さに使える。`a·E(e, t)`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ellint_2 {#ellint_2}

<span class="ver ver-17">C++17</span>

```cpp
double ellint_2(double k, double phi);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | `double` | 離心率（|k| ≤ 1） |
| `phi` | `double` | 振幅（ラジアン） |

第 2 種不完全楕円積分 E(k, φ) の値を返します。楕円弧の長さの計算に現れます。

`k` は離心率（絶対値 1 以下）、`phi` は振幅（ラジアン）です。`E(k, φ) = ∫_0^φ √(1 − k² sin²θ) dθ` で、`E(0, φ) = φ` です。`φ = π/2` のとき、完全楕円積分 `E(k)` と一致します。

楕円の弧の長さのうち、長軸の端から途中の点までの長さを表すのに使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;
  double a = 5.0;
  double b = 3.0;
  double e = std::sqrt(1 - (b * b) / (a * a));

  // 1/4 周の長さ = a E(e, π/2)。完全楕円積分と同じ
  std::println("1/4 周: {:.4f}", a * std::ellint_2(e, kPi / 2));
  std::println("周/4:   {:.4f}", a * std::comp_ellint_2(e));

  // 媒介変数 t の弧の長さ(長軸の端から)
  for (double t : {0.5, 1.0, 1.5}) {
    std::println("t = {}: 弧の長さ {:.4f}", t, a * std::ellint_2(e, t));
  }
}
```

```text title="実行結果"
1/4 周: 6.3817
周/4:   6.3817
t = 0.5: 弧の長さ 2.4351
t = 1: 弧の長さ 4.5249
t = 1.5: 弧の長さ 6.1690
```

`φ = π/2` では、1/4 周の長さになり、完全積分から求めた値と一致します。

## ゲームでの使いどころ

楕円軌道の途中までの距離を、パラメーターから求めたいときに使えます。軌道を一定の速さで動かすとき、距離から角度を逆算する前段階の計算になります。

## よくあるミス

??? failure "phi を楕円の中心角と取り違える"
    `phi` は媒介変数 `t`（`x = a cos t`、`y = b sin t` の `t`）で、中心から見た角度ではありません。

??? failure "度のまま渡す"
    ラジアンで渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`comp_ellint_2`](comp_ellint_2.md) | `φ = π/2` の完全積分 |
| [`ellint_1`](ellint_1.md) | 第 1 種 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ellint_2` は第 2 種不完全楕円積分
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::ellint_2](https://cpprefjp.github.io/reference/cmath/ellint_2.html)
- [cppreference: std::ellint_2](https://en.cppreference.com/w/cpp/numeric/math/ellint_2)

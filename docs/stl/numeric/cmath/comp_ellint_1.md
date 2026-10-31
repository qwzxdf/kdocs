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

振り子は、小さく揺らすと周期が一定ですが、大きく揺らすと周期が長くなります。その正確な周期を求める式に出てくるのが、第 1 種完全楕円積分 `K(k)` で、`std::comp_ellint_1` が返します。

!!! tip "ポイント"
    - `std::comp_ellint_1(0.0)` は π/2 ≈ 1.5708
    - `|k|` は 1 以下
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - 振り子の周期（大きな振れ幅）に使える

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

`k` は −1 から 1 の範囲の、楕円の離心率（母数）です。`K(k) = ∫_0^{π/2} dθ / √(1 − k² sin²θ)` で、`K(0) = π/2` です。`k` が 1 に近づくと、無限大に発散します。

振り子の振れ幅が大きいとき、周期が長くなる効果は、`K(sin(θ0 / 2))` で表されます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;
  double length = 1.0;   // 振り子の長さ (m)
  double g = 9.8;

  // 振れ幅が小さいときの周期: T0 = 2π sqrt(L / g)
  double t0 = 2 * kPi * std::sqrt(length / g);
  std::println("小さい振れ幅の周期: {:.4f} 秒", t0);

  // 振れ幅 θ0 が大きいと、T = 4 sqrt(L / g) K(sin(θ0 / 2))
  for (double deg : {10.0, 45.0, 90.0, 150.0}) {
    double theta0 = deg * kPi / 180.0;
    double period = 4 * std::sqrt(length / g) * std::comp_ellint_1(std::sin(theta0 / 2));
    std::println("振れ幅 {:>5} 度: 周期 {:.4f} 秒", deg, period);
  }
}
```

```text title="実行結果"
小さい振れ幅の周期: 2.0071 秒
振れ幅    10 度: 周期 2.0109 秒
振れ幅    45 度: 周期 2.0873 秒
振れ幅    90 度: 周期 2.3690 秒
振れ幅   150 度: 周期 3.5369 秒
```

振れ幅が 10 度なら周期は小さい振れ幅の値とほぼ同じですが、90 度で約 18% 長くなり、150 度では約 1.8 倍まで伸びます。

## ゲームでの使いどころ

ブランコや振り子の仕掛けを、現実の物理に近い周期で動かしたいときに使えます。振れ幅が大きいゲームの振り子は、小さな振れ幅の式（`2π√(L/g)`）より、ゆっくり動くのが本物です。

## よくあるミス

??? failure "k に 1 を渡す"
    無限大になります。`k` は絶対値が 1 未満です。

??? failure "角度をそのまま渡す"
    `k` は `sin(θ0 / 2)` のような値で、角度そのものではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ellint_1`](ellint_1.md) | 積分範囲を φ までにした版 |
| [`comp_ellint_2`](comp_ellint_2.md) | 第 2 種。楕円の周の長さ |

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

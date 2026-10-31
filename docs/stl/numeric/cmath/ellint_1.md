---
title: std::ellint_1
summary: "第 1 種不完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::ellint_1

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

振り子が最下点から途中の角度まで動くのにかかる時間のように、楕円積分の積分範囲を途中の角度 `φ` までにしたものが、不完全楕円積分です。`std::ellint_1` は、第 1 種の `F(k, φ)` を返します。

!!! tip "ポイント"
    - `std::ellint_1(0.0, 1.0)` は 1（k = 0 なら φ そのもの）
    - `phi` はラジアン
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - `φ = π/2` なら完全楕円積分 `K(k)` と同じ

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ellint_1 {#ellint_1}

<span class="ver ver-17">C++17</span>

```cpp
double ellint_1(double k, double phi);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | `double` | 離心率（|k| ≤ 1） |
| `phi` | `double` | 振幅（ラジアン） |

第 1 種不完全楕円積分 F(k, φ) の値を返します。完全楕円積分の積分範囲を φ までにしたものです。

`k` は離心率（絶対値 1 以下）、`phi` は振幅（ラジアン）です。`F(k, φ) = ∫_0^φ dθ / √(1 − k² sin²θ)` で、`F(0, φ) = φ` です。`φ = π/2` のとき、完全楕円積分 `K(k)` と一致します。

振り子が最下点から、ある角度まで上がるのにかかる時間の計算に出てきます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;
  double k = 0.5;

  // φ = π/2 のとき、完全楕円積分 K(k) と一致
  std::println("F(0.5, π/2) = {:.4f}", std::ellint_1(k, kPi / 2));
  std::println("K(0.5)       = {:.4f}", std::comp_ellint_1(k));

  // k = 0 のとき F(0, φ) = φ
  std::println("F(0, 1.0) = {}", std::ellint_1(0.0, 1.0));

  // φ が増えるほど F も増える
  for (double phi : {0.5, 1.0, 1.5}) {
    std::println("F(0.5, {}) = {:.4f}", phi, std::ellint_1(k, phi));
  }
}
```

```text title="実行結果"
F(0.5, π/2) = 1.6858
K(0.5)       = 1.6858
F(0, 1.0) = 1
F(0.5, 0.5) = 0.5051
F(0.5, 1) = 1.0374
F(0.5, 1.5) = 1.6040
```

`φ = π/2` の値が完全積分と一致し、`k = 0` では `φ` そのものになります。

## ゲームでの使いどころ

振り子が、最下点から途中の角度まで動く時間を、正確に求めたいときに使えます。ゲームの振り子の動きを、時刻から位置を決めるアニメーションとして書くとき、役に立ちます。

## よくあるミス

??? failure "phi を度のまま渡す"
    `phi` はラジアンです。

??? failure "k と phi の順を逆にする"
    第 1 引数が `k`、第 2 引数が `phi` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`comp_ellint_1`](comp_ellint_1.md) | `φ = π/2` の完全積分 |
| [`ellint_2`](ellint_2.md) | 第 2 種 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ellint_1` は第 1 種不完全楕円積分
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::ellint_1](https://cpprefjp.github.io/reference/cmath/ellint_1.html)
- [cppreference: std::ellint_1](https://en.cppreference.com/w/cpp/numeric/math/ellint_1)

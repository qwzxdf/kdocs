---
title: std::riemann_zeta
summary: "リーマンのゼータ関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::riemann_zeta

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

1 位がよく選ばれ、順位が下がるほど選ばれにくくなる、ジップの法則のような偏りの確率を作るとき、全体の合計を 1 にそろえる係数が必要になります。それがゼータ関数 `ζ(s)` で、`std::riemann_zeta` が返します。

!!! tip "ポイント"
    - `std::riemann_zeta(2.0)` は π² / 6 ≈ 1.6449
    - `x` が 1 のとき発散する
    - C++17 で `<cmath>` に追加された特殊関数の 1 つ
    - ジップの法則で、確率を正規化する係数に使える

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::riemann_zeta {#riemann_zeta}

<span class="ver ver-17">C++17</span>

```cpp
double riemann_zeta(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | `double` | 評価する位置（1 以外） |

リーマンのゼータ関数 ζ(s) の値を返します。数論や、統計力学に現れる関数です。

`std::riemann_zeta(s)` は、`ζ(s) = 1 + 1/2^s + 1/3^s + …` の値を返します。`s > 1` で収束し、`ζ(2) = π²/6`（バーゼル問題）、`ζ(4) = π⁴/90` など、π の累乗と結びつく値が有名です。`s` が 1 に近づくと発散し、`s = 1` では無限大になります。

`s < 1` の場合も、解析接続した値を返します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  constexpr double kPi = std::numbers::pi;
  std::println("ζ(2) = {:.6f}, π²/6 = {:.6f}", std::riemann_zeta(2.0), kPi * kPi / 6);
  std::println("ζ(4) = {:.6f}, π⁴/90 = {:.6f}", std::riemann_zeta(4.0), std::pow(kPi, 4) / 90);

  // ジップの法則: k 位のものが選ばれる確率 = (1 / k^s) / ζ(s)
  double s = 2.0;
  for (int k = 1; k <= 3; ++k) {
    std::println("{} 位の確率: {:.4f}", k, std::pow(k, -s) / std::riemann_zeta(s));
  }
}
```

```text title="実行結果"
ζ(2) = 1.644934, π²/6 = 1.644934
ζ(4) = 1.082323, π⁴/90 = 1.082323
1 位の確率: 0.6079
2 位の確率: 0.1520
3 位の確率: 0.0675
```

`ζ(2)` と `π²/6` が一致します。ジップの法則では、1 位が約 61%、2 位が約 15%、3 位が約 7% と、順位とともに急に下がります。

## ゲームでの使いどころ

アイテムや単語の出現頻度が「順位に反比例する」というジップの法則では、確率の合計を 1 にするための係数が `1 / ζ(s)` です。ドロップテーブルや、人気ランキングのような、偏りのある抽選を自作するときに使えます。

## よくあるミス

??? failure "s = 1 を渡す"
    無限大に発散します。調和級数が収束しないのと同じです。

??? failure "級数を足し合わせて求めようとする"
    `s` が 1 に近いと、収束がとても遅くなります。`std::riemann_zeta` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`beta`](beta.md) | 確率分布で出てくる別の特殊関数 |
| [`tgamma`](tgamma.md) | ガンマ関数 |

## コンパイラ対応

C++17 から使えます。`<cmath>` で宣言されます。GCC、Clang（libstdc++）、Visual Studio で使えます。libc++（Clang の標準ライブラリ）は一部の特殊関数が未対応の場合があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::riemann_zeta` はリーマンのゼータ関数
    - [x] 定義域を外れると NaN
    - [x] ゲームでの出番はほぼない

## 関連ページ

- [cpprefjp: std::riemann_zeta](https://cpprefjp.github.io/reference/cmath/riemann_zeta.html)
- [cppreference: std::riemann_zeta](https://en.cppreference.com/w/cpp/numeric/math/riemann_zeta)

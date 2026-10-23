---
title: std::erf
summary: "誤差関数（正規分布の積分に関係する関数）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::erf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

正規分布（ベル型の確率分布）のある範囲に入る確率は、分布の式を積分して求めます。この積分を解析的に書き表したものが、誤差関数 `erf` です。

ゲームでは、ガウスぼかしの重みの計算や、確率の見積もりで使うことがあります。

!!! tip "ポイント"
    - `std::erf(0.0)` は 0、`std::erf(1.0)` は約 0.8427
    - 値の範囲は −1 〜 +1。`x` が大きくなると 1 に近づく
    - 正規分布の累積確率の計算に使う
    - 補誤差関数 `erfc` は `1 - erf(x)` を正確に求める

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::erf {#erf}

<span class="ver ver-11">C++11</span>

```cpp
float erf(float x);
double erf(double x);
long double erf(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 入力 |

戻り値は、誤差関数 `(2 / √π) ∫₀ˣ exp(−t²) dt` の値です。奇関数で、`x` が正の無限大へ向かうと 1 に、負の無限大へ向かうと −1 に近づきます。

標準正規分布の累積分布関数 Φ(z)（z 以下の値が出る確率）は、`0.5 * (1 + erf(z / √2))` と書けます。ガウス分布に従う乱数が、ある範囲に入る確率を求めるときに使います。

`x` が大きいと `erf(x)` は 1 に極めて近くなり、`1 - erf(x)` が桁落ちします。その場合は `erfc` を使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("erf(0) = {}", std::erf(0.0));
  std::println("erf(1) = {}", std::erf(1.0));
  // 標準正規分布で、平均から ±1σ に入る確率 = erf(1/√2)
  const double within_1_sigma = std::erf(1.0 / std::sqrt(2.0));
  std::println("±1σ の確率 = {:.4f}", within_1_sigma);
}
```

```text title="実行結果"
erf(0) = 0
erf(1) = 0.8427007929497149
±1σ の確率 = 0.6827
```

## ゲームでの使いどころ

ガウスぼかしのカーネルを、ピクセルの区間ごとに正確に積分して作るときに使います（ピクセル幅で積分した重みは、`erf` の差で書けます）。ゲームでの出番は多くありません。

## よくあるミス

??? failure "`x` が大きいときに `1 - erf(x)` を使って、0 になる"
    `std::erfc(x)` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`erfc`](erfc.md) | 補誤差関数 `1 - erf(x)` |
| [`tgamma`](tgamma.md) | ガンマ関数 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `erf(x)` は誤差関数。範囲は −1 〜 1
    - [x] 正規分布の累積確率に使える
    - [x] `x` が大きいときの `1 - erf(x)` は `erfc`

## 関連ページ

- [`std::erfc`](erfc.md)
- [cpprefjp: std::erf](https://cpprefjp.github.io/reference/cmath/erf.html)
- [cppreference: std::erf](https://en.cppreference.com/w/cpp/numeric/math/erf)

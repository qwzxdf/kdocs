---
title: std::isinf
summary: "値が無限大かを調べる。"
order: 24
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isinf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

0 で割る、桁があふれる、といった計算の失敗は、浮動小数点数では例外にならず、無限大（inf）という値になって流れていきます。気づかないまま次の計算に使うと、画面の座標が飛んだり、物体が消えたりします。

`std::isinf` は、<strong>値が無限大かどうか</strong>を調べる関数です。

!!! tip "ポイント"
    - `std::isinf(x)` は、正の無限大でも負の無限大でも `true`
    - `x == INFINITY` と書くより意図が明確
    - NaN は無限大ではない（`isinf(NaN)` は `false`）
    - 有限かどうかを一度に調べるなら `isfinite`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isinf {#isinf}

<span class="ver ver-11">C++11</span>

```cpp
bool isinf(float x);
bool isinf(double x);
bool isinf(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 調べたい値 |

戻り値は、`x` が +∞ または −∞ なら `true`、それ以外（有限の値と NaN）は `false` です。

無限大は、`1.0 / 0.0` のような 0 での割り算、`exp(1000.0)` のようなオーバーフローで生まれます。無限大どうしの引き算（∞ − ∞）は NaN になるので、無限大が残っていることに気づかずに計算を続けると、あとで NaN が混ざり、原因がたどりにくくなります。

整数型の引数に対しては、`double` に変換されたうえで判定されるため、常に `false` です（整数には無限大がありません）。

`-ffast-math` のような最適化オプションを使うと、コンパイラが無限大や NaN が出ないと仮定してしまい、`isinf` が常に `false` になることがあります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double inf = std::numeric_limits<double>::infinity();
  const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("isinf(inf)   = {}", std::isinf(inf));
  std::println("isinf(-inf)  = {}", std::isinf(-inf));
  std::println("isinf(1e300) = {}", std::isinf(1e300));
  std::println("isinf(nan)   = {}", std::isinf(nan));
}
```

```text title="実行結果"
isinf(inf)   = true
isinf(-inf)  = true
isinf(1e300) = false
isinf(nan)   = false
```

## ゲームでの使いどころ

計算結果の検証に使います。物理や AI の途中で、0 割りやあふれが起きていないかを確認します。

```cpp
const float speed = distance / elapsed;      // elapsed が 0 だと無限大
if (std::isinf(speed)) {
  speed = max_speed;                          // 上限に置き換える
}
```

実際は、無限大も NaN もまとめて弾くなら、`std::isfinite` のほうが簡単です。

## よくあるミス

??? failure "NaN も無限大も同時に弾くつもりが、NaN を見逃す"
    `isinf` は NaN に `false` を返します。両方を弾くなら `!std::isfinite(x)` を使います。

??? failure "`-ffast-math` で、無限大の検出が働かない"
    この最適化は無限大と NaN を仮定から外すので、検出が必要なコードでは使いません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isfinite`](isfinite.md) | 有限の値か（無限大でも NaN でもない） |
| [`isnan`](isnan.md) | NaN か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `isinf(x)` は ±∞ のとき `true`
    - [x] NaN は無限大ではない。両方弾くなら `!isfinite`
    - [x] `-ffast-math` では検出できなくなる

## 関連ページ

- [`std::isfinite`](isfinite.md)
- [cpprefjp: std::isinf](https://cpprefjp.github.io/reference/cmath/isinf.html)
- [cppreference: std::isinf](https://en.cppreference.com/w/cpp/numeric/math/isinf)

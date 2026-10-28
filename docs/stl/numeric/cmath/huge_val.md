---
title: HUGE_VAL
summary: "double の無限大を表すマクロ。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# HUGE_VAL

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

計算結果が大きすぎて表せないとき、数学関数は `HUGE_VAL` という定数を返します。多くの環境では、これは無限大です。

!!! tip "ポイント"
    - `HUGE_VAL` は `double` の「とても大きな値」を表すマクロ
    - IEEE 754 の環境では、正の無限大に等しい
    - `HUGE_VALF`（`float`）と `HUGE_VALL`（`long double`）もある
    - オーバーフローしたときの戻り値として登場する

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### HUGE_VAL {#huge_val}

<span class="ver ver-11">C++11</span>

```cpp
#define HUGE_VAL /* double の定数式 */
#define HUGE_VALF /* float の定数式 */
#define HUGE_VALL /* long double の定数式 */
```

`HUGE_VAL` は、数学関数が結果を表現できなかったとき（オーバーフロー）に返す値です。浮動小数点が IEEE 754 に従う環境では、これは正の無限大です。

`std::exp(1000.0)` のようにあふれる計算は、`HUGE_VAL` を返し、`errno` に `ERANGE` を設定することがあります。無限大の値を直接書きたいなら、`std::numeric_limits<double>::infinity()` か `INFINITY` のほうが意図がはっきりします。

C の古いコードで、エラーの判定に `if (r == HUGE_VAL)` と書かれているのを見かけます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  std::println("HUGE_VAL は無限大: {}", HUGE_VAL == std::numeric_limits<double>::infinity());
  std::println("exp(1000) は HUGE_VAL: {}", std::exp(1000.0) == HUGE_VAL);
}
```

```text title="実行結果"
HUGE_VAL は無限大: true
exp(1000) は HUGE_VAL: true
```

## ゲームでの使いどころ

古い C のコードで、オーバーフローの検出に使われています。新しいコードでは `std::isinf` で調べます。

## よくあるミス

??? failure "`HUGE_VAL` を最大値だと思う"
    最大値は `numeric_limits<double>::max()` です。`HUGE_VAL` は無限大（に近い値）です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`infinity`](infinity.md) | `float` の無限大を表すマクロ |
| [`isinf`](isinf.md) | 無限大か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `HUGE_VAL` はオーバーフローの戻り値で、通常は無限大
    - [x] 最大値ではない
    - [x] 新しいコードでは `isinf`

## 関連ページ

- [cpprefjp: HUGE_VAL](https://cpprefjp.github.io/reference/cmath/huge_val.html)
- [cppreference: HUGE_VAL](https://en.cppreference.com/w/cpp/numeric/math/HUGE_VAL)

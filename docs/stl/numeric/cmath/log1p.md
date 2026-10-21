---
title: std::log1p
summary: "log(1 + x) を、x が 0 に近くても精度よく求める。"
order: 35
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::log1p

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::log1p(x)` は、**`log(1 + x)` を、x が 0 に近くても精度を落とさずに計算する**関数です。`log(1 + x)` は、`1 + x` で小さな x が丸められて精度が落ちます。

!!! tip "ポイント"
    - `log(1 + x)` の桁落ちを避ける。
    - `expm1` の逆。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::log1p {#log1p}

```cpp
double log1p(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 値（−1 より大きい） |

- 戻り値: `log(1 + x)`
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.3e}", std::log1p(1e-10));
}
```

```text title="実行結果"
1.000e-10
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 小さな増加率の対数 | `std::log1p(rate)` |

## よくあるミス

??? failure "x が −1 以下"
    NaN や −∞ です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log`](log.md) | 通常の自然対数 |
| [`expm1`](expm1.md) | 対応する指数 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `log(1 + x)` を精度よく
    - [x] x は −1 より大きい
    - [x] `expm1` と対

## 関連ページ

- [cpprefjp: std::log1p](https://cpprefjp.github.io/reference/cmath/log1p.html)
- [cppreference: std::log1p](https://en.cppreference.com/w/cpp/numeric/math/log1p)

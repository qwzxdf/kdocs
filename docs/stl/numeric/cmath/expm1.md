---
title: std::expm1
summary: "e^x − 1 を、x が 0 に近くても精度よく求める。"
order: 34
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::expm1

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::expm1(x)` は、**`e^x − 1` を、x が 0 に近くても精度を落とさずに計算する**関数です。`exp(x) - 1` は、x が小さいと桁落ちで精度が悪くなります。小さな変化量を扱う物理計算で使います。

!!! tip "ポイント"
    - `exp(x) - 1` の桁落ちを避ける。
    - 逆の対応は `log1p`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::expm1 {#expm1}

```cpp
double expm1(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 値（0 に近い） |

- 戻り値: `e^x − 1`
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.3e}", std::expm1(1e-10));
}
```

```text title="実行結果"
1.000e-10
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 小さな減衰率の計算 | `std::expm1(-k * dt)` |

## よくあるミス

??? failure "exp(x) - 1 で書く"
    x が小さいと、桁落ちで 0 になることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exp`](exp.md) | 通常の指数 |
| [`log1p`](log1p.md) | 対応する対数 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `e^x − 1` を精度よく
    - [x] x が 0 に近いときに有効
    - [x] `log1p` と対

## 関連ページ

- [cpprefjp: std::expm1](https://cpprefjp.github.io/reference/cmath/expm1.html)
- [cppreference: std::expm1](https://en.cppreference.com/w/cpp/numeric/math/expm1)

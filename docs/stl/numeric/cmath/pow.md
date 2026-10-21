---
title: std::pow
summary: "べき乗（x の y 乗）を求める。"
order: 14
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::pow

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <cmath>`
</div>

`std::pow(x, y)` は、**x の y 乗を求める**関数です。ガンマ補正、減衰カーブなどに使います。**2 乗や 3 乗は `x * x` と書くほうが速い**です。

!!! tip "ポイント"
    - 2 乗は `x * x`。`pow(x, 2)` より速い。
    - 負の底に小数の指数は NaN。
    - ガンマ補正（`pow(c, 2.2)`）や、イージングで使う。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::pow {#pow}

```cpp
float pow(float base, float exp);
```

- `base` の `exp` 乗。2 乗するだけなら `x * x` と書くほうが速くて正確です

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::pow(2.0, 10), std::pow(9.0, 0.5));
}
```

```text title="実行結果"
1024 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ガンマ補正 | `std::pow(color, 1.0f / 2.2f)` |
| イージング関数 | `std::pow(t, 3)` |

## よくあるミス

??? failure "2 乗に pow を使う"
    `x * x` のほうが速く、正確です。

??? failure "整数のべき乗に pow を使う"
    小数で計算するので、大きな整数で誤差が出ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sqrt`](sqrt.md) | 0.5 乗 |
| [`exp`](exp.md) | e の x 乗 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x の y 乗
    - [x] 2 乗は `x * x`
    - [x] 整数のべき乗には向かない

## 関連ページ

- [cpprefjp: std::pow](https://cpprefjp.github.io/reference/cmath/pow.html)
- [cppreference: std::pow](https://en.cppreference.com/w/cpp/numeric/math/pow)

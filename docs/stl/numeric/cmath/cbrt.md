---
title: std::cbrt
summary: "立方根（3 乗根）を求める。"
order: 21
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cbrt

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::cbrt` は、**立方根（3 乗して x になる値）を求める**関数です。負の数にも使えます（`pow(x, 1/3)` は負で NaN）。体積から一辺の長さを求めるときなどに使います。

!!! tip "ポイント"
    - 負の数にも使える。
    - `pow(x, 1.0 / 3)` より正確で速い。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cbrt {#cbrt}

```cpp
float cbrt(float x);
```

- 立方根。マイナスでも使えます

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::cbrt(27.0), std::cbrt(-8.0));
}
```

```text title="実行結果"
3 -2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 体積から一辺の長さを出す | `std::cbrt(volume)` |

## よくあるミス

??? failure "pow で代用して負の数が NaN"
    `std::cbrt` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sqrt`](sqrt.md) | 平方根 |
| [`pow`](pow.md) | 一般のべき乗 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 立方根
    - [x] 負の数にも使える
    - [x] `pow` より正確

## 関連ページ

- [cpprefjp: std::cbrt](https://cpprefjp.github.io/reference/cmath/cbrt.html)
- [cppreference: std::cbrt](https://en.cppreference.com/w/cpp/numeric/math/cbrt)

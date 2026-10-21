---
title: std::sqrt
summary: "平方根（ルート）を求める。"
order: 1
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sqrt

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

`std::sqrt` は、**平方根（√x）を求める**関数です。2 点間の距離、ベクトルの長さの計算で使います。`sqrt` は比較的重いので、**距離を比べるだけなら 2 乗のまま比べる**のが定石です。

!!! tip "ポイント"
    - 距離の比較は、`sqrt` せずに 2 乗で比べる（大小関係は同じ）。
    - 負の値を渡すと NaN になる。
    - ゲームでは `float` 版 `std::sqrt(float)` を使う。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sqrt {#sqrt}

```cpp
float sqrt(float x);
double sqrt(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 0 以上の値 |

- 戻り値: √x。**マイナスを渡すと NaN**

!!! note "実際は"
    「近いかどうか」を比べるだけなら、`dx * dx + dy * dy < range * range` のように 2 乗のまま比べると sqrt が要らず速くなります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::sqrt(16.0), std::isnan(std::sqrt(-1.0)));
}
```

```text title="実行結果"
4 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 点間の距離 | `std::sqrt(dx * dx + dy * dy)` |
| ベクトルの長さ（正規化の前） | `std::sqrt(x * x + y * y + z * z)` |

## よくあるミス

??? failure "距離の比較に毎回 sqrt を使う"
    2 乗のまま比べれば足ります。`d2 < r * r`。

??? failure "負の数を渡す"
    結果は NaN です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hypot`](hypot.md) | x² + y² の平方根を、桁あふれなしで |
| SimpleMath の `Vector3::Length` | ベクトルの長さ |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 平方根
    - [x] 比べるだけなら 2 乗のまま
    - [x] 負は NaN

## 関連ページ

- [cpprefjp: std::sqrt](https://cpprefjp.github.io/reference/cmath/sqrt.html)
- [cppreference: std::sqrt](https://en.cppreference.com/w/cpp/numeric/math/sqrt)

---
title: std::sin
summary: "サイン（正弦）を求める。引数はラジアン。"
order: 3
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sin

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

`std::sin` は、**サイン（正弦）を求める**関数です。**引数は度ではなくラジアン**です。回転、波の動き、アニメーションに使います。度からラジアンへは `度 × π / 180` です。

!!! tip "ポイント"
    - 引数は**ラジアン**。度の値は変換する。
    - `float` 版は `std::sinf` ではなく、`std::sin(float)`。
    - 周期的な動き（ゆらゆら）は、時間に `std::sin` をかける。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sin {#sin}

```cpp
float sin(float radians);
```

- サイン。引数は**ラジアン**（180 度 = π）。揺れ（上下にふわふわ）にも使えます

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  std::println("{:.1f} {:.1f}", std::sin(0.0), std::sin(std::numbers::pi / 2));
}
```

```text title="実行結果"
0.0 1.0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ゆらゆら揺れる動き | `y = amplitude * std::sin(time * speed)` |
| 円周上の位置 | `x = r * std::cos(a); y = r * std::sin(a);` |

## よくあるミス

??? failure "度をそのまま渡す"
    `std::sin(90)` は 90 ラジアンです。`std::numbers::pi_v<float> / 180` をかけてから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cos`](cos.md) | コサイン |
| [`tan`](tan.md) | タンジェント |
| [`<numbers>`](../numbers.md) | π の定数 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] サイン
    - [x] 引数はラジアン
    - [x] 度は変換する

## 関連ページ

- [cpprefjp: std::sin](https://cpprefjp.github.io/reference/cmath/sin.html)
- [cppreference: std::sin](https://en.cppreference.com/w/cpp/numeric/math/sin)

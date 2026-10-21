---
title: std::cos
summary: "コサイン（余弦）を求める。引数はラジアン。"
order: 4
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cos

<div class="page-badges" markdown>
<span class="rank rank-must">必須</span>
`#include <cmath>`
</div>

`std::cos` は、**コサイン（余弦）を求める**関数です。`sin` と組みにして、円周上の位置、向きのベクトルを作るときに使います。**引数はラジアン**です。

!!! tip "ポイント"
    - 角度 a の向きのベクトルは `(cos a, sin a)`。
    - 引数はラジアン。
    - `cos` は `sin` を 90 度ずらしたもの。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cos {#cos}

```cpp
float cos(float radians);
```

- コサイン。`{cos(a), sin(a)}` が角度 a の向きの長さ 1 のベクトルです

```cpp
#include <cmath>
#include <print>

int main() {
  // 時間でふわふわ上下する（振幅 4、0.5 秒ごと）
  for (float t : {0.0f, 0.125f, 0.25f}) {
    float offset = std::sin(t * 2.0f * 3.14159265f / 0.5f) * 4.0f;
    std::println("t={} → {:.1f}", t, offset);
  }
  std::println("{:.1f}", std::cos(0.0f));
}
```

```text title="実行結果"
t=0 → 0.0
t=0.125 → 4.0
t=0.25 → -0.0
1.0
```

`-0.0` は、sin(π) が計算誤差でほんの少しマイナス（-0.0000003 くらい）になったものです。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 向きのベクトルを作る | `Vector2(std::cos(a), std::sin(a))` |

## よくあるミス

??? failure "度をそのまま渡す"
    度の値は、ラジアンに変換してから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sin`](sin.md) | サイン |
| [`atan2`](atan2.md) | 向きから角度を求める |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コサイン
    - [x] 引数はラジアン
    - [x] `(cos a, sin a)` が向き

## 関連ページ

- [cpprefjp: std::cos](https://cpprefjp.github.io/reference/cmath/cos.html)
- [cppreference: std::cos](https://en.cppreference.com/w/cpp/numeric/math/cos)

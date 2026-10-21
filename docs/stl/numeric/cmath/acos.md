---
title: std::acos
summary: "アークコサイン（逆余弦）を求める。結果はラジアン。"
order: 7
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::acos

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::acos` は、**コサインの逆関数**です。−1〜1 の値から、角度（ラジアン、0〜π）を返します。**2 つのベクトルの内積から、なす角を求める**ときの定番です。

!!! tip "ポイント"
    - `acos(dot(a, b))` で、正規化した 2 ベクトルの角度。
    - 内積が誤差で 1.0000001 になると NaN。`std::clamp` で守る。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::acos {#acos}

```cpp
float acos(float x);
```

- コサインの逆。2 つの単位ベクトルの内積から、間の角度を出すのに使います（`acos(dot)`）。誤差で 1 を少し超えると NaN になるので、`std::clamp(dot, -1.0f, 1.0f)` してから渡します

```cpp
#include <algorithm>
#include <cmath>
#include <print>

int main() {
  float dot = 1.0000001f;  // 誤差で 1 を少し超えた内積
  std::println("{}", std::isnan(std::acos(dot)));
  std::println("{}", std::acos(std::clamp(dot, -1.0f, 1.0f)));
  std::println("{:.3f} {:.3f}", std::tan(0.5f), std::asin(1.0f));
}
```

```text title="実行結果"
true
0
0.546 1.571
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 敵が視野角に入っているか | `std::acos(dot(forward, to_target)) < fov / 2` |

## よくあるミス

??? failure "内積が範囲外になる"
    NaN になります。`std::clamp(d, -1.0f, 1.0f)`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`asin`](asin.md) | サインの逆 |
| [`atan2`](atan2.md) | 向きから角度 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] コサインの逆関数
    - [x] 内積からなす角を求める
    - [x] 誤差は clamp

## 関連ページ

- [cpprefjp: std::acos](https://cpprefjp.github.io/reference/cmath/acos.html)
- [cppreference: std::acos](https://en.cppreference.com/w/cpp/numeric/math/acos)

---
title: std::hypot
summary: "√(x² + y²) を、桁あふれしにくく求める。"
order: 15
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::hypot

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::hypot(x, y)` は、**√(x² + y²)（直角三角形の斜辺の長さ）を求める**関数です。x や y が大きいときに、2 乗で桁あふれしないように作られています。C++17 で 3 引数版（3D の長さ）もあります。

!!! tip "ポイント"
    - 2 引数は 2D の距離、3 引数は 3D の距離。
    - 速さは `sqrt(x * x + y * y)` のほうが上。
    - 桁あふれが心配な大きな値のときに使う。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::hypot {#hypot}

```cpp
float hypot(float x, float y);
float hypot(float x, float y, float z);  // C++17
```

- `sqrt(x*x + y*y)` と同じですが、とても大きい・小さい値でもあふれにくいです

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {} {}", std::pow(2.0f, 10.0f), std::hypot(3.0f, 4.0f),
               std::hypot(1.0f, 2.0f, 2.0f));
}
```

```text title="実行結果"
1024 5 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D・3D の距離 | `std::hypot(dx, dy, dz)` |

## よくあるミス

??? failure "毎フレーム大量に使って遅い"
    `sqrt(x*x + y*y)` のほうが速いです。値が小さく、桁あふれの心配がなければそちらを使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sqrt`](sqrt.md) | 平方根 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 斜辺の長さ
    - [x] 桁あふれしにくい
    - [x] 3 引数版は C++17

## 関連ページ

- [cpprefjp: std::hypot](https://cpprefjp.github.io/reference/cmath/hypot.html)
- [cppreference: std::hypot](https://en.cppreference.com/w/cpp/numeric/math/hypot)

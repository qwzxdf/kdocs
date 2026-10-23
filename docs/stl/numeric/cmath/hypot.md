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

2 つの点の距離は、x の差と y の差を 2 乗して足し、平方根を取れば求まります。`sqrt(dx * dx + dy * dy)` と書けば済みますが、値がとても大きい、あるいはとても小さいと、2 乗の途中で桁があふれたり、0 に潰れたりします。

`std::hypot` は、<strong>この計算を途中で壊れにくい形で行う</strong>関数です。2D の長さに加えて、C++17 からは 3D の長さも求められます。

!!! tip "ポイント"
    - `std::hypot(3.0, 4.0)` は 5。直角三角形の斜辺の長さ
    - 2 引数は 2D、3 引数（C++17）は 3D の長さ
    - 途中の 2 乗でオーバーフローしにくい。そのぶん `sqrt(x*x + y*y)` より遅いことが多い
    - ゲームの距離判定は、普段は距離の 2 乗どうしの比較で済ませる。`hypot` は実際の長さが必要なときだけ

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::hypot {#hypot}

```cpp
float hypot(float x, float y);
double hypot(double x, double y);
long double hypot(long double x, long double y);
double hypot(double x, double y, double z);  // C++17
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 1 つ目の成分 |
| `y` | 浮動小数点数 | 2 つ目の成分 |
| `z` | 浮動小数点数 | 3 つ目の成分（3 引数版） |

戻り値は √(x² + y²)（3 引数版は √(x² + y² + z²)）です。引数が整数なら `double` に変換されます。符号は関係なく、戻り値は常に 0 以上です。

通常の `sqrt(x * x + y * y)` は、`x` が `1e200` のとき `x * x` が無限大になり、結果が無限大になります。`hypot` は内部で最大の成分を使って割ってから計算するなど、途中で範囲を超えない工夫をしているので、正しい値を返します。

どちらかが無限大なら、もう一方が NaN でも結果は無限大です。それ以外で NaN が混ざれば NaN を返します。

落とし穴は速さです。`hypot` は安全のための処理が入るため、`sqrt` を直接呼ぶより遅くなります。1 フレームに数万回呼ぶような場所では、`sqrt(x*x + y*y)` か、そもそも平方根を避けた比較を使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("hypot(3, 4)    = {}", std::hypot(3.0, 4.0));       // 2D の長さ
  std::println("hypot(1, 2, 2) = {}", std::hypot(1.0, 2.0, 2.0));  // 3D の長さ
  std::println("hypot(-3, -4)  = {}", std::hypot(-3.0, -4.0));     // 符号は関係ない
}
```

```text title="実行結果"
hypot(3, 4)    = 5
hypot(1, 2, 2) = 3
hypot(-3, -4)  = 5
```

## ゲームでの使いどころ

2 つの位置の距離が実際の長さで要るとき（表示、速度の上限、移動量の計算）に使います。

```cpp
// プレイヤーと敵の距離（メートル）
const float distance = std::hypot(enemy.x - player.x, enemy.y - player.y);
```

当たり判定や「射程内か」の判定は、`hypot` を使わず、距離の 2 乗どうしで比べると平方根が要りません。

```cpp
const float dx = enemy.x - player.x;
const float dy = enemy.y - player.y;
const bool in_range = dx * dx + dy * dy <= range * range;  // 平方根なしで比べる
```

## よくあるミス

??? failure "毎フレーム大量に呼んで遅い"
    桁あふれの心配がない座標の範囲なら、`sqrt(x*x + y*y)` か、2 乗のまま比べます。

??? failure "3 引数版が使えない"
    3 引数版は C++17 からです。C++14 以前では 2 回に分けて `hypot(hypot(x, y), z)` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sqrt`](sqrt.md) | 平方根。2 乗の和を自分で計算する |
| [`pow`](pow.md) | 累乗。2 乗には `x * x` のほうが速い |

## コンパイラ対応

2 引数版は C++98、3 引数版は C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `hypot(x, y)` は √(x²+y²)、3 引数版（C++17）は 3D の長さ
    - [x] 途中でオーバーフローしにくいが、`sqrt` より遅い
    - [x] 距離の比較だけなら、2 乗どうしを比べて平方根を避ける

## 関連ページ

- [`std::sqrt`](sqrt.md)
- [cpprefjp: std::hypot](https://cpprefjp.github.io/reference/cmath/hypot.html)
- [cppreference: std::hypot](https://en.cppreference.com/w/cpp/numeric/math/hypot)

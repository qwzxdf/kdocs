---
title: std::nextafter
summary: "x の次に表せる浮動小数点数を返す（y の方向へ）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::nextafter

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

浮動小数点数は、とびとびの値しか表せません。「1.0 の次に大きい数」はいくつか。`std::nextafter` は、<strong>ある値から指定した方向に、表現できる次の値</strong>を返します。許容誤差の見積もりや、境界の少し外側の値が欲しいときに使います。

!!! tip "ポイント"
    - `std::nextafter(1.0, 2.0)` は 1.0 の次に大きい値
    - `nextafter(x, y)`: `x` から `y` の方向へ 1 つ進んだ値
    - `x == y` なら `y` を返す
    - `nexttoward` は、第 2 引数が `long double`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nextafter {#nextafter}

<span class="ver ver-11">C++11</span>

```cpp
float nextafter(float from, float to);
double nextafter(double from, double to);
long double nextafter(long double from, long double to);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `from` | 浮動小数点数 | 出発点 |
| `to` | 浮動小数点数 | 向かう方向（値そのものではなく、方向を表す） |

戻り値は、`from` から `to` の方向に向かって、その型で表せる隣の値です。`from < to` なら `from` より大きい最小の値、`from > to` なら小さい最大の値です。`from == to` のときは `to` を返します。

隣の値との差は、`from` の大きさに比例します（`double` で 1.0 付近では約 2.2e-16）。ゼロの隣は、最小の非正規化数です。

用途は、浮動小数点の精度の確認や、境界の少し外側の値を作ることです。たとえば、半開区間 [0, 1) の上限として、「1 より小さい最大の値」が必要なときに `nextafter(1.0, 0.0)` が使えます。乱数が 1.0 ちょうどを返さないことを保証したい場面です。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double next = std::nextafter(1.0, 2.0);
  std::println("1.0 より大きい: {}", next > 1.0);
  std::println("差は epsilon : {}", next - 1.0 == std::numeric_limits<double>::epsilon());
  std::println("1 未満の最大値は 1 未満: {}", std::nextafter(1.0, 0.0) < 1.0);
}
```

```text title="実行結果"
1.0 より大きい: true
差は epsilon : true
1 未満の最大値は 1 未満: true
```

## ゲームでの使いどころ

乱数や補間の結果が、上限ちょうどにならないようにするときに使います。

```cpp
// [0, 1) の範囲に収める（1.0 ちょうどを避ける）
const double upper = std::nextafter(1.0, 0.0);
value = std::min(value, upper);
```

## よくあるミス

??? failure "`to` を値として使うと誤解する"
    第 2 引数は方向を決めるだけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nexttoward`](nexttoward.md) | 第 2 引数が `long double` |
| [`numeric_limits`](../limits.md) | `epsilon` などの型の性質 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `nextafter(x, y)` は `x` の隣の表現可能な値（`y` 方向）
    - [x] 隣との差は値の大きさに比例する
    - [x] 半開区間の上限などに使う

## 関連ページ

- [cpprefjp: std::nextafter](https://cpprefjp.github.io/reference/cmath/nextafter.html)
- [cppreference: std::nextafter](https://en.cppreference.com/w/cpp/numeric/math/nextafter)

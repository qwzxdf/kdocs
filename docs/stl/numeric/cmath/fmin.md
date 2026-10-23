---
title: std::fmin
summary: "2 つの小数の小さいほうを返す（NaN は無視する）。"
order: 37
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fmin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::min` は 2 つの値の小さいほうを返しますが、片方が NaN だと、比較が成り立たず、結果が不安定になります。NaN が混ざりうる計算で、有効なほうの値を取りたいときに使うのが `std::fmin` です。

!!! tip "ポイント"
    - `std::fmin(1.0, 2.0)` は 1
    - 片方が NaN なら、もう一方を返す。両方 NaN なら NaN
    - `<cmath>` の関数で、浮動小数点数専用。`std::min` は `<algorithm>` にある
    - 通常のゲームの計算では `std::min` で足り、NaN を無視したいときだけ `fmin`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fmin {#fmin}

<span class="ver ver-11">C++11</span>

```cpp
float fmin(float x, float y);
double fmin(double x, double y);
long double fmin(long double x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 1 つ目の値 |
| `y` | 浮動小数点数 | 2 つ目の値 |

戻り値は 2 つのうち小さいほうの値です。片方が NaN の場合は、NaN でないほうを返します。両方が NaN のときだけ NaN を返します。

`std::min(a, b)` は、`b < a` が真なら `b` を、そうでなければ `a` を返す実装です。`a` が NaN のとき、`b < a` は常に偽なので、NaN が返ります。`b` が NaN のときは `a` が返ります。つまり、引数の順序によって結果が変わります。`fmin` は順序に依存せず、NaN でないほうを返します。

もう 1 つの違いは、戻り値が参照ではなく値であることです。`std::min` は `const T&` を返すので、一時オブジェクトを渡すと危険ですが、`fmin` にはその心配がありません。

符号つきゼロ（`+0.0` と `-0.0`）を比べたときの結果は、規格では決まっていません。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("fmin(1, 2)   = {}", std::fmin(1.0, 2.0));
  std::println("fmin(NaN, 2) = {}", std::fmin(nan, 2.0));   // NaN でないほうを返す
  std::println("fmin(1, NaN) = {}", std::fmin(1.0, nan));
}
```

```text title="実行結果"
fmin(1, 2)   = 1
fmin(NaN, 2) = 2
fmin(1, NaN) = 1
```

## ゲームでの使いどころ

値が欠けているかもしれない複数のセンサーや、計算の結果から最小値を取るときに、NaN を飛ばしたい場合に使います。

```cpp
// 計算できなかった距離が NaN で入っていても、有効な最小の距離が得られる
float nearest = std::numeric_limits<float>::infinity();
for (float d : distances) {
  nearest = std::fmin(nearest, d);
}
```

NaN は、0 で割る、無限大から無限大を引く、といった失敗の印です。NaN を黙って無視すると、バグが隠れることもあります。原因を探すデバッグ中は `std::min` のほうが、NaN が結果に出て気づきやすい場合もあります。

## よくあるミス

??? failure "NaN を無視して、バグに気づけなかった"
    失敗の印としての NaN は、あえて伝えたほうがよい場合もあります。デバッグ中は `std::min` に戻して確かめます。

??? failure "整数に使って、`double` に変換される"
    整数なら `std::min` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fmax`](fmax.md) | 大きいほうを返す |
| [`min`](../../algorithms/min.md) | テンプレート版。NaN の扱いは引数の順序に依存 |
| [`clamp`](../../algorithms/clamp.md) | 下限と上限の両方に収める |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fmin(x, y)` は小さいほう。片方が NaN ならもう一方を返す
    - [x] `std::min` と違い、引数の順序に依存しない
    - [x] 整数や普通の値には `std::min` で足りる

## 関連ページ

- [`std::fmax`](fmax.md)
- [cpprefjp: std::fmin](https://cpprefjp.github.io/reference/cmath/fmin.html)
- [cppreference: std::fmin](https://en.cppreference.com/w/cpp/numeric/math/fmin)

---
title: std::fmax
summary: "2 つの小数の大きいほうを返す（NaN は無視する）。"
order: 36
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fmax

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::max` は 2 つの値の大きいほうを返しますが、片方が NaN だと、比較が成り立たずに、引数の順序で結果が変わってしまいます。NaN が混ざりうる計算で、有効なほうの値を取りたいときに使うのが `std::fmax` です。

!!! tip "ポイント"
    - `std::fmax(1.0, 2.0)` は 2
    - 片方が NaN なら、もう一方を返す。両方 NaN なら NaN
    - `<cmath>` の関数で、浮動小数点数専用
    - 普通のゲームの計算では `std::max` で足りる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fmax {#fmax}

<span class="ver ver-11">C++11</span>

```cpp
float fmax(float x, float y);
double fmax(double x, double y);
long double fmax(long double x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 1 つ目の値 |
| `y` | 浮動小数点数 | 2 つ目の値 |

戻り値は 2 つのうち大きいほうの値です。片方が NaN の場合は NaN でないほうを返し、両方 NaN のときだけ NaN を返します。

`std::max` は、`a < b` が真なら `b` をそうでなければ `a` を返します。`a` が NaN だと `a < b` は偽なので `a`（NaN）が返り、`b` が NaN だと `b` が返ります。引数を入れ替えると結果が変わるのは、NaN を含む場合に比較が成り立たないためです。`fmax` は順序に依存しません。

戻り値は値なので、`std::max` のように一時オブジェクトの参照がぶら下がる危険はありません。

符号つきゼロの比較結果は、規格では決まっていません。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("fmax(1, 2)   = {}", std::fmax(1.0, 2.0));
  std::println("fmax(NaN, 2) = {}", std::fmax(nan, 2.0));   // NaN でないほうを返す
  std::println("fmax(1, NaN) = {}", std::fmax(1.0, nan));
}
```

```text title="実行結果"
fmax(1, 2)   = 2
fmax(NaN, 2) = 2
fmax(1, NaN) = 1
```

## ゲームでの使いどころ

複数の値の最大値を取るとき、NaN の入った要素を飛ばしたい場合に使います。

```cpp
float highest = -std::numeric_limits<float>::infinity();
for (float s : scores) {
  highest = std::fmax(highest, s);   // NaN の要素は無視される
}
```

NaN は失敗の印なので、無視する前になぜ NaN が出たのかを調べるほうがよい場面もあります。

## よくあるミス

??? failure "NaN を無視して、バグを見逃した"
    開発中は `std::max` に戻し、NaN を結果に出して気づけるようにします。

??? failure "整数に使って、`double` に変換される"
    整数なら `std::max` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fmin`](fmin.md) | 小さいほうを返す |
| [`max`](../../algorithms/max.md) | テンプレート版。NaN の扱いは引数の順序に依存 |
| [`clamp`](../../algorithms/clamp.md) | 範囲に収める |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fmax(x, y)` は大きいほう。片方が NaN ならもう一方を返す
    - [x] `std::max` と違い、引数の順序に依存しない
    - [x] 普通の値には `std::max` で足りる

## 関連ページ

- [`std::fmin`](fmin.md)
- [cpprefjp: std::fmax](https://cpprefjp.github.io/reference/cmath/fmax.html)
- [cppreference: std::fmax](https://en.cppreference.com/w/cpp/numeric/math/fmax)

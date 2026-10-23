---
title: std::remquo
summary: "割り算の余りと、商の下位ビットをいっしょに返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::remquo

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::remainder` は商を最も近い整数に丸めた余りを返しますが、その商は返しません。商の下位ビットも必要な場面（周期関数の象限の判定など）では、`std::remquo` が余りと商の一部を同時に返します。

!!! tip "ポイント"
    - `std::remquo(x, y, &q)` は `remainder(x, y)` を返し、商の符号と下位ビットを `q` に入れる
    - `q` には、商の絶対値の下位 3 ビット以上と、符号が入る
    - 三角関数の引数の縮約（範囲を 0〜2π に収める）で使う
    - ゲームでは使わない

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remquo {#remquo}

<span class="ver ver-11">C++11</span>

```cpp
float remquo(float x, float y, int* quo);
double remquo(double x, double y, int* quo);
long double remquo(long double x, long double y, int* quo);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 割られる数 |
| `y` | 浮動小数点数 | 割る数 |
| `quo` | `int*` | 商の符号と下位ビットの書き込み先 |

戻り値は `remainder(x, y)` と同じです。`*quo` には、`x / y` を最も近い整数に丸めた商の、符号と下位ビット（少なくとも 3 ビット）が入ります。商全体は返りません。

余りと商の下位ビットがあれば、象限（0〜3）を判定できます。三角関数の実装が、角度を π/2 の倍数で割って、象限と、その中での位置に分けるときに使います。

ゲームのコードで直接使う場面は、ほとんどありません。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  int quotient = 0;
  const double rem = std::remquo(7.0, 2.0, &quotient);       // 7 / 2 = 3.5 → 4 に丸め
  std::println("余り = {}, 商の下位ビット = {}", rem, quotient);
}
```

```text title="実行結果"
余り = -1, 商の下位ビット = 4
```

## ゲームでの使いどころ

角度の縮約と象限の判定を 1 回で行うライブラリの実装で使われます。

## よくあるミス

??? failure "`quo` に商の全体が入ると思う"
    下位ビットと符号だけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remainder`](remainder.md) | 余りだけ |
| [`fmod`](fmod.md) | 切り捨ての余り |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `remquo` は余りと商の下位ビットを同時に返す
    - [x] `remainder` と同じ余り
    - [x] 角度の縮約に使われる

## 関連ページ

- [cpprefjp: std::remquo](https://cpprefjp.github.io/reference/cmath/remquo.html)
- [cppreference: std::remquo](https://en.cppreference.com/w/cpp/numeric/math/remquo)

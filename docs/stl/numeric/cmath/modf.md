---
title: std::modf
summary: "小数を、整数部と小数部に分ける。"
order: 40
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::modf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

座標を「どのマスにいるか」と「マスの中のどの位置か」に分けたい。浮動小数点数を整数部と小数部に分けて扱いたい場面があります。

`std::modf` は、<strong>値を整数部と小数部に分けて</strong>返します。

!!! tip "ポイント"
    - `std::modf(3.75, &ip)` は 0.75 を返し、`ip` に 3 が入る
    - 負の数でも、整数部と小数部は同じ符号になる
    - 整数部は浮動小数点数のポインタに書き込まれる
    - マス目と、マス内の位置の分離に使える

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::modf {#modf}

```cpp
float modf(float x, float* iptr);
double modf(double x, double* iptr);
long double modf(long double x, long double* iptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 分けたい値 |
| `iptr` | 浮動小数点数のポインタ | 整数部の書き込み先。`nullptr` は不可 |

戻り値は小数部、`*iptr` に整数部が入ります。どちらも `x` と同じ符号を持ち、足すと元の値に戻ります。`modf(-3.75)` は小数部 −0.75、整数部 −3 です。

`floor` で整数部を取り、元の値から引く方法もありますが、負の数では結果が違います（`floor(-3.75)` は −4、小数部は 0.25）。`modf` は符号に対して対称で、0 方向への切り捨てになります。

`iptr` に `nullptr` を渡すと、未定義動作です。整数部が要らない場合も、一時変数を用意して渡します。

無限大では、小数部が ±0、整数部が無限大になります。NaN では両方 NaN です。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  double integer_part;
  const double fraction = std::modf(3.75, &integer_part);
  std::println("3.75  -> 整数部 {}, 小数部 {}", integer_part, fraction);

  const double fraction2 = std::modf(-3.75, &integer_part);
  std::println("-3.75 -> 整数部 {}, 小数部 {}", integer_part, fraction2);
}
```

```text title="実行結果"
3.75  -> 整数部 3, 小数部 0.75
-3.75 -> 整数部 -3, 小数部 -0.75
```

## ゲームでの使いどころ

連続した座標をタイルの番号とタイル内の位置に分けるときに使います。

```cpp
// x = 5.3 → 5 番目のタイルの 0.3 の位置
double tile_index;
const double offset = std::modf(position.x, &tile_index);
```

座標が負になりうる場合は、`floor` の方式（常に小さい方へ）のほうが、タイル番号が連続するので適しています。

## よくあるミス

??? failure "負の座標で、タイル番号が 0 の周りで重なる"
    `modf` は 0 方向に切り捨てるので、−0.5 も 0.5 も整数部は 0 です。タイル分割には `floor` を使います。

??? failure "`iptr` に `nullptr` を渡す"
    一時変数を用意して渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 切り捨て（負の無限大方向） |
| [`trunc`](trunc.md) | 0 方向への切り捨て |
| [`fmod`](fmod.md) | 余り |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `modf(x, &ip)` は小数部を返し、整数部を `ip` に入れる
    - [x] 両方とも `x` と同じ符号（0 方向への切り捨て）
    - [x] 負の座標のタイル分割には `floor`

## 関連ページ

- [`std::floor`](floor.md)
- [cpprefjp: std::modf](https://cpprefjp.github.io/reference/cmath/modf.html)
- [cppreference: std::modf](https://en.cppreference.com/w/cpp/numeric/math/modf)

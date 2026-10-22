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

浮動小数点数は連続ではなく、飛び飛びの値です。`nextafter(x, y)` は、x から y のほうへ 1 つ進んだ、隣の表せる値を返します。許容誤差をぎりぎりまで詰めたい場面で使います。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nextafter {#nextafter}

```cpp
double nextafter(double x, double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 出発点 |
| `y` | 浮動小数点 | 向かう先 |

- 戻り値: x の隣の値（y の方向）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  std::println("{}", std::nextafter(1.0, 2.0) - 1.0 == std::numeric_limits<double>::epsilon());
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 「1 より少しだけ大きい値」をつくる |

## よくあるミス

??? failure "`x + epsilon` と同じだと思う"
    x が 1 から離れるほど、隣の値との差は変わります。`epsilon` は 1 付近の差です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nexttoward`](nexttoward.md) | y が long double |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x の次に表せる浮動小数点数を返す（y の方向へ）
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::nextafter](https://cpprefjp.github.io/reference/cmath/nextafter.html)
- [cppreference: std::nextafter](https://en.cppreference.com/w/cpp/numeric/math/nextafter)

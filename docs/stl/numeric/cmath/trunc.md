---
title: std::trunc
summary: "小数部を捨てる（0 に向かって切り捨てる）。"
order: 12
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::trunc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

小数部を捨てて整数部だけを取り出したい。`floor` は負の無限大方向、`ceil` は正の無限大方向へ丸めますが、負の数では結果が直感に合いません。`-2.7` の小数部を捨てたら `-2` が欲しい、という場合に使うのが `std::trunc` です。

!!! tip "ポイント"
    - `std::trunc(2.7)` は 2、`std::trunc(-2.7)` は −2
    - 0 方向への切り捨て
    - `floor(-2.7)` は −3 で、`trunc` と違う
    - 戻り値は浮動小数点数のまま

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::trunc {#trunc}

<span class="ver ver-11">C++11</span>

```cpp
float trunc(float x);
double trunc(double x);
long double trunc(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 小数部を捨てたい値 |

戻り値は `x` の整数部で、絶対値が `x` 以下の最も近い整数です。正の数では `floor` と、負の数では `ceil` と同じ結果になります。

整数型へのキャスト `static_cast<int>(x)` も、0 方向への切り捨てなので、同じ丸め方です。`trunc` は戻り値が浮動小数点数のままで、整数に入りきらない大きな値でも使えます。

無限大と NaN はそのまま返ります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("trunc(2.7)  = {}", std::trunc(2.7));
  std::println("trunc(-2.7) = {}", std::trunc(-2.7));    // 0 方向
  std::println("floor(-2.7) = {}", std::floor(-2.7));    // 負の無限大方向
}
```

```text title="実行結果"
trunc(2.7)  = 2
trunc(-2.7) = -2
floor(-2.7) = -3
```

## ゲームでの使いどころ

符号に対して対称な切り捨てが必要なとき（速度や移動量の整数化、小数部の取り出し）に使います。

```cpp
const float frac = value - std::trunc(value);   // 小数部（符号は value に従う）
```

タイルの座標のように、負の値が連続して並ぶ場合は、`floor` のほうが適しています。

## よくあるミス

??? failure "負の座標でタイル番号が 0 の周りで重なる"
    `floor` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 負の無限大方向へ |
| [`ceil`](ceil.md) | 正の無限大方向へ |
| [`round`](round.md) | 最も近い整数へ |
| [`modf`](modf.md) | 整数部と小数部に分ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `trunc(x)` は 0 方向への切り捨て
    - [x] 正の数は `floor`、負の数は `ceil` と同じ
    - [x] 整数へのキャストと同じ丸め方

## 関連ページ

- [cpprefjp: std::trunc](https://cpprefjp.github.io/reference/cmath/trunc.html)
- [cppreference: std::trunc](https://en.cppreference.com/w/cpp/numeric/math/trunc)

---
title: std::rint
summary: "現在の丸めモードで整数に丸める（結果は小数）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::rint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::round` は 0.5 を常に遠い側へ丸めますが、`std::rint` は、<strong>現在の丸めモードに従って整数に丸め</strong>ます。既定では 0.5 を偶数側へ丸めます。`nearbyint` との違いは、丸めが起きたときに `FE_INEXACT` を立てるかどうかです。

!!! tip "ポイント"
    - `std::rint(2.5)` は 2、`std::rint(3.5)` は 4（偶数へ）
    - 丸めモード（`fesetround`）に従う
    - 結果が不正確なとき `FE_INEXACT` を立てる（`nearbyint` は立てない）
    - 戻り値は浮動小数点数のまま

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::rint {#rint}

<span class="ver ver-11">C++11</span>

```cpp
float rint(float x);
double rint(double x);
long double rint(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 丸めたい値 |

戻り値は、`x` を現在の丸めモードで整数に丸めた値です。既定の最近接偶数では、小数部がちょうど 0.5 のとき、偶数側に丸めます。

`nearbyint` との違いは、浮動小数点例外 `FE_INEXACT` の扱いだけです。丸めで値が変わったとき、`rint` は `FE_INEXACT` を立ててよく、`nearbyint` は立てません。例外フラグを調べない普通のコードでは、違いは見えません。

整数型で結果が欲しいときは `lrint` / `llrint` を使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("rint(2.5) = {}", std::rint(2.5));     // 偶数の 2 へ
  std::println("rint(3.5) = {}", std::rint(3.5));     // 偶数の 4 へ
  std::println("rint(2.4) = {}", std::rint(2.4));
}
```

```text title="実行結果"
rint(2.5) = 2
rint(3.5) = 4
rint(2.4) = 2
```

## ゲームでの使いどころ

統計の計算で、丸めの偏りを避けたいときに使います。四捨五入が必要なら `round` です。

## よくあるミス

??? failure "`round` と同じと思い、2.5 が 2 になって驚く"
    偶数丸めです。四捨五入は `round` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`nearbyint`](nearbyint.md) | `FE_INEXACT` を立てない版 |
| [`round`](round.md) | 0.5 を常に遠い側へ |
| [`lrint`](lrint.md) | `long` で返す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `rint(x)` は現在の丸めモードで整数に丸める
    - [x] 既定は偶数丸め
    - [x] `nearbyint` との違いは `FE_INEXACT` だけ

## 関連ページ

- [cpprefjp: std::rint](https://cpprefjp.github.io/reference/cmath/rint.html)
- [cppreference: std::rint](https://en.cppreference.com/w/cpp/numeric/math/rint)

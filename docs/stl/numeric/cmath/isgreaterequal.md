---
title: std::isgreaterequal
summary: "浮動小数点を比べる（x が y 以上か）。NaN でも例外を出さない。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isgreaterequal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

NaN が混ざった値を `<` や `>` で比べると、結果は偽になります。ただしこの比較で、一部の環境では、浮動小数点例外 `FE_INVALID` のフラグが立ち、不要な警告やトラップが出ることがあります。`std::isgreaterequal` は、<strong>NaN が混ざっても、例外を立てずに</strong>比べます。

!!! tip "ポイント"
    - `std::isgreaterequal(x, y)` は `x` が `y` 以上とき `true`
    - どちらかが NaN なら `false`（例外フラグは立たない）
    - `x >= y` と同じ結果だが、`FE_INVALID` を立てない
    - 普通のゲームのコードでは、演算子で足りる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isgreaterequal {#isgreaterequal}

<span class="ver ver-11">C++11</span>

```cpp
bool isgreaterequal(float x, float y);
bool isgreaterequal(double x, double y);
bool isgreaterequal(long double x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 1 つ目の値 |
| `y` | 浮動小数点数 | 2 つ目の値 |

戻り値は、`x >= y` のとき `true` です。どちらかが NaN のときは、順序が決まらないので `false` を返します。

演算子 `x >= y` との違いは、NaN を含む場合に `FE_INVALID` を立てないことです。演算子は、NaN を含む順序の比較（`<` など）で、無効な演算として例外フラグを立ててよい、と規格が許しています。`isgreaterequal` はこれを避けます。

浮動小数点例外のフラグを調べているプログラムが NaN の入力をわざと比較して、無関係な `FE_INVALID` で誤検出しないために使います。例外フラグを調べない普通のコードでは、結果は演算子と同じなので、演算子を使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("2.0 >= 2.0 = {}", std::isgreaterequal(2.0, 2.0));
  std::println("NaN を含むと = {}", std::isgreaterequal(nan, 1.0));
}
```

```text title="実行結果"
2.0 >= 2.0 = true
NaN を含むと = false
```

## ゲームでの使いどころ

例外フラグを使った異常検出のコードで、NaN の比較が誤検出を起こさないようにするときに使います。通常は `x >= y` などの演算子で足ります。

## よくあるミス

??? failure "NaN を含む比較の結果を順序があると思う"
    NaN が絡むと必ず `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isunordered`](isunordered.md) | どちらかが NaN か |
| [`isnan`](isnan.md) | NaN か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `isgreaterequal(x, y)` は NaN があっても例外を立てずに比べる
    - [x] NaN を含むと `false`
    - [x] 通常は演算子で足りる

## 関連ページ

- [cpprefjp: std::isgreaterequal](https://cpprefjp.github.io/reference/cmath/isgreaterequal.html)
- [cppreference: std::isgreaterequal](https://en.cppreference.com/w/cpp/numeric/math/isgreaterequal)

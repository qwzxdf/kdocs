---
title: std::fpclassify
summary: "浮動小数点数の種類（0・正規数・NaN など）を判定する。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fpclassify

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

浮動小数点数には、普通の数のほかに、ゼロ、非常に小さい数（非正規化数）、無限大、NaN があります。`std::fpclassify` は、値がどの種類かを 1 回の呼び出しで分類します。

!!! tip "ポイント"
    - `std::fpclassify(x)` は `FP_NORMAL`、`FP_ZERO`、`FP_SUBNORMAL`、`FP_INFINITE`、`FP_NAN` のいずれかを返す
    - 個別の判定は `isnan`・`isinf`・`isfinite`・`isnormal`
    - `switch` で場合分けしたいときに便利
    - 戻り値は `int`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fpclassify {#fpclassify}

<span class="ver ver-11">C++11</span>

```cpp
int fpclassify(float x);
int fpclassify(double x);
int fpclassify(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 分類したい値 |

戻り値は、`x` の種類を表す 5 つの定数のいずれかです。

- `FP_NAN`: 数ではない（NaN）
- `FP_INFINITE`: 正または負の無限大
- `FP_ZERO`: 正または負のゼロ
- `FP_SUBNORMAL`: 非正規化数。0 に近すぎて、通常の精度で表せない小さな数
- `FP_NORMAL`: 通常の数

1 回の呼び出しで全部の場合を分けられるので、`switch` で書くと見通しがよくなります。個別に知りたいだけなら、`isnan` や `isinf` のほうが読みやすいです。

`-ffast-math` のもとでは、NaN や無限大が出ない仮定のため、正しく分類されないことがあります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double inf = std::numeric_limits<double>::infinity();
  std::println("1.0 は通常の数 : {}", std::fpclassify(1.0) == FP_NORMAL);
  std::println("0.0 はゼロ     : {}", std::fpclassify(0.0) == FP_ZERO);
  std::println("inf は無限大   : {}", std::fpclassify(inf) == FP_INFINITE);
}
```

```text title="実行結果"
1.0 は通常の数 : true
0.0 はゼロ     : true
inf は無限大   : true
```

## ゲームでの使いどころ

デバッグ用に、値の種類をログに出すときに使います。

```cpp
switch (std::fpclassify(value)) {
  case FP_NAN:      Log("NaN"); break;
  case FP_INFINITE: Log("無限大"); break;
  case FP_SUBNORMAL: Log("非正規化数"); break;
  default: break;
}
```

## よくあるミス

??? failure "戻り値を `bool` として使う"
    戻り値は分類の定数です。比較して使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | NaN か |
| [`isinf`](isinf.md) | 無限大か |
| [`isnormal`](isnormal.md) | 通常の数か |
| [`isfinite`](isfinite.md) | 有限の値か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fpclassify(x)` は値の種類を 5 つに分類する
    - [x] `switch` で場合分けしたいときに便利
    - [x] 個別の判定は `isnan` / `isinf` など

## 関連ページ

- [cpprefjp: std::fpclassify](https://cpprefjp.github.io/reference/cmath/fpclassify.html)
- [cppreference: std::fpclassify](https://en.cppreference.com/w/cpp/numeric/math/fpclassify)

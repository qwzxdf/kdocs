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

`isnan` や `isinf` など個別の関数でもできますが、`fpclassify` は 1 回で種類を分類します。結果は `FP_ZERO`・`FP_NORMAL`・`FP_SUBNORMAL`・`FP_INFINITE`・`FP_NAN` のどれかです。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fpclassify {#fpclassify}

```cpp
int fpclassify(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: `FP_NAN`・`FP_INFINITE`・`FP_ZERO`・`FP_SUBNORMAL`・`FP_NORMAL` のどれか
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::fpclassify(0.0) == FP_ZERO);
  std::println("{}", std::fpclassify(1.0) == FP_NORMAL);
}
```

```text title="実行結果"
true
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 計算結果の異常値のデバッグ |

## よくあるミス

??? failure "`int` の比較を忘れる"
    戻り値は列挙ではなく `int` です。`FP_xxx` のマクロと比べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | NaN だけ |
| [`isinf`](isinf.md) | 無限大だけ |
| [`isnormal`](isnormal.md) | 正規数かどうか |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点数の種類（0・正規数・NaN など）を判定する
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fpclassify](https://cpprefjp.github.io/reference/cmath/fpclassify.html)
- [cppreference: std::fpclassify](https://en.cppreference.com/w/cpp/numeric/math/fpclassify)

---
title: <cfloat>（小数の限界マクロ）
summary: "`FLT_EPSILON` など、小数型の精度・範囲を表す C 由来のマクロ。"
order: 31
tags:
  - 数値
---

# <cfloat>（小数の限界マクロ）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cfloat>`
</div>

`<cfloat>` は、**小数型（`float`、`double`）の精度や範囲を表すマクロ**を定義するヘッダーです。`FLT_EPSILON`（`float` で 1 と区別できる最小の差）、`DBL_MAX`、`FLT_DIG`（確実に表せる桁数）などがあります。C++ では [`std::numeric_limits`](limits.md) が代わりに使えます。

!!! tip "ポイント"
    - `FLT_EPSILON` は約 1.19e-07。浮動小数点の比較の許容誤差の目安。
    - `FLT_DIG` は 6、`DBL_DIG` は 15（確実に表せる 10 進の桁数）。
    - 新しいコードでは `std::numeric_limits<float>::epsilon()`。

## 関数の詳しい説明

### <cfloat> {#cfloat}

```cpp
#define FLT_EPSILON 1.19209290e-07F
#define FLT_DIG 6
#define DBL_DIG 15
```

- 戻り値: 定数
- 計算量: コンパイル時

```cpp
#include <cfloat>
#include <print>

int main() {
  std::println("{} {} {}", FLT_EPSILON, FLT_DIG, DBL_DIG);
}
```

```text title="実行結果"
1.1920929e-07 6 15
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 浮動小数点の比較の許容誤差の目安 | `FLT_EPSILON` |

## よくあるミス

??? failure "EPSILON を絶対的な許容誤差にする"
    `FLT_EPSILON` は 1.0 付近での誤差です。大きな値や小さな値では、相対的な比較が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::numeric_limits`](limits.md) | 型安全な代わり |
| [`climits`](climits.md) | 整数の限界 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 小数の限界マクロ
    - [x] `FLT_EPSILON` は 1 付近の誤差
    - [x] C 由来

## 関連ページ

- [cpprefjp: <cfloat>（小数の限界マクロ）](https://cpprefjp.github.io/reference/cfloat.html)
- [cppreference: <cfloat>（小数の限界マクロ）](https://en.cppreference.com/w/cpp/types/climits)

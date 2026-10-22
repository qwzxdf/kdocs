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

### FLT_EPSILON {#FLT_EPSILON}

```cpp
#define FLT_EPSILON /* 実装定義 */
```

- 戻り値: `float` の1 と、1 より大きい次の値との差（機械イプシロン）
- 計算量: コンパイル時

`float` の1 と、1 より大きい次の値との差（機械イプシロン）です。比べるときの許容誤差の目安に使えますが、値の大きさに応じた比べ方（相対誤差）が必要です。

`std::numeric_limits<float>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### DBL_EPSILON {#DBL_EPSILON}

```cpp
#define DBL_EPSILON /* 実装定義 */
```

- 戻り値: `double` の1 と、1 より大きい次の値との差（機械イプシロン）
- 計算量: コンパイル時

`double` の1 と、1 より大きい次の値との差（機械イプシロン）です。比べるときの許容誤差の目安に使えますが、値の大きさに応じた比べ方（相対誤差）が必要です。

`std::numeric_limits<double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LDBL_EPSILON {#LDBL_EPSILON}

```cpp
#define LDBL_EPSILON /* 実装定義 */
```

- 戻り値: `long double` の1 と、1 より大きい次の値との差（機械イプシロン）
- 計算量: コンパイル時

`long double` の1 と、1 より大きい次の値との差（機械イプシロン）です。比べるときの許容誤差の目安に使えますが、値の大きさに応じた比べ方（相対誤差）が必要です。

`std::numeric_limits<long double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### FLT_MAX {#FLT_MAX}

```cpp
#define FLT_MAX /* 実装定義 */
```

- 戻り値: `float` の表せる最大の有限値
- 計算量: コンパイル時

`float` の表せる最大の有限値です。

`std::numeric_limits<float>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### DBL_MAX {#DBL_MAX}

```cpp
#define DBL_MAX /* 実装定義 */
```

- 戻り値: `double` の表せる最大の有限値
- 計算量: コンパイル時

`double` の表せる最大の有限値です。

`std::numeric_limits<double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LDBL_MAX {#LDBL_MAX}

```cpp
#define LDBL_MAX /* 実装定義 */
```

- 戻り値: `long double` の表せる最大の有限値
- 計算量: コンパイル時

`long double` の表せる最大の有限値です。

`std::numeric_limits<long double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### FLT_MIN {#FLT_MIN}

```cpp
#define FLT_MIN /* 実装定義 */
```

- 戻り値: `float` の表せる最小の正の正規数
- 計算量: コンパイル時

`float` の表せる最小の正の正規数です。

`std::numeric_limits<float>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### DBL_MIN {#DBL_MIN}

```cpp
#define DBL_MIN /* 実装定義 */
```

- 戻り値: `double` の表せる最小の正の正規数
- 計算量: コンパイル時

`double` の表せる最小の正の正規数です。

`std::numeric_limits<double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LDBL_MIN {#LDBL_MIN}

```cpp
#define LDBL_MIN /* 実装定義 */
```

- 戻り値: `long double` の表せる最小の正の正規数
- 計算量: コンパイル時

`long double` の表せる最小の正の正規数です。

`std::numeric_limits<long double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### FLT_DIG {#FLT_DIG}

```cpp
#define FLT_DIG /* 実装定義 */
```

- 戻り値: `float` の10 進数で、情報を失わずに往復できる桁数
- 計算量: コンパイル時

`float` の10 進数で、情報を失わずに往復できる桁数です。

`std::numeric_limits<float>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### DBL_DIG {#DBL_DIG}

```cpp
#define DBL_DIG /* 実装定義 */
```

- 戻り値: `double` の10 進数で、情報を失わずに往復できる桁数
- 計算量: コンパイル時

`double` の10 進数で、情報を失わずに往復できる桁数です。

`std::numeric_limits<double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LDBL_DIG {#LDBL_DIG}

```cpp
#define LDBL_DIG /* 実装定義 */
```

- 戻り値: `long double` の10 進数で、情報を失わずに往復できる桁数
- 計算量: コンパイル時

`long double` の10 進数で、情報を失わずに往復できる桁数です。

`std::numeric_limits<long double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### FLT_MANT_DIG {#FLT_MANT_DIG}

```cpp
#define FLT_MANT_DIG /* 実装定義 */
```

- 戻り値: `float` の仮数部のビット数（基数 `FLT_RADIX` の桁数）
- 計算量: コンパイル時

`float` の仮数部のビット数（基数 `FLT_RADIX` の桁数）です。

`std::numeric_limits<float>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### DBL_MANT_DIG {#DBL_MANT_DIG}

```cpp
#define DBL_MANT_DIG /* 実装定義 */
```

- 戻り値: `double` の仮数部のビット数（基数 `FLT_RADIX` の桁数）
- 計算量: コンパイル時

`double` の仮数部のビット数（基数 `FLT_RADIX` の桁数）です。

`std::numeric_limits<double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LDBL_MANT_DIG {#LDBL_MANT_DIG}

```cpp
#define LDBL_MANT_DIG /* 実装定義 */
```

- 戻り値: `long double` の仮数部のビット数（基数 `FLT_RADIX` の桁数）
- 計算量: コンパイル時

`long double` の仮数部のビット数（基数 `FLT_RADIX` の桁数）です。

`std::numeric_limits<long double>` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### FLT_RADIX {#FLT_RADIX}

```cpp
#define FLT_RADIX 2
```

- 戻り値: 浮動小数点の基数（ほぼ 2）
- 計算量: コンパイル時

浮動小数点数の指数の基数です。ほとんどの環境で 2 です。

### FLT_EVAL_METHOD {#FLT_EVAL_METHOD}

```cpp
#define FLT_EVAL_METHOD /* 0, 1, 2 のどれか */
```

- 戻り値: 式を評価するときの精度の方式
- 計算量: コンパイル時

`float` どうしの式を、`float` のまま計算するか（0）、`double` に拡張して計算するか（1）、`long double` に拡張するか（2）を表します。x87 の古い環境では 2 になり、計算結果が微妙に変わります。

### FLT_ROUNDS {#FLT_ROUNDS}

```cpp
#define FLT_ROUNDS /* 丸めモード */
```

- 戻り値: 現在の丸めモード
- 計算量: 実行時

浮動小数点の加算の丸めモード（0: 0 方向、1: 最近接、2: 正の無限大、3: 負の無限大）を表します。変えるのは `std::fesetround` です。

### DECIMAL_DIG {#DECIMAL_DIG}

```cpp
#define DECIMAL_DIG /* 実装定義 */
```

- 戻り値: 最大の浮動小数点型を、10 進数に往復するのに必要な桁数
- 計算量: コンパイル時

最も精度の高い浮動小数点型（`long double`）の値を、10 進数に変換して戻しても同じ値になるのに必要な桁数です。

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

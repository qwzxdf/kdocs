---
title: <climits>（整数の限界マクロ）
summary: "`INT_MAX` など、整数型の最大値・最小値を表す C 由来のマクロ。"
order: 30
tags:
  - 数値
---

# <climits>（整数の限界マクロ）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <climits>`
</div>

`<climits>` は、**整数型の最大値・最小値・ビット数を表すマクロ**を定義するヘッダーです。`INT_MAX`、`INT_MIN`、`UINT_MAX`、`CHAR_BIT`（1 バイトのビット数）などがあります。C++ では、型安全な [`std::numeric_limits`](limits.md) が代わりに使えます。

!!! tip "ポイント"
    - `INT_MAX` は 2147483647（32 ビット `int`）。
    - `CHAR_BIT` は 8。
    - 新しいコードでは `std::numeric_limits<int>::max()` が型安全。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### <climits> {#climits}

```cpp
#define INT_MAX 2147483647
#define INT_MIN (-INT_MAX - 1)
#define CHAR_BIT 8
```

- 戻り値: 定数
- 計算量: コンパイル時

```cpp
#include <climits>
#include <print>

int main() {
  std::println("{} {}", INT_MAX, CHAR_BIT);
}
```

```text title="実行結果"
2147483647 8
```

### CHAR_BIT {#CHAR_BIT}

```cpp
#define CHAR_BIT /* 実装定義 */
```

- 戻り値: 1 バイトのビット数（ほぼ 8）（整数の定数）
- 計算量: コンパイル時

1 バイトのビット数（ほぼ 8）。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### SCHAR_MIN {#SCHAR_MIN}

```cpp
#define SCHAR_MIN /* 実装定義 */
```

- 戻り値: `signed char` の最小値（整数の定数）
- 計算量: コンパイル時

`signed char` の最小値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### SCHAR_MAX {#SCHAR_MAX}

```cpp
#define SCHAR_MAX /* 実装定義 */
```

- 戻り値: `signed char` の最大値（整数の定数）
- 計算量: コンパイル時

`signed char` の最大値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### UCHAR_MAX {#UCHAR_MAX}

```cpp
#define UCHAR_MAX /* 実装定義 */
```

- 戻り値: `unsigned char` の最大値（整数の定数）
- 計算量: コンパイル時

`unsigned char` の最大値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### CHAR_MIN {#CHAR_MIN}

```cpp
#define CHAR_MIN /* 実装定義 */
```

- 戻り値: `char` の最小値（符号つきの環境では `SCHAR_MIN`、符号なしでは 0）（整数の定数）
- 計算量: コンパイル時

`char` の最小値（符号つきの環境では `SCHAR_MIN`、符号なしでは 0）。`char` の符号は処理系で決まります。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### CHAR_MAX {#CHAR_MAX}

```cpp
#define CHAR_MAX /* 実装定義 */
```

- 戻り値: `char` の最大値（整数の定数）
- 計算量: コンパイル時

`char` の最大値。`char` の符号は処理系で決まります。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### SHRT_MIN {#SHRT_MIN}

```cpp
#define SHRT_MIN /* 実装定義 */
```

- 戻り値: `short` の最小値（整数の定数）
- 計算量: コンパイル時

`short` の最小値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### SHRT_MAX {#SHRT_MAX}

```cpp
#define SHRT_MAX /* 実装定義 */
```

- 戻り値: `short` の最大値（整数の定数）
- 計算量: コンパイル時

`short` の最大値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### USHRT_MAX {#USHRT_MAX}

```cpp
#define USHRT_MAX /* 実装定義 */
```

- 戻り値: `unsigned short` の最大値（整数の定数）
- 計算量: コンパイル時

`unsigned short` の最大値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### INT_MIN {#INT_MIN}

```cpp
#define INT_MIN /* 実装定義 */
```

- 戻り値: `int` の最小値（整数の定数）
- 計算量: コンパイル時

`int` の最小値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### INT_MAX {#INT_MAX}

```cpp
#define INT_MAX /* 実装定義 */
```

- 戻り値: `int` の最大値（整数の定数）
- 計算量: コンパイル時

`int` の最大値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### UINT_MAX {#UINT_MAX}

```cpp
#define UINT_MAX /* 実装定義 */
```

- 戻り値: `unsigned int` の最大値（整数の定数）
- 計算量: コンパイル時

`unsigned int` の最大値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LONG_MIN {#LONG_MIN}

```cpp
#define LONG_MIN /* 実装定義 */
```

- 戻り値: `long` の最小値（Windows では 32 ビット）（整数の定数）
- 計算量: コンパイル時

`long` の最小値（Windows では 32 ビット）。値は環境で変わります（Windows は 32 ビット、Linux の 64 ビット環境は 64 ビット）。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LONG_MAX {#LONG_MAX}

```cpp
#define LONG_MAX /* 実装定義 */
```

- 戻り値: `long` の最大値（Windows では 32 ビット）（整数の定数）
- 計算量: コンパイル時

`long` の最大値（Windows では 32 ビット）。値は環境で変わります（Windows は 32 ビット、Linux の 64 ビット環境は 64 ビット）。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### ULONG_MAX {#ULONG_MAX}

```cpp
#define ULONG_MAX /* 実装定義 */
```

- 戻り値: `unsigned long` の最大値（整数の定数）
- 計算量: コンパイル時

`unsigned long` の最大値。値は環境で変わります（Windows は 32 ビット、Linux の 64 ビット環境は 64 ビット）。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LLONG_MIN {#LLONG_MIN}

```cpp
#define LLONG_MIN /* 実装定義 */
```

- 戻り値: `long long` の最小値（整数の定数）
- 計算量: コンパイル時

`long long` の最小値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### LLONG_MAX {#LLONG_MAX}

```cpp
#define LLONG_MAX /* 実装定義 */
```

- 戻り値: `long long` の最大値（整数の定数）
- 計算量: コンパイル時

`long long` の最大値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### ULLONG_MAX {#ULLONG_MAX}

```cpp
#define ULLONG_MAX /* 実装定義 */
```

- 戻り値: `unsigned long long` の最大値（整数の定数）
- 計算量: コンパイル時

`unsigned long long` の最大値。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

### MB_LEN_MAX {#MB_LEN_MAX}

```cpp
#define MB_LEN_MAX /* 実装定義 */
```

- 戻り値: マルチバイト文字 1 文字の最大のバイト数（整数の定数）
- 計算量: コンパイル時

マルチバイト文字 1 文字の最大のバイト数。

`std::numeric_limits` のほうが型に合わせて書けるので、新しいコードではそちらを優先します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| C のライブラリの定数をそのまま使う | `INT_MAX` |

## よくあるミス

??? failure "マクロの min / max と混同する"
    Windows の `min` / `max` マクロとは別です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::numeric_limits`](limits.md) | 型安全な代わり |
| [`cfloat`](cfloat.md) | 小数の限界 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数の限界マクロ
    - [x] 型安全なのは numeric_limits
    - [x] C 由来

## 関連ページ

- [cpprefjp: <climits>（整数の限界マクロ）](https://cpprefjp.github.io/reference/climits.html)
- [cppreference: <climits>（整数の限界マクロ）](https://en.cppreference.com/w/cpp/types/climits)

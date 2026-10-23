---
title: std::scalbn
summary: "x × 2ⁿ を、乗算を使わずに計算する。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::scalbn

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::ldexp(x, n)` と同じく、`x × 2ⁿ` を指数部をずらして求めます。`ldexp` は 2 進数の環境を前提にした名前ですが、`std::scalbn` は、浮動小数点の基数（`FLT_RADIX`）を使う、より一般的な形です。ほとんどの環境で基数は 2 なので、結果は `ldexp` と同じです。

!!! tip "ポイント"
    - `std::scalbn(1.5, 3)` は 12（1.5 × 2³）
    - 基数が 2 の環境では `ldexp` と同じ
    - `n` が `long` の版は `scalbln`
    - 指数部をずらすだけなので、誤差が出ない

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::scalbn {#scalbn}

<span class="ver ver-11">C++11</span>

```cpp
float scalbn(float x, int n);
double scalbn(double x, int n);
long double scalbn(long double x, int n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 元の値 |
| `n` | `int` | 指数 |

戻り値は `x × FLT_RADIX^n` です。ほぼ全ての環境で `FLT_RADIX` は 2 なので、`x × 2ⁿ` と読めます。指数部を直接書き換えるため、乗算より速く、丸め誤差も生じません（範囲内の場合）。

結果が大きすぎれば無限大、小さすぎれば 0 や非正規化数になります。

`n` の型は `int` です。`long` の範囲が要るときは `scalbln` を使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("scalbn(1.5, 3)  = {}", std::scalbn(1.5, 3));
  std::println("scalbn(1.0, -2) = {}", std::scalbn(1.0, -2));
}
```

```text title="実行結果"
scalbn(1.5, 3)  = 12
scalbn(1.0, -2) = 0.25
```

## ゲームでの使いどころ

固定小数点の値を実数に直すなど、2 の累乗のスケールを掛けるときに使います。多くの場合、`ldexp` が読みやすい名前です。

## よくあるミス

??? failure "`n` に浮動小数点数を渡して切り捨てられる"
    `n` は整数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ldexp`](ldexp.md) | 2 進数の環境向けの名前 |
| [`scalbln`](scalbln.md) | `n` が `long` |
| [`frexp`](frexp.md) | 仮数と指数に分ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `scalbn(x, n)` は `x × 2ⁿ`
    - [x] 基数 2 の環境では `ldexp` と同じ
    - [x] 指数部をずらすだけで誤差がない

## 関連ページ

- [cpprefjp: std::scalbn](https://cpprefjp.github.io/reference/cmath/scalbn.html)
- [cppreference: std::scalbn](https://en.cppreference.com/w/cpp/numeric/math/scalbn)

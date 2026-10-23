---
title: std::ldexp
summary: "x × 2^n を求める（2 のべき乗倍）。"
order: 41
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::ldexp

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

浮動小数点数は、内部では「仮数」と「指数」に分かれています。`x * 2^n` は、指数部をずらすだけで済み、掛け算を行う必要がありません。

`std::ldexp` は、<strong>`x` に 2 の `n` 乗を掛けた値</strong>を、この性質を使って求めます。

!!! tip "ポイント"
    - `std::ldexp(1.5, 3)` は 12（1.5 × 2³）
    - `n` は整数。`x * exp2(n)` と同じ意味
    - 逆の分解は `frexp`
    - 精度の落ちない拡大・縮小になる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ldexp {#ldexp}

```cpp
float ldexp(float x, int exp);
double ldexp(double x, int exp);
long double ldexp(long double x, int exp);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 元の値 |
| `exp` | `int` | 2 の指数 |

戻り値は `x * 2^exp` です。2 の累乗を掛けるのは、指数部を変えるだけなので、誤差が出ません（範囲を超えない限り）。

結果が大きすぎて型の範囲を超えると無限大、小さすぎると 0 や非正規化数になります。

`x * std::exp2(exp)` と同じ値ですが、2 の累乗を計算してから掛ける手間がなく、丸めが 1 回で済みます。ゲームの通常のコードでは使う機会は少なく、数値計算のライブラリが内部で使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("ldexp(1.5, 3)  = {}", std::ldexp(1.5, 3));     // 1.5 * 8
  std::println("ldexp(1.0, -2) = {}", std::ldexp(1.0, -2));    // 1.0 / 4
  std::println("ldexp(3.0, 0)  = {}", std::ldexp(3.0, 0));
}
```

```text title="実行結果"
ldexp(1.5, 3)  = 12
ldexp(1.0, -2) = 0.25
ldexp(3.0, 0)  = 3
```

## ゲームでの使いどころ

固定小数点の値を浮動小数点数に直すときに使います。たとえば 16 ビットの小数部を持つ固定小数点数 `fixed` は、`std::ldexp(fixed, -16)` で実数になります。

```cpp
// 小数部 8 ビットの固定小数点（整数値）を実数に変換
const float real = std::ldexp(static_cast<float>(fixed), -8);
```

## よくあるミス

??? failure "`exp` に浮動小数点数を渡して、切り捨てられる"
    `exp` は `int` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`frexp`](frexp.md) | 仮数と指数に分ける（逆の操作） |
| [`scalbn`](scalbn.md) | 2 の累乗を掛ける（基数に依存） |
| [`exp2`](exp2.md) | 2 の `x` 乗 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ldexp(x, n)` は `x * 2^n`
    - [x] 指数部をずらすだけで誤差が出ない
    - [x] 固定小数点数の変換などに

## 関連ページ

- [`std::frexp`](frexp.md)
- [cpprefjp: std::ldexp](https://cpprefjp.github.io/reference/cmath/ldexp.html)
- [cppreference: std::ldexp](https://en.cppreference.com/w/cpp/numeric/math/ldexp)

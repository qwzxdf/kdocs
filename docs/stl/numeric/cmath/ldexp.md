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

`std::ldexp(x, n)` は、**x に 2 の n 乗をかけた値**を返す関数です。浮動小数点数の指数部を直接操作するので、高速で正確です。`frexp` の逆です。

!!! tip "ポイント"
    - `ldexp(x, n)` は `x * 2^n`。
    - 丸めの誤差が出ない。
    - `frexp` で分解した値を戻す。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ldexp {#ldexp}

```cpp
double ldexp(double x, int n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 元の値 |
| `n` | `int` | 2 の指数 |

- 戻り値: `x × 2^n`
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::ldexp(1.5, 4));  // 1.5 × 16
}
```

```text title="実行結果"
24
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 浮動小数点の指数だけを操作する低レベルの処理 | `std::ldexp(m, e)` |

## よくあるミス

??? failure "通常のべき乗に使う"
    `pow(2, n)` や `1 << n` が分かりやすいです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`frexp`](frexp.md) | 仮数と指数に分ける |
| [`exp2`](exp2.md) | 2 の x 乗 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x × 2^n
    - [x] `frexp` の逆
    - [x] 指数部だけを操作

## 関連ページ

- [cpprefjp: std::ldexp](https://cpprefjp.github.io/reference/cmath/ldexp.html)
- [cppreference: std::ldexp](https://en.cppreference.com/w/cpp/numeric/math/ldexp)

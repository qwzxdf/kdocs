---
title: std::modf
summary: "小数を、整数部と小数部に分ける。"
order: 40
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::modf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::modf` は、**小数を整数部と小数部に分ける**関数です。小数部が戻り値で、整数部は引数のポインターに入ります。アニメーションの経過時間から「何周目か」と「周の途中」を分けるときに使えます。

!!! tip "ポイント"
    - 戻り値が小数部、整数部は第 2 引数。
    - 符号は両方とも元の値と同じ。
    - 小数部だけなら `x - std::floor(x)`（負の数で挙動が違う）。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::modf {#modf}

```cpp
double modf(double x, double* iptr);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 分ける値 |
| `iptr` | `double*` | 整数部の書き込み先 |

- 戻り値: 小数部
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  double ip = 0.0;
  double frac = std::modf(3.75, &ip);
  std::println("{} {}", ip, frac);
}
```

```text title="実行結果"
3 0.75
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 経過時間を「周回数」と「周の途中」に分ける | `std::modf(t / period, &laps)` |

## よくあるミス

??? failure "負の数で floor との違いを忘れる"
    `modf(-3.75)` の小数部は −0.75 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`floor`](floor.md) | 小さいほうへ切り捨て |
| [`trunc`](trunc.md) | 整数部 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数部と小数部に分ける
    - [x] 小数部が戻り値
    - [x] 符号は元と同じ

## 関連ページ

- [cpprefjp: std::modf](https://cpprefjp.github.io/reference/cmath/modf.html)
- [cppreference: std::modf](https://en.cppreference.com/w/cpp/numeric/math/modf)

---
title: std::ilogb
summary: "x の指数部（2 を底とした対数の整数部分）を int で返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::ilogb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

浮動小数点数は `仮数 × 2^指数` の形で持たれます。`ilogb(x)` は、その指数を整数で返します。正の数 x に対して `floor(log2(x))` と同じです。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ilogb {#ilogb}

```cpp
int ilogb(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 0 以外の有限の値 |

- 戻り値: 指数部（`int`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::ilogb(8.0), std::ilogb(10.0));
}
```

```text title="実行結果"
3 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 必要なビット数やミップマップの段数を求める |

## よくあるミス

??? failure "0 や NaN を渡す"
    特別な値（`FP_ILOGB0` など）が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logb`](logb.md) | 小数で返す版 |
| [`log2`](log2.md) | 対数そのもの |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x の指数部（2 を底とした対数の整数部分）を int で返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ilogb](https://cpprefjp.github.io/reference/cmath/ilogb.html)
- [cppreference: std::ilogb](https://en.cppreference.com/w/cpp/numeric/math/ilogb)

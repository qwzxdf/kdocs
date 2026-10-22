---
title: std::logb
summary: "x の指数部を、浮動小数点で返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::logb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`ilogb` と同じ値を、小数型で返します。無限大や 0 のときも、数学的に自然な値（±∞）を返します。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::logb {#logb}

```cpp
double logb(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 0 以外の有限の値 |

- 戻り値: 指数部（小数型）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::logb(8.0));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 2 のべき乗の桁の大きさを調べる |

## よくあるミス

??? failure "`log2` と取り違える"
    `logb` は指数部（整数値）を返します。`log2(10)` は 3.32… ですが、`logb(10)` は 3 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ilogb`](ilogb.md) | int で返す版 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x の指数部を、浮動小数点で返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::logb](https://cpprefjp.github.io/reference/cmath/logb.html)
- [cppreference: std::logb](https://en.cppreference.com/w/cpp/numeric/math/logb)

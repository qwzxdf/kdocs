---
title: std::legendre
summary: "ルジャンドル多項式を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::legendre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

球面上の計算や数値積分（ガウス求積）に登場する多項式です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::legendre {#legendre}

```cpp
double legendre(unsigned l, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `l` | unsigned | 次数 |
| `x` | 浮動小数点 | -1 〜 1 |

- 戻り値: `P_l(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::legendre(2, 0.5));
}
```

```text title="実行結果"
-0.125
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 球面調和関数による照明の近似 |

## よくあるミス

??? failure "範囲外を渡す"
    |x| > 1 では定義されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`assoc_legendre`](assoc_legendre.md) | 陪関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ルジャンドル多項式を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::legendre](https://cpprefjp.github.io/reference/cmath/legendre.html)
- [cppreference: std::legendre](https://en.cppreference.com/w/cpp/numeric/math/legendre)

---
title: std::assoc_legendre
summary: "ルジャンドル陪関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::assoc_legendre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

球面調和関数などに登場する特殊関数です。`assoc_legendre(l, m, x)` は、条件 m ≤ l、−1 ≤ x ≤ 1 で定義されます。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::assoc_legendre {#assoc_legendre}

```cpp
double assoc_legendre(unsigned l, unsigned m, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `l, m` | unsigned | 次数（m ≤ l） |
| `x` | 浮動小数点 | -1 〜 1 |

- 戻り値: `P_l^m(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::assoc_legendre(1, 1, 0.6));
}
```

```text title="実行結果"
0.8000
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 球面上の計算 |

## よくあるミス

??? failure "標準と他の定義の符号を取り違える"
    C++ の定義は、数学で使う (−1)^m の符号（Condon–Shortley 位相）を**含みません**。

## 類似

| 名前 | 違い |
| --- | --- |
| [`legendre`](legendre.md) | m = 0 の場合 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ルジャンドル陪関数を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::assoc_legendre](https://cpprefjp.github.io/reference/cmath/assoc_legendre.html)
- [cppreference: std::assoc_legendre](https://en.cppreference.com/w/cpp/numeric/math/assoc_legendre)

---
title: std::assoc_laguerre
summary: "ラゲール陪多項式を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::assoc_laguerre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

量子力学や数値解析の式に登場する、特殊関数の 1 つです。ゲームではほとんど使いません。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::assoc_laguerre {#assoc_laguerre}

```cpp
double assoc_laguerre(unsigned n, unsigned m, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n, m` | unsigned | 次数 |
| `x` | 浮動小数点 | x ≥ 0 |

- 戻り値: `L_n^m(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::assoc_laguerre(1, 1, 0.5));
}
```

```text title="実行結果"
1.5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 数値解析 |

## よくあるミス

??? failure "負の x を渡す"
    x は 0 以上です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`laguerre`](laguerre.md) | m = 0 の場合 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ラゲール陪多項式を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::assoc_laguerre](https://cpprefjp.github.io/reference/cmath/assoc_laguerre.html)
- [cppreference: std::assoc_laguerre](https://en.cppreference.com/w/cpp/numeric/math/assoc_laguerre)

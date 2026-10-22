---
title: std::riemann_zeta
summary: "リーマンのゼータ関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::riemann_zeta

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

数論や統計物理に登場する関数です。`riemann_zeta(2)` は `π²/6` です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::riemann_zeta {#riemann_zeta}

```cpp
double riemann_zeta(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: `ζ(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::riemann_zeta(2.0));
}
```

```text title="実行結果"
1.6449
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 数論の計算 |

## よくあるミス

??? failure "x = 1 を渡す"
    x = 1 で発散します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tgamma`](tgamma.md) | ガンマ関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] リーマンのゼータ関数を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::riemann_zeta](https://cpprefjp.github.io/reference/cmath/riemann_zeta.html)
- [cppreference: std::riemann_zeta](https://en.cppreference.com/w/cpp/numeric/math/riemann_zeta)

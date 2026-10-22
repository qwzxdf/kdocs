---
title: std::hermite
summary: "エルミート多項式を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::hermite

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

量子力学の調和振動子の解などに登場する多項式です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::hermite {#hermite}

```cpp
double hermite(unsigned n, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | unsigned | 次数 |
| `x` | 浮動小数点 | 値 |

- 戻り値: `H_n(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::hermite(2, 1.0));
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 確率論の展開式 |

## よくあるミス

??? failure "次数が大きすぎる"
    n が大きいと計算が不安定になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`laguerre`](laguerre.md) | ラゲール多項式 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] エルミート多項式を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::hermite](https://cpprefjp.github.io/reference/cmath/hermite.html)
- [cppreference: std::hermite](https://en.cppreference.com/w/cpp/numeric/math/hermite)

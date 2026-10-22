---
title: std::laguerre
summary: "ラゲール多項式を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::laguerre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

量子力学の水素原子の解などに登場する多項式です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::laguerre {#laguerre}

```cpp
double laguerre(unsigned n, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | unsigned | 次数 |
| `x` | 浮動小数点 | x ≥ 0 |

- 戻り値: `L_n(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::laguerre(2, 1.0));
}
```

```text title="実行結果"
-0.5
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
| [`assoc_laguerre`](assoc_laguerre.md) | 陪多項式 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ラゲール多項式を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::laguerre](https://cpprefjp.github.io/reference/cmath/laguerre.html)
- [cppreference: std::laguerre](https://en.cppreference.com/w/cpp/numeric/math/laguerre)

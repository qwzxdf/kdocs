---
title: std::cyl_neumann
summary: "ノイマン関数（第 2 種ベッセル関数）を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cyl_neumann

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

ベッセル関数の、もう 1 つの独立な解です。x = 0 で発散します。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cyl_neumann {#cyl_neumann}

```cpp
double cyl_neumann(double nu, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `nu` | 浮動小数点 | 次数（0 以上） |
| `x` | 浮動小数点 | 正の値 |

- 戻り値: `N_nu(x)`（`Y_nu(x)`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::cyl_neumann(0.0, 1.0));
}
```

```text title="実行結果"
0.0883
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 波動の解析 |

## よくあるミス

??? failure "0 を渡す"
    x = 0 では発散します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cyl_bessel_j`](cyl_bessel_j.md) | 第 1 種ベッセル関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ノイマン関数（第 2 種ベッセル関数）を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::cyl_neumann](https://cpprefjp.github.io/reference/cmath/cyl_neumann.html)
- [cppreference: std::cyl_neumann](https://en.cppreference.com/w/cpp/numeric/math/cyl_neumann)

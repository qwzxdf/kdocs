---
title: std::cyl_bessel_j
summary: "第 1 種ベッセル関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cyl_bessel_j

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

円形の膜の振動や、波の回折などの解に出てくる関数です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cyl_bessel_j {#cyl_bessel_j}

```cpp
double cyl_bessel_j(double nu, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `nu` | 浮動小数点 | 次数（0 以上） |
| `x` | 浮動小数点 | 0 以上 |

- 戻り値: `J_nu(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::cyl_bessel_j(0.0, 1.0));
}
```

```text title="実行結果"
0.7652
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 円形の振動の解析 |

## よくあるミス

??? failure "負の x を渡す"
    x は 0 以上です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cyl_neumann`](cyl_neumann.md) | 第 2 種ベッセル関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 第 1 種ベッセル関数を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::cyl_bessel_j](https://cpprefjp.github.io/reference/cmath/cyl_bessel_j.html)
- [cppreference: std::cyl_bessel_j](https://en.cppreference.com/w/cpp/numeric/math/cyl_bessel_j)

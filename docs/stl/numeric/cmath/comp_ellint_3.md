---
title: std::comp_ellint_3
summary: "第 3 種完全楕円積分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::comp_ellint_3

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

楕円積分のうち、パラメータ `nu` をもつ 3 番目の種類です。物理の式に登場します。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::comp_ellint_3 {#comp_ellint_3}

```cpp
double comp_ellint_3(double k, double nu);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `k` | 浮動小数点 | 離心率 −1 〜 1 |
| `nu` | 浮動小数点 | 特性数 |

- 戻り値: `Π(nu, k)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::comp_ellint_3(0.0, 0.0));
}
```

```text title="実行結果"
1.5708
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 物理の計算 |

## よくあるミス

??? failure "範囲外を渡す"
    |k| > 1 では定義されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`comp_ellint_1`](comp_ellint_1.md) | 第 1 種 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 第 3 種完全楕円積分を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::comp_ellint_3](https://cpprefjp.github.io/reference/cmath/comp_ellint_3.html)
- [cppreference: std::comp_ellint_3](https://en.cppreference.com/w/cpp/numeric/math/comp_ellint_3)

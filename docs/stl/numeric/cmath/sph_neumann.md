---
title: std::sph_neumann
summary: "球ノイマン関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sph_neumann

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

球ベッセル関数のもう 1 つの独立な解です。`sph_neumann(0, x)` は `-cos(x) / x` です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sph_neumann {#sph_neumann}

```cpp
double sph_neumann(unsigned n, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | unsigned | 次数 |
| `x` | 浮動小数点 | 正の値 |

- 戻り値: `n_n(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::sph_neumann(0, 1.0));
}
```

```text title="実行結果"
-0.5403
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 球状の波の解析 |

## よくあるミス

??? failure "0 を渡す"
    x = 0 では発散します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sph_bessel`](sph_bessel.md) | 球ベッセル関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 球ノイマン関数を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sph_neumann](https://cpprefjp.github.io/reference/cmath/sph_neumann.html)
- [cppreference: std::sph_neumann](https://en.cppreference.com/w/cpp/numeric/math/sph_neumann)

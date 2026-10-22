---
title: std::sph_bessel
summary: "球ベッセル関数（第 1 種）を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sph_bessel

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

球対称な波の解に出てくる関数です。`sph_bessel(0, x)` は `sin(x) / x` です。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sph_bessel {#sph_bessel}

```cpp
double sph_bessel(unsigned n, double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | unsigned | 次数 |
| `x` | 浮動小数点 | 0 以上 |

- 戻り値: `j_n(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::sph_bessel(0, 1.0));
}
```

```text title="実行結果"
0.8415
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 球状の波の解析 |

## よくあるミス

??? failure "負の x を渡す"
    x は 0 以上です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sph_neumann`](sph_neumann.md) | 球ノイマン関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 球ベッセル関数（第 1 種）を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sph_bessel](https://cpprefjp.github.io/reference/cmath/sph_bessel.html)
- [cppreference: std::sph_bessel](https://en.cppreference.com/w/cpp/numeric/math/sph_bessel)

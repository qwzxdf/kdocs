---
title: std::sph_legendre
summary: "球面調和関数の θ 部分を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sph_legendre

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

球面上の関数を展開する球面調和関数のうち、角度 θ に依存する部分を求めます。環境光の球面調和関数（SH）による近似の理屈に登場します。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sph_legendre {#sph_legendre}

```cpp
double sph_legendre(unsigned l, unsigned m, double theta);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `l, m` | unsigned | 次数（m ≤ l） |
| `theta` | 浮動小数点 | 角度（ラジアン） |

- 戻り値: 球面調和関数の θ 部分
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::sph_legendre(0, 0, 0.0));
}
```

```text title="実行結果"
0.2821
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 環境光の球面調和関数 |

## よくあるミス

??? failure "角度の単位を度にする"
    角度はラジアンです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`assoc_legendre`](assoc_legendre.md) | ルジャンドル陪関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 球面調和関数の θ 部分を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sph_legendre](https://cpprefjp.github.io/reference/cmath/sph_legendre.html)
- [cppreference: std::sph_legendre](https://en.cppreference.com/w/cpp/numeric/math/sph_legendre)

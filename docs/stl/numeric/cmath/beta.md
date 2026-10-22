---
title: std::beta
summary: "ベータ関数を求める。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::beta

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <cmath>`
</div>

`B(x, y) = Γ(x)Γ(y) / Γ(x+y)`。確率分布（ベータ分布）の係数に登場します。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::beta {#beta}

```cpp
double beta(double x, double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x, y` | 浮動小数点 | 正の値 |

- 戻り値: `B(x, y)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::beta(2.0, 3.0));
}
```

```text title="実行結果"
0.0833
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 確率分布の係数 |

## よくあるミス

??? failure "0 以下を渡す"
    引数は正の数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tgamma`](tgamma.md) | ガンマ関数 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ベータ関数を求める
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::beta](https://cpprefjp.github.io/reference/cmath/beta.html)
- [cppreference: std::beta](https://en.cppreference.com/w/cpp/numeric/math/beta)

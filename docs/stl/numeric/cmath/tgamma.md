---
title: std::tgamma
summary: "ガンマ関数（階乗の一般化）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::tgamma

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

整数 n のとき `tgamma(n)` は `(n-1)!` です。階乗を小数にまで広げた関数で、確率分布や組み合わせの計算に登場します。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::tgamma {#tgamma}

```cpp
double tgamma(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: `Γ(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::tgamma(5.0));
}
```

```text title="実行結果"
24
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 階乗を小数まで広げた計算 |

## よくあるミス

??? failure "`tgamma(n)` を n! と思う"
    `tgamma(n)` は `(n-1)!` です。5! を求めるなら `tgamma(6)` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lgamma`](lgamma.md) | ガンマ関数の対数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ガンマ関数（階乗の一般化）を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::tgamma](https://cpprefjp.github.io/reference/cmath/tgamma.html)
- [cppreference: std::tgamma](https://en.cppreference.com/w/cpp/numeric/math/tgamma)

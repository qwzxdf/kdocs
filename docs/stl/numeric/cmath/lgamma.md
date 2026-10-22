---
title: std::lgamma
summary: "ガンマ関数の自然対数を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::lgamma

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`tgamma(x)` は x が少し大きいだけで桁あふれします。そこで、その対数を直接計算する `lgamma` が使えます。大きな組み合わせの計算（二項係数など）で、対数のまま足し引きして最後に `exp` で戻します。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lgamma {#lgamma}

```cpp
double lgamma(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: `log(|Γ(x)|)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::lgamma(5.0));
}
```

```text title="実行結果"
3.1781
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 大きな組み合わせの数を桁あふれなしで扱う |

## よくあるミス

??? failure "`tgamma` を `log` する"
    桁あふれするので `lgamma` を直接使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`tgamma`](tgamma.md) | ガンマ関数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ガンマ関数の自然対数を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::lgamma](https://cpprefjp.github.io/reference/cmath/lgamma.html)
- [cppreference: std::lgamma](https://en.cppreference.com/w/cpp/numeric/math/lgamma)

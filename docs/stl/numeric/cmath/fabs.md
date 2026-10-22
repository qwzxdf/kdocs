---
title: std::fabs
summary: "浮動小数点の絶対値を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fabs

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::abs` は整数にも小数にも使えますが、小数だけを明示したいときは `fabs` が使えます。C 由来の名前で、C++ では `abs` と同じ働きです。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fabs {#fabs}

```cpp
double fabs(double x);  // float / long double 版もある
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 絶対値を求める値 |

- 戻り値: `|x|`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::fabs(-3.5));
}
```

```text title="実行結果"
3.5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 2 点の座標の差の大きさを調べる |

## よくあるミス

??? failure "整数に使って精度を失う"
    整数には `std::abs` を使います。`fabs` は `double` へ変換して計算します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`abs`](abs.md) | 整数にも使える |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点の絶対値を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fabs](https://cpprefjp.github.io/reference/cmath/fabs.html)
- [cppreference: std::fabs](https://en.cppreference.com/w/cpp/numeric/math/fabs)

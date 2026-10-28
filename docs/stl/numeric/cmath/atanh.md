---
title: std::atanh
summary: "双曲線逆正接（tanh の逆関数）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::atanh

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

双曲線関数 `sinh`・`cosh`・`tanh` の逆関数が逆双曲線関数です。`std::atanh` は、双曲線正接 `tanh` の逆関数です。値から元の引数を逆算したいときに使いますが、ゲームのコードで使う機会は多くありません。

!!! tip "ポイント"
    - `std::atanh(0.0)` は 0
    - 定義域は −1 〜 1。範囲外は NaN、±1 は ±∞
    - atanh(x) = log((1 + x) / (1 − x)) / 2
    - C++11 で追加

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::atanh {#atanh}

<span class="ver ver-11">C++11</span>

```cpp
float atanh(float x);
double atanh(double x);
long double atanh(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 入力 |

戻り値は、双曲線正接 `tanh` の逆関数です。数学的には `atanh(x) = log((1 + x) / (1 − x)) / 2` と書けます。

定義域を外れると NaN を返します。`errno` に `EDOM` が設定されることがあります。

標準の `log` を使って自分で書くこともできますが、`x` が 0 に近い場所や大きな場所で桁落ちしないよう、専用の関数のほうが精度よく計算されます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("atanh(0.0) = {}", std::atanh(0.0));
}
```

```text title="実行結果"
atanh(0.0) = 0
```

## ゲームでの使いどころ

ゲームで使う場面はほとんどありません。`tanh` で滑らかに頭打ちさせた値を元の値に戻したいときなどに登場します。

## よくあるミス

??? failure "定義域の外を渡して NaN になる"
    呼ぶ前に範囲を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sinh`](sinh.md) | 双曲線正弦 |
| [`cosh`](cosh.md) | 双曲線余弦 |
| [`tanh`](tanh.md) | 双曲線正接 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `atanh` は双曲線正接 `tanh` の逆関数
    - [x] 定義域は −1 〜 1。範囲外は NaN、±1 は ±∞
    - [x] 双曲線関数の逆

## 関連ページ

- [cpprefjp: std::atanh](https://cpprefjp.github.io/reference/cmath/atanh.html)
- [cppreference: std::atanh](https://en.cppreference.com/w/cpp/numeric/math/atanh)

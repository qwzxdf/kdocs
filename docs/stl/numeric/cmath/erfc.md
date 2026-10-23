---
title: std::erfc
summary: "相補誤差関数（1 − erf）を返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::erfc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

誤差関数 `erf(x)` は、`x` が大きいと 1 にとても近づきます。そこから 1 を引いて小さな値を求めると、桁落ちで精度が失われます。`std::erfc` は、<strong>`1 - erf(x)` を、`x` が大きくても精度を保って</strong>求めます。

!!! tip "ポイント"
    - `std::erfc(0.0)` は 1、`std::erfc(1.0)` は約 0.1573
    - `1 - erf(x)` と同じ値だが、`x` が大きいときの精度が違う
    - 値の範囲は 0 〜 2
    - 正規分布の裾の確率の計算に使う

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::erfc {#erfc}

<span class="ver ver-11">C++11</span>

```cpp
float erfc(float x);
double erfc(double x);
long double erfc(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 入力 |

戻り値は `1 - erf(x)` です。`x` が大きいほど 0 に近づき、`x` が負で大きいと 2 に近づきます。

`erf(5.0)` は `double` で 0.9999999999984626 のように 1 にごく近く、`1 - erf(5.0)` は有効桁が 3 桁ほどしか残りません。`erfc(5.0)` は内部で別の式を使うので、全桁の精度を保ちます。

標準正規分布で、`z` を超える値が出る確率（上側確率）は `0.5 * erfc(z / √2)` です。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("erfc(0) = {}", std::erfc(0.0));
  std::println("erfc(1) = {:.4f}", std::erfc(1.0));
}
```

```text title="実行結果"
erfc(0) = 1
erfc(1) = 0.1573
```

## ゲームでの使いどころ

正規分布の裾の確率（極端に珍しい出来事の確率）を求めるときに使います。ゲームでの出番はほとんどありません。

## よくあるミス

??? failure "大きな `x` で `1 - erf(x)` を使い、0 になる"
    `erfc` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`erf`](erf.md) | 誤差関数 |
| [`tgamma`](tgamma.md) | ガンマ関数 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `erfc(x)` は `1 - erf(x)` を桁落ちなく求める
    - [x] 範囲は 0 〜 2
    - [x] 正規分布の裾の確率に使う

## 関連ページ

- [cpprefjp: std::erfc](https://cpprefjp.github.io/reference/cmath/erfc.html)
- [cppreference: std::erfc](https://en.cppreference.com/w/cpp/numeric/math/erfc)

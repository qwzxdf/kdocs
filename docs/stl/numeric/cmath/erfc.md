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

`1 - erf(x)` を、桁落ちなしで計算します。x が大きいとき、`erf(x)` は 1 に近すぎて引き算で精度が落ちるので、`erfc` を使います。

!!! tip "ポイント"
    - `float` / `double` / `long double` の版がある。
    - 引数が整数なら `double` として計算される。
    - エラーは `errno` か浮動小数点例外で知らされる。

!!! info "このページを読む前に"
    [<cmath>](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::erfc {#erfc}

```cpp
double erfc(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 引数 |

- 戻り値: `1 - erf(x)`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{:.4f}", std::erfc(1.0));
}
```

```text title="実行結果"
0.1573
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 正規分布の裾の確率を求める |

## よくあるミス

??? failure "`1 - erf` で計算する"
    x が大きいと桁落ちします。`erfc` を直接使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`erf`](erf.md) | 誤差関数 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 相補誤差関数（1 − erf）を返す
    - [x] `float` / `double` / `long double` の版がある
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::erfc](https://cpprefjp.github.io/reference/cmath/erfc.html)
- [cppreference: std::erfc](https://en.cppreference.com/w/cpp/numeric/math/erfc)

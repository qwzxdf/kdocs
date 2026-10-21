---
title: std::log
summary: "自然対数（底が e の対数）を求める。"
order: 18
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::log

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

`std::log` は、**自然対数（e を底とする対数）**を返す関数です。`exp` の逆関数です。0 以下の値を渡すと NaN か無限大になります。レベルが上がるごとの経験値の増え方、音量（デシベル）の計算などに使います。

!!! tip "ポイント"
    - 底が 2 は `log2`、底が 10 は `log10`。
    - 0 以下は NaN または −∞。
    - べき乗の指数を求めたいときに使う。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::log {#log}

```cpp
float log(float x);
```

- 自然対数（e を底）。0 以下を渡すと -inf や NaN

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  std::println("{:.1f} {:.1f}", std::log(1.0), std::log(std::numbers::e));
}
```

```text title="実行結果"
0.0 1.0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 音量のデシベル換算 | `20 * std::log10(amplitude)` |

## よくあるミス

??? failure "0 以下の値を渡す"
    結果が NaN か −∞ です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log2`](log2.md) | 底が 2 |
| [`log10`](log10.md) | 底が 10 |
| [`exp`](exp.md) | 逆関数 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自然対数
    - [x] 0 以下は NaN
    - [x] 逆関数は exp

## 関連ページ

- [cpprefjp: std::log](https://cpprefjp.github.io/reference/cmath/log.html)
- [cppreference: std::log](https://en.cppreference.com/w/cpp/numeric/math/log)

---
title: std::log10
summary: "底が 10 の対数を求める。"
order: 20
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::log10

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::log10` は、**底が 10 の対数**を返す関数です。「10 を何回かけると x になるか」で、桁数や、デシベル（音量）の計算に使います。

!!! tip "ポイント"
    - `log10(1000)` は 3。
    - 桁数は `floor(log10(n)) + 1`。
    - デシベルは `20 * log10(振幅比)`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::log10 {#log10}

```cpp
float log10(float x);
```

- 10 を底とする対数。音量（デシベル）の計算に使います

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {}", std::log10(1000.0), std::log10(10.0));
}
```

```text title="実行結果"
3 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| スコアの桁数を調べる | `std::floor(std::log10(score)) + 1` |

## よくあるミス

??? failure "0 以下の値を渡す"
    NaN か −∞ です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log`](log.md) | 自然対数 |
| [`log2`](log2.md) | 底が 2 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 底が 10 の対数
    - [x] 桁数とデシベル
    - [x] 0 以下は NaN

## 関連ページ

- [cpprefjp: std::log10](https://cpprefjp.github.io/reference/cmath/log10.html)
- [cppreference: std::log10](https://en.cppreference.com/w/cpp/numeric/math/log10)

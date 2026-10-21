---
title: std::exp2
summary: "2 の x 乗を求める。"
order: 33
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::exp2

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::exp2` は、**2 の x 乗**を返す関数です。2 のべき乗の計算（ミップマップの大きさ、ビット数）に使います。`pow(2, x)` より正確で速いことがあります。

!!! tip "ポイント"
    - `exp2(10)` は 1024。
    - 整数のシフト `1 << n` のほうが速い場面もある。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exp2 {#exp2}

```cpp
double exp2(double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点 | 指数 |

- 戻り値: 2 の x 乗
- 計算量: O(1)

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{}", std::exp2(10.0));
}
```

```text title="実行結果"
1024
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ミップレベルごとの大きさ | `std::exp2(level)` |

## よくあるミス

??? failure "整数の 2 の累乗に使う"
    `1 << n`（整数のシフト）のほうが速くて正確です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`pow`](pow.md) | 一般のべき乗 |
| [`log2`](log2.md) | 逆関数 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 の x 乗
    - [x] `log2` の逆
    - [x] 整数なら `1 << n`

## 関連ページ

- [cpprefjp: std::exp2](https://cpprefjp.github.io/reference/cmath/exp2.html)
- [cppreference: std::exp2](https://en.cppreference.com/w/cpp/numeric/math/exp2)

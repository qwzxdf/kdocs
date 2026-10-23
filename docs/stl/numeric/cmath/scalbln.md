---
title: std::scalbln
summary: "x × 2ⁿ を計算する（指数が long）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::scalbln

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::scalbn` の、指数 `n` が `long` の版です。`int` に収まらない指数を渡す必要がある場面（めったにありません）のために用意されています。

!!! tip "ポイント"
    - `std::scalbln(1.0, 10L)` は 1024
    - `scalbn` との違いは、指数の型が `long`
    - 基数が 2 の環境では `ldexp` と同じ
    - 通常は `scalbn` で足りる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::scalbln {#scalbln}

<span class="ver ver-11">C++11</span>

```cpp
float scalbln(float x, long n);
double scalbln(double x, long n);
long double scalbln(long double x, long n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 元の値 |
| `n` | `long` | 指数 |

戻り値は `x × FLT_RADIX^n` です。`scalbn` と同じですが、指数の引数が `long` です。

`double` の指数部は 11 ビット程度なので、`int` で十分に足ります。`long` を受け取る必要が生じるのは、`long double` に 128 ビットの型を使うような特殊な環境だけです。結果が範囲を超えると、無限大や 0 になります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("scalbln(1.0, 10) = {}", std::scalbln(1.0, 10L));
}
```

```text title="実行結果"
scalbln(1.0, 10) = 1024
```

## ゲームでの使いどころ

`scalbn` で足ります。この関数を使う理由は、ほとんどありません。

## よくあるミス

??? failure "`scalbn` で足りるのに使う"
    `int` に収まる指数なら `scalbn` で足ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`scalbn`](scalbn.md) | 指数が `int` |
| [`ldexp`](ldexp.md) | 2 進数の環境向けの名前 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `scalbln(x, n)` は `x × 2ⁿ`（`n` は `long`）
    - [x] 通常は `scalbn` で足りる
    - [x] 誤差はない

## 関連ページ

- [cpprefjp: std::scalbln](https://cpprefjp.github.io/reference/cmath/scalbln.html)
- [cppreference: std::scalbln](https://en.cppreference.com/w/cpp/numeric/math/scalbn)

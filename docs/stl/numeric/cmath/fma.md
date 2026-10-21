---
title: std::fma
summary: "`x * y + z` を、丸めを 1 回だけで計算する。"
order: 22
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fma

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::fma(x, y, z)` は、**`x * y + z` を、途中で丸めずに 1 回だけ丸めて計算する**関数です（積和演算）。精度が高く、対応する CPU では 1 命令で速く動きます。ベクトルの内積、多項式の評価で使われます。

!!! tip "ポイント"
    - 精度が良い。CPU によっては速い。
    - 対応していない CPU では、ソフトウェアで計算するので遅い。
    - コンパイラが自動で `fma` に置き換えることもある。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fma {#fma}

```cpp
float fma(float a, float b, float c);
```

- `a * b + c` を 1 回の丸めで計算します（誤差が少ない）

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("{} {} {} {} {}", std::copysign(3.0f, -1.0f), std::log2(256.0f),
               std::log10(1000.0f), std::cbrt(-27.0f), std::fma(2.0f, 3.0f, 1.0f));
}
```

```text title="実行結果"
-3 8 3 -3 7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 多項式の評価（ホーナー法） | `r = std::fma(r, x, c)` |

## よくあるミス

??? failure "FMA 非対応の環境で遅くなる"
    速度が重要なら、測って確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lerp`](lerp.md) | 補間 |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] x * y + z を 1 回の丸めで
    - [x] 精度が良い
    - [x] 非対応 CPU では遅い

## 関連ページ

- [cpprefjp: std::fma](https://cpprefjp.github.io/reference/cmath/fma.html)
- [cppreference: std::fma](https://en.cppreference.com/w/cpp/numeric/math/fma)

---
title: std::isinf
summary: "値が無限大かを調べる。"
order: 24
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isinf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`std::isinf` は、**値が無限大（+∞ か −∞）か**を調べる関数です。0 で割ったときや、桁あふれしたときに無限大になります。

!!! tip "ポイント"
    - `1.0f / 0.0f` は +∞（浮動小数点では例外にならない）。
    - 有限かどうかをまとめて見るなら `isfinite`。

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isinf {#isinf}

```cpp
bool isinf(float x);
```

- 無限大か（1.0f / 0.0f など）

```cpp
#include <cmath>
#include <print>

int main() {
  float nan = std::sqrt(-1.0f);
  float inf = std::exp(1000.0f);
  std::println("{} {} {}", std::isnan(nan), nan == nan, std::isinf(inf));
  float velocity = 10.0f;
  velocity *= std::exp(-2.0f * 0.5f);  // 0.5 秒で減衰
  std::println("{:.2f} {:.2f}", velocity, std::log(std::exp(3.0f)));
}
```

```text title="実行結果"
true false true
3.68 3.00
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 割り算の結果が無限大になっていないか確認する | `assert(!std::isinf(v))` |

## よくあるミス

??? failure "整数の 0 除算と混同する"
    整数の 0 割りは未定義動作で、無限大にはなりません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isnan`](isnan.md) | NaN か |
| [`isfinite`](isfinite.md) | 有限か |

## コンパイラ対応

C++98 から使えます。`std::lerp` は C++20、`hypot` の 3 引数は C++17 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 無限大かを調べる
    - [x] 小数の 0 割りは無限大
    - [x] 整数の 0 割りは未定義

## 関連ページ

- [cpprefjp: std::isinf](https://cpprefjp.github.io/reference/cmath/isinf.html)
- [cppreference: std::isinf](https://en.cppreference.com/w/cpp/numeric/math/isinf)

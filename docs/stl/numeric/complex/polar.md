---
title: std::polar
summary: "大きさと角度から複素数を作る。"
order: 900
tags:
  - 数値
---

# std::polar

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

回転や波の計算では、「大きさ r と角度 θ」の形（極形式）で考えるほうが自然なことがあります。`std::polar(r, theta)` は、その極形式から `r·(cosθ + i·sinθ)` の複素数を作ります。

!!! tip "ポイント"
    - 引数は `std::complex<T>`。
    - ゲームでは 2D の回転や周期的な波の計算で登場する。
    - `float` / `double` / `long double` で使える。

!!! info "このページを読む前に"
    [`std::complex`](../complex.md) を先に読んでください。

## 関数の詳しい説明

### std::polar {#polar}

```cpp
template <class T> complex<T> polar(const T& rho, const T& theta = T());
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `rho` | T | 大きさ |
| `theta` | T | 角度（ラジアン） |

- 戻り値: 大きさと角度から複素数を作る結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <complex>
#include <numbers>
#include <print>

int main() {
  auto z = std::polar(2.0, std::numbers::pi / 2);
  std::println("{:.1f} {:.1f}", z.real(), z.imag());
}
```

```text title="実行結果"
0.0 2.0
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D の向きと回転 | `std::polar(z)` |

## よくあるミス

??? failure "float の変数に double を混ぜる"
    `complex<float>` に `double` の値を混ぜると型が合わずコンパイルエラーになります。型をそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::complex`](../complex.md) | 複素数の型 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 大きさと角度から複素数を作る
    - [x] std::complex の関数
    - [x] 2D の回転で使える

## 関連ページ

- [cpprefjp: std::polar](https://cpprefjp.github.io/reference/complex/polar.html)
- [cppreference: std::polar](https://en.cppreference.com/w/cpp/numeric/complex/polar)

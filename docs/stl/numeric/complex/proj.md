---
title: std::proj
summary: "複素数をリーマン球面への射影に直す（無限大の扱いをそろえる）。"
order: 900
tags:
  - 数値
---

# std::proj

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数に無限大が混ざると、`(inf, 1)` と `(inf, -1)` のように、同じ「無限遠点」でも表現が何通りもできます。`std::proj(z)` は、有限の値はそのまま、無限大を含むものを `(inf, ±0)` の 1 つの形にそろえます。

!!! tip "ポイント"
    - 引数は `std::complex<T>`。
    - ゲームでは 2D の回転や周期的な波の計算で登場する。
    - `float` / `double` / `long double` で使える。

!!! info "このページを読む前に"
    [`std::complex`](../complex.md) を先に読んでください。

## 関数の詳しい説明

### std::proj {#proj}

```cpp
template <class T> complex<T> proj(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | complex<T> | 対象の複素数 |

- 戻り値: 複素数をリーマン球面への射影に直す（無限大の扱いをそろえる）結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  auto p = std::proj(z);
  std::println("{} {}", p.real(), p.imag());
}
```

```text title="実行結果"
3 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D の向きと回転 | `std::proj(z)` |

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
    - [x] 複素数をリーマン球面への射影に直す（無限大の扱いをそろえる）
    - [x] std::complex の関数
    - [x] 2D の回転で使える

## 関連ページ

- [cpprefjp: std::proj](https://cpprefjp.github.io/reference/complex/proj.html)
- [cppreference: std::proj](https://en.cppreference.com/w/cpp/numeric/complex/proj)

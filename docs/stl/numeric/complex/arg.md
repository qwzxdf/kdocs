---
title: std::arg
summary: "複素数の偏角（実軸からの角度）をラジアンで返す。"
order: 900
tags:
  - 数値
---

# std::arg

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数を平面の点 `(実部, 虚部)` と見ると、原点からの向きが角度になります。`std::arg(z)` は、その角度（−π 〜 π）をラジアンで返し、`atan2(虚部, 実部)` と同じ値です。

!!! tip "ポイント"
    - 引数は `std::complex<T>`。
    - ゲームでは 2D の回転や周期的な波の計算で登場する。
    - `float` / `double` / `long double` で使える。

!!! info "このページを読む前に"
    [`std::complex`](../complex.md) を先に読んでください。

## 関数の詳しい説明

### std::arg {#arg}

```cpp
template <class T> T arg(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | complex<T> | 対象の複素数 |

- 戻り値: 複素数の偏角（実軸からの角度）をラジアンで返す結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  std::complex<double> z{1.0, 1.0};
  std::println("{:.4f}", std::arg(z));
}
```

```text title="実行結果"
0.7854
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D の向きと回転 | `std::arg(z)` |

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
    - [x] 複素数の偏角（実軸からの角度）をラジアンで返す
    - [x] std::complex の関数
    - [x] 2D の回転で使える

## 関連ページ

- [cpprefjp: std::arg](https://cpprefjp.github.io/reference/complex/arg.html)
- [cppreference: std::arg](https://en.cppreference.com/w/cpp/numeric/complex/arg)

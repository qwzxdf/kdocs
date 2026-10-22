---
title: std::conj
summary: "共役複素数（虚部の符号を反転したもの）を返す。"
order: 900
tags:
  - 数値
---

# std::conj

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数 `a + bi` の共役は `a - bi` です。2D の回転を打ち消したいとき（逆回転）や、複素数の割り算の計算に使います。

!!! tip "ポイント"
    - 引数は `std::complex<T>`。
    - ゲームでは 2D の回転や周期的な波の計算で登場する。
    - `float` / `double` / `long double` で使える。

!!! info "このページを読む前に"
    [`std::complex`](../complex.md) を先に読んでください。

## 関数の詳しい説明

### std::conj {#conj}

```cpp
template <class T> complex<T> conj(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | complex<T> | 対象の複素数 |

- 戻り値: 共役複素数（虚部の符号を反転したもの）を返す結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  auto c = std::conj(z);
  std::println("{} {}", c.real(), c.imag());
}
```

```text title="実行結果"
3 -4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D の向きと回転 | `std::conj(z)` |

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
    - [x] 共役複素数（虚部の符号を反転したもの）を返す
    - [x] std::complex の関数
    - [x] 2D の回転で使える

## 関連ページ

- [cpprefjp: std::conj](https://cpprefjp.github.io/reference/complex/conj.html)
- [cppreference: std::conj](https://en.cppreference.com/w/cpp/numeric/complex/conj)

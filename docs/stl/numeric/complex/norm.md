---
title: std::norm
summary: "複素数の大きさの 2 乗を返す。"
order: 900
tags:
  - 数値
---

# std::norm

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数の大きさ `|z|` は `sqrt(a² + b²)` ですが、比べるだけなら平方根は不要です。`std::norm(z)` は `a² + b²` を返し、`sqrt` を使わない分だけ速く計算できます。

!!! tip "ポイント"
    - 引数は `std::complex<T>`。
    - ゲームでは 2D の回転や周期的な波の計算で登場する。
    - `float` / `double` / `long double` で使える。

!!! info "このページを読む前に"
    [`std::complex`](../complex.md) を先に読んでください。

## 関数の詳しい説明

### std::norm {#norm}

```cpp
template <class T> T norm(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | complex<T> | 対象の複素数 |

- 戻り値: 複素数の大きさの 2 乗を返す結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  std::println("{} {}", std::norm(z), std::abs(z));
}
```

```text title="実行結果"
25 5
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D の向きと回転 | `std::norm(z)` |

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
    - [x] 複素数の大きさの 2 乗を返す
    - [x] std::complex の関数
    - [x] 2D の回転で使える

## 関連ページ

- [cpprefjp: std::norm](https://cpprefjp.github.io/reference/complex/norm.html)
- [cppreference: std::norm](https://en.cppreference.com/w/cpp/numeric/complex/norm)

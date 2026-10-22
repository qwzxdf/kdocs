---
title: std::imag
summary: "複素数の虚部を取り出す。"
order: 900
tags:
  - 数値
---

# std::imag

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数 `a + bi` の `b`（虚部）を取り出します。`z.imag()` と `std::imag(z)` の 2 通りがあります。2D の回転や波の計算で、実部と虚部を座標として使うときに便利です。

!!! tip "ポイント"
    - メンバ関数と同名の自由関数がある。
    - ゲームでは 2D の回転や周期的な波の計算で登場する。
    - `float` / `double` / `long double` で使える。

!!! info "このページを読む前に"
    [`std::complex`](../complex.md) を先に読んでください。

## 関数の詳しい説明

### std::imag {#imag}

```cpp
template <class T> constexpr T imag(const complex<T>& z);
constexpr T complex<T>::imag() const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | complex<T> | 対象の複素数 |

- 戻り値: 複素数の虚部を取り出す結果
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  std::complex<double> z{3.0, 4.0};
  std::println("{} {}", std::imag(z), z.imag());
}
```

```text title="実行結果"
4 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2D の向きと回転 | `std::imag(z)` |

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
    - [x] 複素数の虚部を取り出す
    - [x] std::complex の関数
    - [x] 2D の回転で使える

## 関連ページ

- [cpprefjp: std::imag](https://cpprefjp.github.io/reference/complex/imag.html)
- [cppreference: std::imag](https://en.cppreference.com/w/cpp/numeric/complex/imag)

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

複素数 a + bi の虚部の符号を反転した a − bi を、共役複素数と呼びます。複素数に共役を掛けると、虚数が消えて実数になるため、絶対値の 2 乗や、割り算の計算で使われます。`std::conj` は、その共役を返します。

!!! tip "ポイント"
    - `std::conj(z)` は虚部の符号を反転した複素数
    - `z * conj(z)` は実数（絶対値の 2 乗）
    - 回転の逆（逆回転）に使える
    - 実数に使うと複素数型で返る

!!! info "このページを読む前に"
    [`<complex>`](../complex.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::conj {#conj}

```cpp
template <class T>
complex<T> conj(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | `complex<T>` | 複素数 |

戻り値は `z` の共役複素数で、実部はそのまま、虚部の符号を反転します。`conj(3 + 4i)` は `3 − 4i` です。

2D の回転を単位複素数（絶対値が 1）で表している場合、その共役が逆回転になります。回転 `r` を適用した後に `conj(r)` を掛けると、元に戻ります。

実数を渡すと、虚部が 0 の `complex` 型の値として返ります（C++11 以降。型は `double` などの複素数型）。

## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  const std::complex<double> z{3.0, 4.0};
  const auto c = std::conj(z);
  std::println("real = {}, imag = {}", c.real(), c.imag());
  const auto p = z * c;                         // 実数になる（絶対値の 2 乗）
  std::println("z * conj(z) = {} + {}i", p.real(), p.imag());
}
```

```text title="実行結果"
real = 3, imag = -4
z * conj(z) = 25 + 0i
```

## ゲームでの使いどころ

2D の回転を複素数で表すとき、逆回転を作ります。

```cpp
std::complex<float> rotation = std::polar(1.0f, angle);
std::complex<float> inverse = std::conj(rotation);   // 逆の回転
```

## よくあるミス

??? failure "共役を掛けて絶対値の 2 乗を求めるのに `norm` を使わない"
    `std::norm(z)` のほうが速く短いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`norm`](norm.md) | 絶対値の 2 乗 |
| [`polar`](polar.md) | 極形式から作る |

## コンパイラ対応

C++98 から使えます。`<complex>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `conj(z)` は虚部の符号を反転する
    - [x] `z * conj(z)` は絶対値の 2 乗
    - [x] 回転の逆に使える

## 関連ページ

- [cpprefjp: std::conj](https://cpprefjp.github.io/reference/complex/conj.html)
- [cppreference: std::conj](https://en.cppreference.com/w/cpp/numeric/complex/conj)

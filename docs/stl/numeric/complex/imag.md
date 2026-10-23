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

複素数の 2 つの成分のうち、虚部（`i` の係数）を取り出すのが `std::imag` です。`std::real` と対になります。

!!! tip "ポイント"
    - `std::imag(z)` は複素数 `z` の虚部
    - メンバー関数 `z.imag()` と同じ
    - 実数に対しては 0 を返す
    - `std::real` は実部

!!! info "このページを読む前に"
    [`<complex>`](../complex.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::imag {#imag}

```cpp
template <class T>
constexpr T imag(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | `complex<T>` | 複素数 |

戻り値は `z` の虚部です。`std::complex<double>{3, 4}` なら 4 です。メンバー関数 `z.imag()` と同じです。

`complex` でない実数に使うと、0 を返します。実数は、虚部が 0 の複素数とみなせるからです。

## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  const std::complex<double> z{3.0, 4.0};
  std::println("imag(z)   = {}", std::imag(z));
  std::println("imag(2.0) = {}", std::imag(2.0));   // 実数の虚部は 0
}
```

```text title="実行結果"
imag(z)   = 4
imag(2.0) = 0
```

## ゲームでの使いどころ

複素数で 2D の位置を持つとき、y 座標を取り出します。

```cpp
const float py = std::imag(position);
```

## よくあるミス

??? failure "実数に使って 0 が返ることに驚く"
    実数の虚部は 0 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`real`](real.md) | 実部 |
| [`conj`](conj.md) | 共役複素数 |

## コンパイラ対応

C++98 から使えます。`<complex>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `imag(z)` は虚部
    - [x] 実数の虚部は 0
    - [x] 実部は `real`

## 関連ページ

- [cpprefjp: std::imag](https://cpprefjp.github.io/reference/complex/imag.html)
- [cppreference: std::imag](https://en.cppreference.com/w/cpp/numeric/complex/imag)

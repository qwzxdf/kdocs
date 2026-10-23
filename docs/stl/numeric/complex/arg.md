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

複素数を平面上の点と見たとき、原点から見た向きの角度が偏角です。2D の位置ベクトルから向きの角度を求めるのと同じ計算で、`std::atan2(imag, real)` に相当します。`std::arg` は、その偏角を返します。

!!! tip "ポイント"
    - `std::arg(z)` は偏角（ラジアン、−π 〜 π）
    - `atan2(imag, real)` と同じ
    - 正の実軸が 0、虚軸の正の側が π/2
    - 大きさは `abs`

!!! info "このページを読む前に"
    [`<complex>`](../complex.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::arg {#arg}

```cpp
template <class T>
constexpr T arg(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | `complex<T>` | 複素数 |

戻り値は、実軸の正の方向から測った `z` の角度で、単位はラジアン、範囲は −π 〜 +π です。`arg(1 + 0i)` は 0、`arg(0 + 1i)` は π/2、`arg(−1 + 0i)` は π です。

内部では `atan2(imag, real)` を計算しているので、象限を正しく区別できます。`z` が 0 のときは 0 を返します。

大きさと偏角を組み合わせて、`std::polar` で元の複素数に戻せます。

## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  std::println("arg(1)  = {}", std::arg(std::complex<double>{1.0, 0.0}));
  std::println("arg(i)  = {}", std::arg(std::complex<double>{0.0, 1.0}));
  std::println("arg(-1) = {}", std::arg(std::complex<double>{-1.0, 0.0}));
}
```

```text title="実行結果"
arg(1)  = 0
arg(i)  = 1.5707963267948966
arg(-1) = 3.141592653589793
```

## ゲームでの使いどころ

2D の位置を複素数で持つ実装で、向きの角度を求めます。

```cpp
const float heading = std::arg(target - position);   // 目標に向かう角度
```

## よくあるミス

??? failure "度とラジアンを取り違える"
    戻り値はラジアンです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`polar`](polar.md) | 大きさと偏角から作る |
| [`atan2`](../cmath/atan2.md) | 実数で角度を求める |

## コンパイラ対応

C++98 から使えます。`<complex>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `arg(z)` は偏角（ラジアン、−π 〜 π）
    - [x] `atan2(imag, real)` と同じ
    - [x] `polar` で元に戻せる

## 関連ページ

- [cpprefjp: std::arg](https://cpprefjp.github.io/reference/complex/arg.html)
- [cppreference: std::arg](https://en.cppreference.com/w/cpp/numeric/complex/arg)

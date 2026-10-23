---
title: std::real
summary: "複素数の実部を取り出す。"
order: 900
tags:
  - 数値
---

# std::real

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <complex>`
</div>

複素数は、実部と虚部の 2 つの値の組です。2D の回転や、波の計算で、複素数をそのまま使うと、式が短くなることがあります。`std::real` は、その<strong>実部を取り出します</strong>。

!!! tip "ポイント"
    - `std::real(z)` は複素数 `z` の実部
    - メンバー関数 `z.real()` と同じ
    - 値を読むだけでなく、`z.real(新しい値)` で設定もできる
    - `std::imag` は虚部

!!! info "このページを読む前に"
    [`<complex>`](../complex.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::real {#real}

```cpp
template <class T>
constexpr T real(const complex<T>& z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `z` | `complex<T>` | 複素数 |

戻り値は `z` の実部です。`std::complex<double>{3, 4}` なら 3 です。メンバー関数 `z.real()` と同じ働きで、どちらを使っても構いません。

`std::real(x)` は、`complex` でない実数（`double` など）にも使えて、その値自体を返します。実数と複素数を同じテンプレートで扱うときに便利です。

## 実際に動かしてみる

```cpp
#include <complex>
#include <print>

int main() {
  const std::complex<double> z{3.0, 4.0};
  std::println("real = {}", std::real(z));
  std::println("imag = {}", std::imag(z));
}
```

```text title="実行結果"
real = 3
imag = 4
```

## ゲームでの使いどころ

複素数の実部だけを取り出して使うときに使います。2D の位置を複素数で持つ実装では、実部が x 座標、虚部が y 座標です。

```cpp
std::complex<float> position{x, y};
const float px = std::real(position);
```

## よくあるミス

??? failure "`complex<float>` と `double` を混ぜて、型が合わない"
    型をそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`imag`](imag.md) | 虚部 |
| [`norm`](norm.md) | 絶対値の 2 乗 |
| [`arg`](arg.md) | 偏角 |

## コンパイラ対応

C++98 から使えます。`<complex>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `real(z)` は複素数の実部
    - [x] メンバーの `z.real()` と同じ
    - [x] 虚部は `imag`

## 関連ページ

- [cpprefjp: std::real](https://cpprefjp.github.io/reference/complex/real.html)
- [cppreference: std::real](https://en.cppreference.com/w/cpp/numeric/complex/real)

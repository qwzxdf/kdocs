---
title: std::midpoint
summary: "2 つの値の中間を、桁あふれなしで求める。"
order: 3
group: <numeric> の整数・補間関数
tags:
  - 数値
---

# std::midpoint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <numeric>`
</div>

2 つの値の中間を `(a + b) / 2` で求めると、`a + b` が型の範囲を超えて桁あふれすることがあります。二分探索の中央を求めるコードがこの桁あふれで長年バグを抱えていたことは、有名な話です。

`std::midpoint` は、<strong>桁あふれしない中間値</strong>を返します。整数、浮動小数点数、ポインタに使えます。

!!! tip "ポイント"
    - `std::midpoint(1, 4)` は 2（`a` に近いほうへ丸める）
    - `midpoint(4, 1)` は 3。丸めの向きは第 1 引数に寄る
    - `a + b` が桁あふれする値でも、安全
    - 浮動小数点数やポインタにも使える

!!! info "このページを読む前に"
    [`<numeric>`](numeric.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::midpoint {#midpoint}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr T midpoint(T a, T b) noexcept;   // 整数・浮動小数点数
template <class T>
constexpr T* midpoint(T* a, T* b);          // ポインタ
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a` | 算術型またはポインタ | 1 つ目の値 |
| `b` | `a` と同じ型 | 2 つ目の値 |

整数の場合、戻り値は `(a + b) / 2` を桁あふれなしで求めた値です。割り切れないときは、<strong>第 1 引数 `a` に近いほう</strong>へ丸めます。`midpoint(1, 4)` は 2.5 の手前の 2、`midpoint(4, 1)` は 2.5 の `a`（4）に近い 3 になります。引数の順序で結果が変わるのは、この規則のためです。

`(a + b) / 2` との違いは、`a + b` が型の範囲を超えるとき、桁あふれして負の値になることがあるかないかです。`midpoint` は内部で、型を広げる、または差を使うなどして、この問題を避けます。

浮動小数点数の場合は、`a` と `b` の中間を桁あふれや不要な丸め誤差なしで返します。ポインタの場合は、同じ配列の中の 2 つのポインタの中間を返します。

`std::lerp(a, b, 0.5)` と似ていますが、`lerp` は補間専用の関数で、`midpoint` は中点専用です。

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>

int main() {
  std::println("midpoint(1, 4)    = {}", std::midpoint(1, 4));       // 2.5 → a に近い 2
  std::println("midpoint(4, 1)    = {}", std::midpoint(4, 1));       // 2.5 → a に近い 3
  std::println("midpoint(1.0, 2.0) = {}", std::midpoint(1.0, 2.0));

  // 桁あふれしやすい値でも安全
  const int big = 2'000'000'000;
  std::println("midpoint(big, big - 2) = {}", std::midpoint(big, big - 2));
}
```

```text title="実行結果"
midpoint(1, 4)    = 2
midpoint(4, 1)    = 3
midpoint(1.0, 2.0) = 1.5
midpoint(big, big - 2) = 1999999999
```

## ゲームでの使いどころ

二分探索の中央を求めるときの定番です。

```cpp
// lo と hi の中間。lo + hi が int を超えても安全
const std::size_t mid = std::midpoint(lo, hi);
```

2 点の中心位置を求めるときにも使えます。浮動小数点数なら `(a + b) / 2` で足りますが、桁あふれの心配がある整数のときに効果があります。

## よくあるミス

??? failure "`(lo + hi) / 2` で桁あふれする"
    `std::midpoint(lo, hi)` を使います。

??? failure "丸めの向きを知らず、引数を入れ替えて結果が変わって驚く"
    割り切れない場合は、第 1 引数に近いほうへ丸めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lerp`](cmath/lerp.md) | 補間。係数を指定できる |
| [`gcd`](gcd.md) | 最大公約数 |

## コンパイラ対応

C++20 から使えます。GCC 9 以降、Clang 14 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `midpoint(a, b)` は桁あふれしない中間値
    - [x] 割り切れないときは `a` に近いほうへ丸める
    - [x] 二分探索の中央、2 点の中心に使う

## 関連ページ

- [cpprefjp: std::midpoint](https://cpprefjp.github.io/reference/numeric/midpoint.html)
- [cppreference: std::midpoint](https://en.cppreference.com/w/cpp/numeric/midpoint)

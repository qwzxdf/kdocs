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

`std::midpoint(a, b)` は、**2 つの値の中間**を返す関数です。整数では `(a + b) / 2` が桁あふれする場合でも、正しく計算します。ポインターにも使えます。

!!! tip "ポイント"
    - 整数では、**0 に近い側**へ丸める。
    - `a + (b - a) / 2` の書き方より安全。
    - 二分探索の中央の位置に使える。

!!! info "このページを読む前に"
    [`<numeric>`](numeric.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::midpoint {#midpoint}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
constexpr T midpoint(T a, T b) noexcept;  // 整数・浮動小数点
template <class T>
constexpr T* midpoint(T* a, T* b);        // ポインタ
```

- `a` と `b` の真ん中。`(a + b) / 2` は大きい整数どうしだと足し算であふれますが、midpoint はあふれません。整数のときは `a` 寄りに丸めます

```cpp
#include <climits>
#include <numeric>
#include <print>

int main() {
  int a = INT_MAX - 2;
  int b = INT_MAX;
  std::println("{}", std::midpoint(a, b) == INT_MAX - 1);
  std::println("{} {}", std::midpoint(1, 4), std::midpoint(4, 1));
}
```

```text title="実行結果"
true
2 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 二分探索の中央の添字 | `std::midpoint(lo, hi)` |

## よくあるミス

??? failure "整数の丸めの向き"
    `midpoint(1, 2)` は 1（a に近い側）です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lerp`](cmath/lerp.md) | 割合で補間 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 中間を桁あふれなしで
    - [x] 整数は a に近い側へ丸める
    - [x] C++20

## 関連ページ

- [cpprefjp: std::midpoint](https://cpprefjp.github.io/reference/numeric/midpoint.html)
- [cppreference: std::midpoint](https://en.cppreference.com/w/cpp/numeric/midpoint)

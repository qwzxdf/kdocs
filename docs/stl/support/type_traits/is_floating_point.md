---
title: std::is_floating_point
summary: "小数型（float・double・long double）かを調べる。"
order: 3
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_floating_point

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <type_traits>`
</div>

数値を受け取るテンプレートで、整数と小数で処理を分けたい。`std::is_floating_point` は、<strong>型が浮動小数点型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_floating_point_v<T>` は、`T` が浮動小数点型（`float`、`double`、`long double`）か
    - `float`・`double`・`long double` と、`const` / `volatile` 付きが `true`
    - `std::is_floating_point<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `int` や `bool` は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_floating_point_v {#is_floating_point}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_floating_point_v = is_floating_point<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`float`・`double`・`long double` が `true` です。`const` や `volatile` が付いていても `true` です。C++23 の `std::float16_t` などの拡張浮動小数点型も `true` になります。`int` や `bool` は `false` です。DirectXMath の `HALF` は、実体が `uint16_t` なので `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("float                      -> {}", std::is_floating_point_v<float>);
  std::println("double                     -> {}", std::is_floating_point_v<double>);
  std::println("int                        -> {}", std::is_floating_point_v<int>);
  std::println("float*                     -> {}", std::is_floating_point_v<float*>);
}
```

```text title="実行結果"
float                      -> true
double                     -> true
int                        -> false
float*                     -> false
```

## ゲームでの使いどころ

浮動小数点数は誤差を許して比べ、整数は完全に一致で比べる、汎用の比較関数を書けます。

```cpp
template <class T>
bool NearlyEqual(T a, T b) {
  if constexpr (std::is_floating_point_v<T>) {
    return std::abs(a - b) <= std::numeric_limits<T>::epsilon() * 8 * std::max({T(1), std::abs(a), std::abs(b)});
  } else {
    return a == b;
  }
}
```

## よくあるミス

??? failure "HALF を浮動小数点型だと思う"
    DirectXMath の `HALF` は `uint16_t` の別名なので、`false` です。

??? failure "整数にも true を期待する"
    `int` や `bool` は `false` です。整数型は `is_integral` で調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_integral`](is_integral.md) | 整数型か |
| [`is_arithmetic`](is_arithmetic.md) | 整数型か浮動小数点型か |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_floating_point_v<T>` は、`T` が浮動小数点型（`float`、`double`、`long double`）か
    - [x] 浮動小数点型なら `true`
    - [x] 整数は `is_integral` で調べる

## 関連ページ

- [cpprefjp: std::is_floating_point](https://cpprefjp.github.io/reference/type_traits/is_floating_point.html)
- [cppreference: std::is_floating_point](https://en.cppreference.com/w/cpp/types/is_floating_point)

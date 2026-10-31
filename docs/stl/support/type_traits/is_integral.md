---
title: std::is_integral
summary: "整数型かを調べる。"
order: 2
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_integral

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
`#include <type_traits>`
</div>

整数だけを受け取るテンプレート関数を書きたい。`int`、`unsigned`、`char`、`bool` などはすべて整数型です。`std::is_integral` は、<strong>型が整数型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_integral_v<T>` は、`T` が整数型（`bool`、`char` 系、`int` 系）か
    - `bool` と `char` 系も整数型
    - `std::is_integral<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 列挙型は整数型ではない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_integral_v {#is_integral}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_integral_v = is_integral<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`bool`・`char` 系（`char8_t` などを含む）・`short`・`int`・`long`・`long long` と、それらの符号なしの型が `true` です。`bool` も整数型なので `true` です。列挙型と浮動小数点型は `false` です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("int                        -> {}", std::is_integral_v<int>);
  std::println("bool                       -> {}", std::is_integral_v<bool>);
  std::println("char                       -> {}", std::is_integral_v<char>);
  std::println("float                      -> {}", std::is_integral_v<float>);
  std::println("int*                       -> {}", std::is_integral_v<int*>);
}
```

```text title="実行結果"
int                        -> true
bool                       -> true
char                       -> true
float                      -> false
int*                       -> false
```

## ゲームでの使いどころ

整数だけを受け取る、ビット演算やハッシュの関数を、制約で絞ります。

```cpp
template <class T>
  requires std::is_integral_v<T>
constexpr int PopCount(T value) {
  int count = 0;
  for (auto v = static_cast<std::make_unsigned_t<T>>(value); v != 0; v >>= 1) count += v & 1;
  return count;
}
```

## よくあるミス

??? failure "bool が false だと思う"
    `bool` は整数型なので `true` です。数としては使いたくないなら、`!std::is_same_v<T, bool>` を足します。

??? failure "列挙型が true だと思う"
    `enum` と `enum class` は `false` です。`std::to_underlying` で整数に直して調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_floating_point`](is_floating_point.md) | 浮動小数点型か |
| [`is_arithmetic`](is_arithmetic.md) | 整数型か浮動小数点型か |
| [`is_signed`](is_signed.md) | 符号つきか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_integral_v<T>` は、`T` が整数型（`bool`、`char` 系、`int` 系）か
    - [x] `bool`・`char` 系・整数型が `true`
    - [x] 列挙型は `false`

## 関連ページ

- [cpprefjp: std::is_integral](https://cpprefjp.github.io/reference/type_traits/is_integral.html)
- [cppreference: std::is_integral](https://en.cppreference.com/w/cpp/types/is_integral)

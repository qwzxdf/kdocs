---
title: std::is_arithmetic
summary: "算術型（整数または小数）かを調べる。"
order: 4
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_arithmetic

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

数値として計算できる型だけを受け取りたい。`std::is_arithmetic` は、<strong>型が算術型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_arithmetic_v<T>` は、`T` が算術型（整数型または浮動小数点型）か
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_arithmetic<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_arithmetic_v {#is_arithmetic}

```cpp
template <class T>
inline constexpr bool is_arithmetic_v = is_arithmetic<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

整数型（`bool` と `char` を含む）と浮動小数点型が `true` です。ポインタ、列挙型、クラスは `false` です。

数値を受け取る関数テンプレートの制約として、C++20 の `concept` を使うなら `std::integral<T> || std::floating_point<T>` と書けます。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                        -> {}", std::is_arithmetic_v<int>);
  std::println("float                      -> {}", std::is_arithmetic_v<float>);
  std::println("bool                       -> {}", std::is_arithmetic_v<bool>);
  std::println("int*                       -> {}", std::is_arithmetic_v<int*>);
  std::println("Player                     -> {}", std::is_arithmetic_v<Player>);
}
```

```text title="実行結果"
int                        -> true
float                      -> true
bool                       -> true
int*                       -> false
Player                     -> false
```

## ゲームでの使いどころ

数値だけを受け取る関数に他の型が渡されたとき、読みやすいエラーを出します。

```cpp
template <class T>
T Clamp01(T value) {
  static_assert(std::is_arithmetic_v<T>, "数値型を渡してください");
  return value < T{0} ? T{0} : (value > T{1} ? T{1} : value);
}
```

## よくあるミス

??? failure "`T` に参照や `const` が付いていて、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "実行時の値に使おうとする"
    調べるのは型です。値の判定には通常の比較を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](../type_traits.md) | 型の性質を調べる道具の一覧 |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_arithmetic_v<T>` は、`T` が算術型（整数型または浮動小数点型）か
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_arithmetic](https://cpprefjp.github.io/reference/type_traits/is_arithmetic.html)
- [cppreference: std::is_arithmetic](https://en.cppreference.com/w/cpp/types/is_arithmetic)

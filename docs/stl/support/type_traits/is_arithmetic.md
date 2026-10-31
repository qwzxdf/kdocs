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
    - 整数型と浮動小数点型の合計
    - `std::is_arithmetic<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `bool` も `true`

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

整数型（`bool` と `char` 系を含む）と浮動小数点型が `true` です。ポインター、列挙型、クラスは `false` です。`is_integral` と `is_floating_point` のどちらかが `true` なら、`is_arithmetic` も `true` になります。

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

数値だけを受け取る関数に、数値でない型が渡されたとき、読みやすいエラーにします。

```cpp
template <class T>
T Clamp01(T value) {
  static_assert(std::is_arithmetic_v<T>, "数値型を渡してください");
  return value < T{0} ? T{0} : (value > T{1} ? T{1} : value);
}
```

## よくあるミス

??? failure "bool を数値型から除いたつもりになる"
    `bool` は整数型なので `true` です。除くなら、`!std::is_same_v<T, bool>` を足します。

??? failure "列挙型が true になると思う"
    列挙型は算術型ではありません。`std::to_underlying` で整数に直してから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_integral`](is_integral.md) | 整数型か |
| [`is_floating_point`](is_floating_point.md) | 浮動小数点型か |
| [`is_scalar`](is_scalar.md) | 列挙型やポインターも含むか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_arithmetic_v<T>` は、`T` が算術型（整数型または浮動小数点型）か
    - [x] 整数型か浮動小数点型なら `true`
    - [x] C++20 のコンセプトでは `std::integral` と `std::floating_point` が使える

## 関連ページ

- [cpprefjp: std::is_arithmetic](https://cpprefjp.github.io/reference/type_traits/is_arithmetic.html)
- [cppreference: std::is_arithmetic](https://en.cppreference.com/w/cpp/types/is_arithmetic)

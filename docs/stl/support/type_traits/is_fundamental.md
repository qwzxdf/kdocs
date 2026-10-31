---
title: std::is_fundamental
summary: "型が基本型（算術型・`void`・`nullptr_t`）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_fundamental

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

ユーザーが定義した型と、言語が元から持つ型を区別したい。`std::is_fundamental` は、<strong>型が基本型か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_fundamental_v<T>` は、`T` が基本型（算術型、`void`、`nullptr_t`）か
    - 算術型・`void`・`nullptr_t` が基本型
    - `std::is_fundamental<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - ポインターや列挙型は基本型ではない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_fundamental_v {#is_fundamental}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_fundamental_v = is_fundamental<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

言語に組み込まれた基本型が `true` です。算術型（整数と浮動小数点数、`bool`）、`void`、`std::nullptr_t` が含まれます。クラス、ポインター、配列、列挙型は、基本型ではありません。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                        -> {}", std::is_fundamental_v<int>);
  std::println("void                       -> {}", std::is_fundamental_v<void>);
  std::println("std::nullptr_t             -> {}", std::is_fundamental_v<std::nullptr_t>);
  std::println("Player                     -> {}", std::is_fundamental_v<Player>);
  std::println("int*                       -> {}", std::is_fundamental_v<int*>);
}
```

```text title="実行結果"
int                        -> true
void                       -> true
std::nullptr_t             -> true
Player                     -> false
int*                       -> false
```

## ゲームでの使いどころ

基本型は値渡し、それ以外は参照渡しにする、引数の型を選ぶ別名に使えます。

```cpp
template <class T>
using ParamType = std::conditional_t<std::is_fundamental_v<T>, T, const T&>;

template <class T>
void Show(ParamType<T> value);   // int は値渡し、std::string は const 参照
```

## よくあるミス

??? failure "ポインターを基本型だと思う"
    ポインターは基本型ではありません。`false` です。`is_scalar` なら `true` です。

??? failure "std::string を基本型だと思う"
    標準ライブラリの型は、すべてクラスなので `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_compound`](is_compound.md) | 基本型でないか。裏返し |
| [`is_arithmetic`](is_arithmetic.md) | 整数型か浮動小数点型か |
| [`is_scalar`](is_scalar.md) | ポインターや列挙型も含むか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_fundamental_v<T>` は、`T` が基本型（算術型、`void`、`nullptr_t`）か
    - [x] 算術型・`void`・`nullptr_t` が `true`
    - [x] ポインターや列挙型は `false`

## 関連ページ

- [cpprefjp: std::is_fundamental](https://cpprefjp.github.io/reference/type_traits/is_fundamental.html)
- [cppreference: std::is_fundamental](https://en.cppreference.com/w/cpp/types/is_fundamental)

---
title: std::is_scoped_enum
summary: "型がスコープ付き列挙型（`enum class`）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_scoped_enum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <type_traits>`
</div>

`enum` と `enum class` は、整数への暗黙の変換ができるかが違います。`std::is_scoped_enum` は、<strong>型が `enum class` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_scoped_enum_v<T>` は、`T` が `enum class`（スコープ付き列挙型）か
    - `enum class` だけが `true`（C++23）
    - `std::is_scoped_enum<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 旧式の `enum` は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_scoped_enum_v {#is_scoped_enum}

<span class="ver ver-23">C++23</span>

```cpp
template <class T>
inline constexpr bool is_scoped_enum_v = is_scoped_enum<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`enum class Color` のような、スコープつきの列挙型が `true` です。旧式の `enum` と、整数型は `false` です。C++23 で追加されました。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

enum class Color { kRed, kBlue };
enum Old { kOne };

int main() {
  std::println("Color                      -> {}", std::is_scoped_enum_v<Color>);
  std::println("Old                        -> {}", std::is_scoped_enum_v<Old>);
  std::println("int                        -> {}", std::is_scoped_enum_v<int>);
}
```

```text title="実行結果"
Color                      -> true
Old                        -> false
int                        -> false
```

## ゲームでの使いどころ

ビットフラグの演算子を、`enum class` だけに用意します。旧式の `enum` は、すでに整数として演算できるからです。

```cpp
template <class E>
  requires std::is_scoped_enum_v<E>
constexpr E operator|(E a, E b) {
  return static_cast<E>(std::to_underlying(a) | std::to_underlying(b));
}

enum class Layer : std::uint8_t { kGround = 1, kAir = 2 };
// auto both = Layer::kGround | Layer::kAir;
```

## よくあるミス

??? failure "C++20 以前で使う"
    C++23 で追加されました。それ以前は、`std::is_enum_v<E> && !std::is_convertible_v<E, std::underlying_type_t<E>>` で代用します。

??? failure "enum class が整数に暗黙に変わると思う"
    `enum class` は暗黙には整数に変わりません。`std::to_underlying` か `static_cast` で変換します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_enum`](is_enum.md) | 列挙型か。旧式も含む |
| [`underlying_type`](underlying_type.md) | 基になる整数の型 |
| [`is_convertible`](is_convertible.md) | 暗黙に変換できるか |

## コンパイラ対応

C++23 から使えます。新しい規格の機能なので、コンパイラの対応状況を確かめてください。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_scoped_enum_v<T>` は、`T` が `enum class`（スコープ付き列挙型）か
    - [x] `enum class` が `true`
    - [x] C++23 で追加された

## 関連ページ

- [cpprefjp: std::is_scoped_enum](https://cpprefjp.github.io/reference/type_traits/is_scoped_enum.html)
- [cppreference: std::is_scoped_enum](https://en.cppreference.com/w/cpp/types/is_scoped_enum)

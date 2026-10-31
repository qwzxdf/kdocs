---
title: std::is_scalar
summary: "型がスカラー型（算術型・列挙・ポインタなど）かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_scalar

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

クラスや配列でない、「1 つの値」を表す型かを調べたい。`std::is_scalar` は、<strong>型がスカラーか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_scalar_v<T>` は、`T` が算術型、列挙型、ポインタ、メンバーポインタ、`nullptr_t` のいずれかか
    - 算術型・列挙型・ポインター・`nullptr_t` が `true`
    - `std::is_scalar<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - クラスと配列は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_scalar_v {#is_scalar}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_scalar_v = is_scalar<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

算術型（整数・浮動小数点数・`bool`・`char` など）、列挙型、ポインター、メンバーへのポインター、`std::nullptr_t` が `true` です。クラス、配列、関数、参照は `false` です。「1 つの値として扱える」型の目安です。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

enum class Color { kRed, kBlue };
struct Player {
  int hp;
  float x;
};

int main() {
  std::println("int                        -> {}", std::is_scalar_v<int>);
  std::println("int*                       -> {}", std::is_scalar_v<int*>);
  std::println("Color                      -> {}", std::is_scalar_v<Color>);
  std::println("Player                     -> {}", std::is_scalar_v<Player>);
  std::println("int[3]                     -> {}", std::is_scalar_v<int[3]>);
}
```

```text title="実行結果"
int                        -> true
int*                       -> true
Color                      -> true
Player                     -> false
int[3]                     -> false
```

## ゲームでの使いどころ

1 つの値を保存する設定項目に、スカラー型だけを許します。

```cpp
template <class T>
class Setting {
  static_assert(std::is_scalar_v<T>, "設定値は、数値・列挙型・ポインターのいずれかにしてください");
  T value_;
};
```

## よくあるミス

??? failure "構造体を scalar だと思う"
    `struct Vec2 { float x, y; };` はクラスなので `false` です。

??? failure "配列を調べる"
    `int[3]` は配列なので `false` です。要素の型を `std::remove_extent_t` で取り出して調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_arithmetic`](is_arithmetic.md) | 数値型に絞った版 |
| [`is_fundamental`](is_fundamental.md) | `void` を含み、ポインターを含まない |
| [`is_object`](is_object.md) | より広く、クラスも含む |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_scalar_v<T>` は、`T` が算術型、列挙型、ポインタ、メンバーポインタ、`nullptr_t` のいずれかか
    - [x] 1 つの値で表せる型が `true`
    - [x] クラスや配列は `false`

## 関連ページ

- [cpprefjp: std::is_scalar](https://cpprefjp.github.io/reference/type_traits/is_scalar.html)
- [cppreference: std::is_scalar](https://en.cppreference.com/w/cpp/types/is_scalar)

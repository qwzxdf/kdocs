---
title: std::tuple_size
summary: "tuple や pair、array の要素数、各要素の型を、コンパイル時に調べる。"
order: 59
tags:
  - ユーティリティ
---

# std::tuple_size

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <tuple>`
</div>

`tuple` の要素数を、コンパイル時に知りたい。テンプレートの中で、`std::tuple_size<T>::value`（C++17 以降は `tuple_size_v<T>`）と書くと、`tuple`、`pair`、`std::array` の要素数が定数として得られます。構造化束縛や `std::apply` が、要素を数えるのに使っているのと同じ仕組みです。

!!! tip "ポイント"
    - `std::tuple_size_v<T>` は要素数。コンパイル時の定数
    - `tuple`、`pair`（常に 2）、`std::array<T, N>`（N）で使える
    - 自作の型にも、特殊化すれば構造化束縛に対応させられる
    - `const` や `volatile` が付いた型にも使える

!!! info "このページを読む前に"
    [`std::make_tuple`](make_tuple.md) を先に読んでください。

## 関数の詳しい説明

### std::tuple_size {#tuple_size}

<span class="ver ver-11">C++11</span>

```cpp
template <class T> struct tuple_size;
template <class T> inline constexpr std::size_t tuple_size_v = tuple_size<T>::value;
```

`tuple<A, B, C>` なら 3、`pair<A, B>` なら 2、`array<T, N>` なら N です。`tuple_size<const T>` は `tuple_size<T>` と同じです。

標準の型以外は、特殊化されていなければ、不完全型になり、使うとコンパイル エラーです。自作の型を構造化束縛に対応させるには、次の 3 つを用意します。

1. `std::tuple_size<MyType>` の特殊化（要素数）
2. `std::tuple_element<I, MyType>` の特殊化（各要素の型）
3. `get<I>(MyType&)` 関数（各要素の取り出し）

`std::tuple_element_t<I, T>` で、`I` 番目の要素の型が得られます。

## 実際に動かしてみる

```cpp
#include <array>
#include <print>
#include <tuple>
#include <utility>

int main() {
  static_assert(std::tuple_size_v<std::tuple<int, float, char>> == 3);
  static_assert(std::tuple_size_v<std::pair<int, int>> == 2);
  static_assert(std::tuple_size_v<std::array<int, 5>> == 5);

  using T = std::tuple<int, float, char>;
  static_assert(std::is_same_v<std::tuple_element_t<1, T>, float>);

  std::println("tuple: {}", std::tuple_size_v<T>);
  std::println("array: {}", std::tuple_size_v<std::array<int, 5>>);
}
```

```text title="実行結果"
tuple: 3
array: 5
```

## ゲームでの使いどころ

要素の数に応じて、コンパイル時にコードを生成する、テンプレートの処理（`tuple` の全要素を順に処理する、など）で使います。

## よくあるミス

??? failure "tuple_size を tuple の値に使う"
    `std::tuple_size_v` は型を受け取ります。`decltype(t)` を渡します。

??? failure "参照型の変数に直接使う"
    `decltype(t)` が参照になる場合、`std::remove_cvref_t` を通します。

## 類似

| 名前 | 違い |
| --- | --- |
| `std::tuple_element` | 各要素の型 |
| `std::array::size()` | `array` の実行時の要素数 |
| [`std::get`](get.md) | 要素を取り出す |

## コンパイラ対応

C++11 から使えます。`tuple_size_v` は C++17 から。

## 関連ページ

- [cpprefjp: std::tuple_size](https://cpprefjp.github.io/reference/tuple/tuple_size.html)
- [cppreference: std::tuple_size](https://en.cppreference.com/w/cpp/utility/tuple_size)

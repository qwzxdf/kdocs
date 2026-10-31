---
title: std::is_null_pointer
summary: "型が `std::nullptr_t` かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_null_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-14">C++14</span>
`#include <type_traits>`
</div>

`nullptr` は特別な型 `std::nullptr_t` を持ちます。ポインタ型とは別の型です。`std::is_null_pointer` は、<strong>型が `nullptr_t` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_null_pointer_v<T>` は、`T` が `std::nullptr_t` か
    - `nullptr` リテラルの型だけが `true`
    - `std::is_null_pointer<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `nullptr` を代入した `int*` の変数は `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_null_pointer_v {#is_null_pointer}

<span class="ver ver-14">C++14</span>

```cpp
template <class T>
inline constexpr bool is_null_pointer_v = is_null_pointer<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`T` が `std::nullptr_t`（`const` や `volatile` が付いた型も含む）なら `true` です。`int*` に `nullptr` を代入した変数の型は `int*` で、`nullptr_t` ではありません。`nullptr` というリテラル自体の型が `nullptr_t` です。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <type_traits>

int main() {
  std::println("std::nullptr_t             -> {}", std::is_null_pointer_v<std::nullptr_t>);
  std::println("int*                       -> {}", std::is_null_pointer_v<int*>);
  std::println("int                        -> {}", std::is_null_pointer_v<int>);
}
```

```text title="実行結果"
std::nullptr_t             -> true
int*                       -> false
int                        -> false
```

## ゲームでの使いどころ

`nullptr` が直接渡されたかを区別して、ポインターのリセットとして扱う関数を書けます。

```cpp
template <class T>
void SetTarget(T target) {
  if constexpr (std::is_null_pointer_v<T>) {
    target_ = nullptr;     // nullptr リテラルが渡された
  } else {
    target_ = target;
  }
}
```

## よくあるミス

??? failure "NULL を渡して true を期待する"
    `NULL` は整数（またはマクロ）で、`nullptr_t` ではありません。`false` です。

??? failure "nullptr を入れたポインター変数を調べる"
    変数の型は `int*` のままなので、`false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_pointer`](is_pointer.md) | ポインター型か |
| [`is_fundamental`](is_fundamental.md) | `nullptr_t` は基本型に含まれる |

## コンパイラ対応

C++14 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_null_pointer_v<T>` は、`T` が `std::nullptr_t` か
    - [x] `std::nullptr_t` だけが `true`
    - [x] `NULL` や `nullptr` を代入したポインターは `false`

## 関連ページ

- [cpprefjp: std::is_null_pointer](https://cpprefjp.github.io/reference/type_traits/is_null_pointer.html)
- [cppreference: std::is_null_pointer](https://en.cppreference.com/w/cpp/types/is_null_pointer)

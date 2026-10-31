---
title: std::is_pointer
summary: "ポインター型かを調べる。"
order: 7
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

スマート ポインタと生のポインタは別物です。ポインタを受け取るテンプレートで、生のポインタか確かめたい場面があります。`std::is_pointer` は、<strong>型がポインタか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_pointer_v<T>` は、`T` がポインタ型か
    - `const` や `volatile` が付いたポインターも `true`
    - `std::is_pointer<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - スマートポインターは `false`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_pointer_v {#is_pointer}

```cpp
template <class T>
inline constexpr bool is_pointer_v = is_pointer<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`int*`、`const char*`、`void*`、関数ポインターなどが `true` です。`const` や `volatile` が付いたポインター（`int* const`）も `true` です。`std::nullptr_t`、メンバーへのポインター、参照、`std::unique_ptr` などのスマートポインターは `false` です。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <memory>
#include <print>
#include <type_traits>

int main() {
  std::println("int*                       -> {}", std::is_pointer_v<int*>);
  std::println("const char*                -> {}", std::is_pointer_v<const char*>);
  std::println("std::nullptr_t             -> {}", std::is_pointer_v<std::nullptr_t>);
  std::println("std::unique_ptr<int>       -> {}", std::is_pointer_v<std::unique_ptr<int>>);
  std::println("int                        -> {}", std::is_pointer_v<int>);
}
```

```text title="実行結果"
int*                       -> true
const char*                -> true
std::nullptr_t             -> false
std::unique_ptr<int>       -> false
int                        -> false
```

## ゲームでの使いどころ

ポインターが渡されたら中身を、そうでなければ値そのものを表示する、汎用の出力関数を書けます。

```cpp
template <class T>
void Print(const T& value) {
  if constexpr (std::is_pointer_v<T>) {
    if (value != nullptr) std::println("{}", *value);   // ポインターは指す先を出す
  } else {
    std::println("{}", value);
  }
}
```

## よくあるミス

??? failure "スマートポインターが true になると思う"
    `std::unique_ptr` や `std::shared_ptr` は、クラスなので `false` です。

??? failure "参照を外さずに調べる"
    `int*&` のような参照型は、ポインターではなく参照なので `false` です。`std::remove_reference_t` で外してから調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_member_pointer`](is_member_pointer.md) | メンバーへのポインターか |
| [`is_null_pointer`](is_null_pointer.md) | `nullptr` の型か |
| [`remove_pointer`](remove_pointer.md) | ポインターを外した型 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_pointer_v<T>` は、`T` がポインタ型か
    - [x] 生のポインターが `true`
    - [x] スマートポインターや参照は `false`

## 関連ページ

- [cpprefjp: std::is_pointer](https://cpprefjp.github.io/reference/type_traits/is_pointer.html)
- [cppreference: std::is_pointer](https://en.cppreference.com/w/cpp/types/is_pointer)

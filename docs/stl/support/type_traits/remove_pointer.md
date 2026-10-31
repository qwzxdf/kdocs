---
title: std::remove_pointer
summary: "ポインタを取り除く。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

ポインタ型 `int*` から、指す先の型 `int` を取り出したい。`std::remove_pointer` は、<strong>ポインタを 1 段外した型</strong>を返します。

!!! tip "ポイント"
    - `std::remove_pointer_t<int*>` は `int`
    - 1 段だけ外す
    - ポインタでなければ、そのまま
    - スマート ポインタには効かない（`element_type` を使う）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_pointer_t {#remove_pointer}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using remove_pointer_t = typename remove_pointer<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int*` なら `int` を返します。ポインタでない型は、そのまま返します。ポインタのポインタ（`int**`）は、1 段だけ外して `int*` になります。

ポインタ自体に付いた `const`（`int* const`）も外れて、指す先の型 `int` になります。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::remove_pointer<T>::type` と書いても同じ型ですが、C++14 以降の `std::remove_pointer_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::remove_pointer_t<int*> は int : {}", std::is_same_v<std::remove_pointer_t<int*>, int>);
  std::println("std::remove_pointer_t<int**> は int* : {}", std::is_same_v<std::remove_pointer_t<int**>, int*>);
  std::println("std::remove_pointer_t<int> は int : {}", std::is_same_v<std::remove_pointer_t<int>, int>);
}
```

```text title="実行結果"
std::remove_pointer_t<int*> は int : true
std::remove_pointer_t<int**> は int* : true
std::remove_pointer_t<int> は int : true
```

## ゲームでの使いどころ

ポインター型から、指す先の型を取り出します。`int*` なら `int`、`const char*` なら `const char` です。ポインターを受け取るテンプレートで、指す先の型の変数を用意するときに使います。

```cpp
template <class P>
auto Dereference(P ptr) {
  using Pointee = std::remove_pointer_t<P>;   // int* なら int
  Pointee copy = *ptr;
  return copy;
}
```

## よくあるミス

??? failure "スマートポインターの指す先を取り出せると思う"
    `std::unique_ptr<T>` はクラスなので、そのまま返ります。指す先の型は `element_type` で取ります。

??? failure "二重ポインターが全部外れると思う"
    `int**` は 1 段だけ外れて `int*` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`add_pointer`](add_pointer.md) | ポインタを付ける |
| [`remove_reference`](remove_reference.md) | 参照を外す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::remove_pointer_t<int*>` は `int`
    - [x] 1 段だけ外す
    - [x] ポインタでなければ、そのまま

## 関連ページ

- [cpprefjp: std::remove_pointer](https://cpprefjp.github.io/reference/type_traits/remove_pointer.html)
- [cppreference: std::remove_pointer](https://en.cppreference.com/w/cpp/types/remove_pointer)

---
title: std::is_const
summary: "`const` が付いた型かを調べる。"
order: 9
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_const

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <type_traits>`
</div>

`const` の型かどうかで、書き込めるかを判断したい。`std::is_const` は、<strong>型そのものが `const` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_const_v<T>` は、`T` が `const` 修飾されているか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_const<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_const_v {#is_const}

```cpp
template <class T>
inline constexpr bool is_const_v = is_const<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`const int` は `true` です。ただし、`const int*`（`const int` を指すポインタ）は、ポインタ自体が `const` でないので `false` です。`int* const`（ポインタ自体が `const`）は `true` です。

参照は `const` を付けられないため、`const int&` も `false` になります。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("const int                  -> {}", std::is_const_v<const int>);
  std::println("int                        -> {}", std::is_const_v<int>);
  std::println("const int*                 -> {}", std::is_const_v<const int*>);
  std::println("int* const                 -> {}", std::is_const_v<int* const>);
}
```

```text title="実行結果"
const int                  -> true
int                        -> false
const int*                 -> false
int* const                 -> true
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_const_v<T>) {
    // T が条件に当てはまる型のときの処理
  } else {
    // それ以外の型の処理
  }
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
    - [x] `std::is_const_v<T>` は、`T` が `const` 修飾されているか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_const](https://cpprefjp.github.io/reference/type_traits/is_const.html)
- [cppreference: std::is_const](https://en.cppreference.com/w/cpp/types/is_const)

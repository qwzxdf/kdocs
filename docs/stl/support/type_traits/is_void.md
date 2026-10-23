---
title: std::is_void
summary: "型が `void` かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_void

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

関数の戻り値が `void` かどうかで処理を分けたい。テンプレートの中で、`void` だけが他の型と違う扱いを受ける場面は多くあります（値を返せない、変数を作れない）。`std::is_void` は、<strong>型が `void` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_void_v<T>` は、`T` が `void`（`const` や `volatile` 付きを含む）か
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_void<T>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_void_v {#is_void}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
inline constexpr bool is_void_v = is_void<T>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べたい型 |

`T` が `void`、`const void`、`volatile void`、`const volatile void` のいずれかなら `true` です。ポインタ `void*` は `void` ではないので `false` です。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("void                       -> {}", std::is_void_v<void>);
  std::println("const void                 -> {}", std::is_void_v<const void>);
  std::println("void*                      -> {}", std::is_void_v<void*>);
  std::println("int                        -> {}", std::is_void_v<int>);
}
```

```text title="実行結果"
void                       -> true
const void                 -> true
void*                      -> false
int                        -> false
```

## ゲームでの使いどころ

関数の戻り値の型で分岐する場面で使います。

```cpp
using R = std::invoke_result_t<F>;
if constexpr (std::is_void_v<R>) {
  f();            // 戻り値がないので、結果を受け取れない
} else {
  auto result = f();
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
    - [x] `std::is_void_v<T>` は、`T` が `void`（`const` や `volatile` 付きを含む）か
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_void](https://cpprefjp.github.io/reference/type_traits/is_void.html)
- [cppreference: std::is_void](https://en.cppreference.com/w/cpp/types/is_void)

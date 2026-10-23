---
title: std::is_nothrow_swappable_with
summary: "2 つの型の値を、例外を投げずに `swap` できるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_swappable_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

型の違う 2 つの値の入れ替えが、例外を投げないと保証できるかを知りたい。`std::is_nothrow_swappable_with<T, U>` は、<strong>入れ替えが `noexcept` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_swappable_with_v<T, U>` は、`T` と `U` の `swap` が例外を投げないか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_nothrow_swappable_with<T, U>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_swappable_with_v {#is_nothrow_swappable_with}

<span class="ver ver-17">C++17</span>

```cpp
template <class T, class U>
inline constexpr bool is_nothrow_swappable_with_v = is_nothrow_swappable_with<T, U>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 1 つ目の型（`T&` で渡す） |
| `U` | 型 | 2 つ目の型（`U&` で渡す） |

2 つの型の `swap` が書けて、どちらも `noexcept` なら `true` です。`T` と `U` は、通常 `T&` のように参照で渡します。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct MayThrow {
  MayThrow() = default;
  MayThrow(MayThrow&&) noexcept(false) {}
  MayThrow& operator=(MayThrow&&) noexcept(false) { return *this; }
};

int main() {
  std::println("int&, int&                         -> {}", std::is_nothrow_swappable_with_v<int&, int&>);
  std::println("MayThrow&, MayThrow&               -> {}", std::is_nothrow_swappable_with_v<MayThrow&, MayThrow&>);
}
```

```text title="実行結果"
int&, int&                         -> true
MayThrow&, MayThrow&               -> false
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_nothrow_swappable_with_v<T>) {
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

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_swappable_with_v<T, U>` は、`T` と `U` の `swap` が例外を投げないか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_nothrow_swappable_with](https://cpprefjp.github.io/reference/type_traits/is_nothrow_swappable_with.html)
- [cppreference: std::is_nothrow_swappable_with](https://en.cppreference.com/w/cpp/types/is_nothrow_swappable_with)

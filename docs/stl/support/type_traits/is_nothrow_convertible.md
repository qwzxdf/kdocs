---
title: std::is_nothrow_convertible
summary: "暗黙の変換が例外を投げないかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_convertible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

変換が失敗しない（例外を投げない）と保証できるかを知りたい。`std::is_nothrow_convertible<From, To>` は、<strong>暗黙の変換が `noexcept` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_convertible_v<From, To>` は、`From` から `To` への変換が例外を投げずにできるか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_nothrow_convertible<From, To>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_convertible_v {#is_nothrow_convertible}

<span class="ver ver-20">C++20</span>

```cpp
template <class From, class To>
inline constexpr bool is_nothrow_convertible_v = is_nothrow_convertible<From, To>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `From` | 型 | 変換元の型 |
| `To` | 型 | 変換先の型 |

`From` の値を `To` に暗黙に変換でき、しかもその変換が `noexcept` なら `true` です。`is_convertible` に、`noexcept` の条件を足したものです。

型の性質を調べるだけで、オブジェクトは作りません。テンプレートの中で、型によって処理を分ける（`if constexpr`）、使えない型を早い段階で弾く（`static_assert`、`concept`）、といった用途で使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Base {};
struct Derived : Base {};

int main() {
  std::println("int, float                         -> {}", std::is_nothrow_convertible_v<int, float>);
  std::println("const char*, std::string           -> {}", std::is_nothrow_convertible_v<const char*, std::string>);
  std::println("Derived*, Base*                    -> {}", std::is_nothrow_convertible_v<Derived*, Base*>);
}
```

```text title="実行結果"
int, float                         -> true
const char*, std::string           -> false
Derived*, Base*                    -> true
```

## ゲームでの使いどころ

型によって処理を切り替えるテンプレートで使います。

```cpp
template <class T>
void Process(const T& value) {
  if constexpr (std::is_nothrow_convertible_v<T>) {
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

C++20 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_convertible_v<From, To>` は、`From` から `To` への変換が例外を投げずにできるか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 参照や `const` が付いた型は、先に `remove_cvref_t` で外す

## 関連ページ

- [cpprefjp: std::is_nothrow_convertible](https://cpprefjp.github.io/reference/type_traits/is_nothrow_convertible.html)
- [cppreference: std::is_nothrow_convertible](https://en.cppreference.com/w/cpp/types/is_nothrow_convertible)

---
title: std::is_nothrow_assignable
summary: "例外を投げずに代入できる型の組かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_nothrow_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

代入が例外を投げないと保証できるかを知りたい。`std::is_nothrow_assignable<T, U>` は、<strong>代入が `noexcept` か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_nothrow_assignable_v<T, U>` は、`T` に `U` を代入するとき例外を投げないか
    - 代入の式に `noexcept` が付いているかを調べる
    - `std::is_nothrow_assignable<T, U>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - `T` は参照型（`T&`）で渡す

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_nothrow_assignable_v {#is_nothrow_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class U>
inline constexpr bool is_nothrow_assignable_v = is_nothrow_assignable<T, U>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 代入される側の型（`T&` で渡す） |
| `U` | 型 | 代入する値の型 |

`std::declval<T>() = std::declval<U>()` が書けて、その式が `noexcept` と宣言されているときだけ `true` です。`T` は代入される側の型で、普通は `T&` の形で渡します。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

struct Player {
  int hp;
  float x;
};

int main() {
  std::println("Player&, const Player&             -> {}", std::is_nothrow_assignable_v<Player&, const Player&>);
  std::println("int&, int                          -> {}", std::is_nothrow_assignable_v<int&, int>);
  std::println("std::string&, const std::string&   -> {}", std::is_nothrow_assignable_v<std::string&, const std::string&>);
}
```

```text title="実行結果"
Player&, const Player&             -> true
int&, int                          -> true
std::string&, const std::string&   -> false
```

## ゲームでの使いどころ

汎用のラッパーで、中の型の代入が例外を投げないときだけ、ラッパーの代入も `noexcept` にします。

```cpp
template <class T>
class Wrapper {
 public:
  Wrapper& operator=(const T& v) noexcept(std::is_nothrow_assignable_v<T&, const T&>) {
    value_ = v;
    return *this;
  }

 private:
  T value_;
};
```

## よくあるミス

??? failure "T を参照にしないで調べる"
    `int` への代入は、右辺値への代入になるので `false` です。`T&` の形で渡します。

??? failure "宣言の noexcept を実際の動きと同じだと思う"
    調べるのは宣言だけです。`noexcept` と書いた関数の中で例外が飛べば、`std::terminate` で終了します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_assignable`](is_assignable.md) | 例外を考えずに、代入できるかだけを調べる |
| [`is_nothrow_copy_assignable`](is_nothrow_copy_assignable.md) | 同じ型のコピー代入に絞った版 |
| [`is_nothrow_move_assignable`](is_nothrow_move_assignable.md) | 同じ型のムーブ代入に絞った版 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_assignable_v<T, U>` は、`T` に `U` を代入するとき例外を投げないか
    - [x] 代入式の `noexcept` を調べる
    - [x] `T` は `T&` の形で渡す

## 関連ページ

- [cpprefjp: std::is_nothrow_assignable](https://cpprefjp.github.io/reference/type_traits/is_nothrow_assignable.html)
- [cppreference: std::is_nothrow_assignable](https://en.cppreference.com/w/cpp/types/is_nothrow_assignable)

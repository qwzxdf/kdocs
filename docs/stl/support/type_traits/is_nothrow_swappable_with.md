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
    - `T` と `U` は、参照型（`T&`）で渡す
    - `std::is_nothrow_swappable_with<T, U>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 同じ型どうしなら `is_nothrow_swappable` が短い

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

2 つの型 `T` と `U` で、`swap(declval<T>(), declval<U>())` と `swap(declval<U>(), declval<T>())` の両方が書けて、どちらも `noexcept` なら `true` です。`T` と `U` は、通常 `T&` のように参照で渡します。

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

型の違う 2 つの変数を入れ替える関数の `noexcept` を、`swap` の性質に合わせます。

```cpp
template <class A, class B>
void Exchange(A& a, B& b) noexcept(std::is_nothrow_swappable_with_v<A&, B&>) {
  using std::swap;
  swap(a, b);
}
```

## よくあるミス

??? failure "参照を付けずに調べる"
    `int` と `int` では右辺値になり、`false` です。`int&` と `int&` の形で渡します。

??? failure "同じ型の入れ替えに使う"
    同じ型なら、`is_nothrow_swappable` のほうが短く書けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_nothrow_swappable`](is_nothrow_swappable.md) | 同じ型の入れ替え |
| [`is_swappable_with`](is_swappable_with.md) | 例外を考えずに、2 つの型を入れ替えられるか |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_nothrow_swappable_with_v<T, U>` は、`T` と `U` の `swap` が例外を投げないか
    - [x] 型の違う 2 つの `swap` の `noexcept` を調べる
    - [x] 参照型を渡す

## 関連ページ

- [cpprefjp: std::is_nothrow_swappable_with](https://cpprefjp.github.io/reference/type_traits/is_nothrow_swappable_with.html)
- [cppreference: std::is_nothrow_swappable_with](https://en.cppreference.com/w/cpp/types/is_nothrow_swappable_with)

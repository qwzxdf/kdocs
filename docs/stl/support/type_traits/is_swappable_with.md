---
title: std::is_swappable_with
summary: "2 つの型の値を、たがいに `swap` できるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_swappable_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <type_traits>`
</div>

型の違う 2 つの値を入れ替えられるかを調べたい。`std::is_swappable_with<T, U>` は、<strong>2 つの型の値を入れ替えられるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_swappable_with_v<T, U>` は、`T` と `U` の値を `swap` できるか
    - `T` と `U` は参照型で渡す
    - `std::is_swappable_with<T, U>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 標準では、型の違う入れ替えはほとんど用意されていない

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_swappable_with_v {#is_swappable_with}

<span class="ver ver-17">C++17</span>

```cpp
template <class T, class U>
inline constexpr bool is_swappable_with_v = is_swappable_with<T, U>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 1 つ目の型（`T&` で渡す） |
| `U` | 型 | 2 つ目の型（`U&` で渡す） |

`swap(declval<T>(), declval<U>())` と `swap(declval<U>(), declval<T>())` の両方が書けるなら `true` です。`T` と `U` は、通常 `T&` のように参照で渡します。型の違う 2 つの値を入れ替える仕組みを持つ型（代理オブジェクトなど）で意味を持ちます。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

int main() {
  std::println("int&, int&                         -> {}", std::is_swappable_with_v<int&, int&>);
  std::println("int&, float&                       -> {}", std::is_swappable_with_v<int&, float&>);
  std::println("std::string&, std::string&         -> {}", std::is_swappable_with_v<std::string&, std::string&>);
}
```

```text title="実行結果"
int&, int&                         -> true
int&, float&                       -> false
std::string&, std::string&         -> true
```

## ゲームでの使いどころ

型の違う 2 つを入れ替える関数に、前提を確かめる制約を付けます。

```cpp
template <class A, class B>
  requires std::is_swappable_with_v<A&, B&>
void Exchange(A& a, B& b) {
  using std::swap;
  swap(a, b);
}
```

## よくあるミス

??? failure "参照を付けずに調べる"
    `int` と `int` は右辺値になり、`false` です。`int&` と `int&` で渡します。

??? failure "異なる型が自動で入れ替わると思う"
    `int` と `double` を入れ替える `swap` は標準にありません。`false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_swappable`](is_swappable.md) | 同じ型の入れ替え |
| [`is_nothrow_swappable_with`](is_nothrow_swappable_with.md) | 例外を投げないかも調べる |

## コンパイラ対応

C++17 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_swappable_with_v<T, U>` は、`T` と `U` の値を `swap` できるか
    - [x] 2 つの型の `swap` が両方向で書けるかを調べる
    - [x] 同じ型なら `is_swappable` が短い

## 関連ページ

- [cpprefjp: std::is_swappable_with](https://cpprefjp.github.io/reference/type_traits/is_swappable_with.html)
- [cppreference: std::is_swappable_with](https://en.cppreference.com/w/cpp/types/is_swappable_with)

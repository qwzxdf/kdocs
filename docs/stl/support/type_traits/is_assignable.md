---
title: std::is_assignable
summary: "代入できる型の組かを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_assignable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`a = b` と書ける組み合わせかを事前に調べたい。`std::is_assignable<T, U>` は、<strong>T への U の代入が可能か</strong>を調べます。

!!! tip "ポイント"
    - `std::is_assignable_v<T, U>` は、`T` に `U` を代入できるか
    - `T` を `U` に代入できるか。`T` は参照型にして渡す
    - `std::is_assignable<T, U>::value` と書いても同じ（`_v` は C++17 の短縮形）
    - 同じ型どうしなら、`is_copy_assignable` などが短い

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_assignable_v {#is_assignable}

<span class="ver ver-11">C++11</span>

```cpp
template <class T, class U>
inline constexpr bool is_assignable_v = is_assignable<T, U>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 代入される側の型（`T&` で渡す） |
| `U` | 型 | 代入する値の型 |

`std::is_assignable_v<T, U>` は、`std::declval<T>() = std::declval<U>()` と書けるかを調べます。クラス型への代入は、左辺が左辺値でなくても書けてしまうので、普通は `T` を参照型（`Vec3&`）にして調べます。

`is_copy_assignable` と `is_move_assignable` は、この特殊なケースです。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <type_traits>

int main() {
  std::println("int&, int                          -> {}", std::is_assignable_v<int&, int>);
  std::println("int, int                           -> {}", std::is_assignable_v<int, int>);
  std::println("std::string&, const char*          -> {}", std::is_assignable_v<std::string&, const char*>);
}
```

```text title="実行結果"
int&, int                          -> true
int, int                           -> false
std::string&, const char*          -> true
```

## ゲームでの使いどころ

代入の前提を、早い段階で確かめる関数テンプレートに使います。

```cpp
template <class Dst, class Src>
void Assign(Dst& dst, const Src& src) {
  static_assert(std::is_assignable_v<Dst&, const Src&>, "代入できない組み合わせです");
  dst = src;
}
```

## よくあるミス

??? failure "T を参照にしないで調べる"
    `std::is_assignable_v<int, int>` は `false` です。`int` の右辺値には代入できないからです。`int&` にして調べます。

??? failure "変換できても代入できると思う"
    代入演算子が `explicit` なコンストラクターを経由しないなど、暗黙の変換ができない組み合わせは `false` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_copy_assignable`](is_copy_assignable.md) | 同じ型のコピー代入ができるか |
| [`is_nothrow_assignable`](is_nothrow_assignable.md) | 代入が例外を投げないか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_assignable_v<T, U>` は、`T` に `U` を代入できるか
    - [x] `is_assignable_v<T&, U>` の形で、`T` に参照を付ける
    - [x] 代入の式 `a = b` が書けるかを調べる

## 関連ページ

- [cpprefjp: std::is_assignable](https://cpprefjp.github.io/reference/type_traits/is_assignable.html)
- [cppreference: std::is_assignable](https://en.cppreference.com/w/cpp/types/is_assignable)

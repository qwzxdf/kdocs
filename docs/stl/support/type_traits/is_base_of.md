---
title: std::is_base_of
summary: "ある型が、別の型の基底クラスかを調べる。"
order: 8
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_base_of

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <type_traits>`
</div>

継承関係をコンパイル時に確かめたいことがあります。コンポーネントの登録時に、`Component` を継承した型だけを受け付けたい、といった場面です。`std::is_base_of<Base, Derived>` は、<strong>Base が Derived の基底クラスか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_base_of_v<A, B>` は、`A` が `B` の基底クラスか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_base_of<A, B>::value` と書いても同じ
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_base_of_v {#is_base_of}

```cpp
template <class A, class B>
inline constexpr bool is_base_of_v = is_base_of<A, B>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `A` | 型 | 1 つ目の型 |
| `B` | 型 | 2 つ目の型 |

`B` が `A` を（直接または間接に）継承していれば `true` です。同じクラス型どうしも `true` です。`private` 継承でも `true` になる点に注意します。クラスでない型（`int` など）は、常に `false` です。

型の関係を調べるだけで、オブジェクトは作りません。テンプレートの制約や、`static_assert` による型の確認に使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Base {};
struct Derived : Base {};

int main() {
  std::println("Base, Derived -> {}", std::is_base_of_v<Base, Derived>);
  std::println("Derived, Base -> {}", std::is_base_of_v<Derived, Base>);
  std::println("Base, Base -> {}", std::is_base_of_v<Base, Base>);
  std::println("Base, int -> {}", std::is_base_of_v<Base, int>);
}
```

```text title="実行結果"
Base, Derived -> true
Derived, Base -> false
Base, Base -> true
Base, int -> false
```

## ゲームでの使いどころ

テンプレートの引数どうしの関係を、コンパイル時に保証します。

```cpp
template <class D>
void Register(D& obj) {
  static_assert(std::is_base_of_v<Component, D>, "型の関係が合いません");
}
```

## よくあるミス

??? failure "引数の順序を取り違える"
    `is_base_of<Base, Derived>` のように、先に基底、後に派生です。

??? failure "参照や `const` が付いた型で期待と違う結果になる"
    `remove_cvref_t` で外してから調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`<type_traits>`](../type_traits.md) | 型の性質を調べる道具の一覧 |
| [`is_same`](is_same.md) | 2 つの型が同じか |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::is_base_of_v<A, B>` は、`A` が `B` の基底クラスか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 型の関係の確認に使う

## 関連ページ

- [cpprefjp: std::is_base_of](https://cpprefjp.github.io/reference/type_traits/is_base_of.html)
- [cppreference: std::is_base_of](https://en.cppreference.com/w/cpp/types/is_base_of)

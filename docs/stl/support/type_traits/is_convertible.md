---
title: std::is_convertible
summary: "型 `From` から `To` へ暗黙に変換できるかを調べる。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::is_convertible

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

関数に渡せる型かどうかを事前に調べたい。`std::is_convertible<From, To>` は、<strong>From の値を To に暗黙に変換できるか</strong>を調べます。

!!! tip "ポイント"
    - `std::is_convertible_v<A, B>` は、`A` の値を `B` へ暗黙に変換できるか
    - 値は `bool` の定数。`static_assert` や `if constexpr` に使える
    - `std::is_convertible<A, B>::value` と書いても同じ
    - 実行時のコストはない（コンパイル時に決まる）

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::is_convertible_v {#is_convertible}

<span class="ver ver-11">C++11</span>

```cpp
template <class A, class B>
inline constexpr bool is_convertible_v = is_convertible<A, B>::value;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `A` | 型 | 1 つ目の型 |
| `B` | 型 | 2 つ目の型 |

`From` の値を `To` を受け取る関数にそのまま渡せるなら `true` です。`explicit` なコンストラクターだけで変換できる場合は `false` です。派生クラスから基底クラスへのポインタは `true` ですが、逆は `false` です。

型の関係を調べるだけで、オブジェクトは作りません。テンプレートの制約や、`static_assert` による型の確認に使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

struct Base {};
struct Derived : Base {};

int main() {
  std::println("int, float -> {}", std::is_convertible_v<int, float>);
  std::println("float, int -> {}", std::is_convertible_v<float, int>);
  std::println("Derived*, Base* -> {}", std::is_convertible_v<Derived*, Base*>);
  std::println("Base*, Derived* -> {}", std::is_convertible_v<Base*, Derived*>);
  std::println("int, Base -> {}", std::is_convertible_v<int, Base>);
}
```

```text title="実行結果"
int, float -> true
float, int -> true
Derived*, Base* -> true
Base*, Derived* -> false
int, Base -> false
```

## ゲームでの使いどころ

テンプレートの引数どうしの関係をコンパイル時に保証します。

```cpp
template <class D>
void Register(D& obj) {
  static_assert(std::is_convertible_v<int, D>, "型の関係が合いません");
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
    - [x] `std::is_convertible_v<A, B>` は、`A` の値を `B` へ暗黙に変換できるか
    - [x] `static_assert` と `if constexpr` に使える
    - [x] 型の関係の確認に使う

## 関連ページ

- [cpprefjp: std::is_convertible](https://cpprefjp.github.io/reference/type_traits/is_convertible.html)
- [cppreference: std::is_convertible](https://en.cppreference.com/w/cpp/types/is_convertible)

---
title: std::derived_from
summary: "別のクラスの派生クラスであることを要求するコンセプト。"
order: 5
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::derived_from

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

テンプレートの引数に、特定の基底クラスを継承した型だけを受け付けたい。`std::derived_from<Derived, Base>` は、<strong>Derived が Base から公開継承されているか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::derived_from<Derived, Base>` は、`Derived` が `Base` の派生クラスか
    - `template <std::derived_from T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::derived_from {#derived_from}

<span class="ver ver-20">C++20</span>

```cpp
template <class Derived, class Base>
concept derived_from = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Derived` | 型 | 派生側の型 |
| `Base` | 型 | 基底側の型 |

`Derived` が `Base` を公開継承していれば満たします。同じ型どうしも満たします。`private` 継承は満たしません。ここが `std::is_base_of` との違いです（`is_base_of` は `private` 継承でも真）。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

struct Base {};
struct Derived : Base {};

int main() {
  std::println("Derived, Base                      -> {}", std::derived_from<Derived, Base>);
  std::println("Base, Derived                      -> {}", std::derived_from<Base, Derived>);
  std::println("Derived, Derived                   -> {}", std::derived_from<Derived, Derived>);
  std::println("int, int                           -> {}", std::derived_from<int, int>);
}
```

```text title="実行結果"
Derived, Base                      -> true
Base, Derived                      -> false
Derived, Derived                   -> true
int, int                           -> false
```

## ゲームでの使いどころ

コンポーネントの登録で、基底クラスを継承した型だけを受け付けます。

```cpp
template <std::derived_from<Component> T>
void AddComponent(Entity& e) { e.Add(std::make_unique<T>()); }
```

## よくあるミス

??? failure "参照や `const` が付いた型で、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_base_of`](../type_traits/is_base_of.md) | 型特性版。`private` 継承でも真 |
| [`convertible_to`](convertible_to.md) | 変換できるか |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::derived_from<Derived, Base>` は、`Derived` が `Base` の派生クラスか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::derived_from](https://cpprefjp.github.io/reference/concepts/derived_from.html)
- [cppreference: std::derived_from](https://en.cppreference.com/w/cpp/concepts/derived_from)

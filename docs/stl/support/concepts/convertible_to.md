---
title: std::convertible_to
summary: "ある型から別の型へ変換できることを要求するコンセプト。"
order: 4
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::convertible_to

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <concepts>`
</div>

関数に渡せる型だけを受け付けたい。`std::convertible_to<From, To>` は、<strong>From の値を To に変換できるか</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::convertible_to<From, To>` は、`From` が `To` に暗黙にも明示にも変換できるか
    - `template <std::convertible_to T>` のように、テンプレートの引数に直接書ける
    - 値は `bool` の定数なので、`static_assert` や `if constexpr` にも使える
    - 条件を満たさないと、分かりやすいエラーメッセージで弾かれる

!!! info "このページを読む前に"
    [テンプレートの基本](../../../basics/template.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::convertible_to {#convertible_to}

<span class="ver ver-20">C++20</span>

```cpp
template <class From, class To>
concept convertible_to = /* 条件 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `From` | 型 | 変換元の型 |
| `To` | 型 | 変換先の型 |

`From` から `To` への暗黙の変換と、`static_cast` による明示的な変換の両方ができれば満たします。`int` から `float` へ、派生クラスのポインターから基底クラスのポインターへは満たします。

コンセプトは、テンプレートの引数に条件を付ける C++20 の機能です。条件を満たさない型を渡すと、テンプレートの深い所でエラーが出るのではなく、呼び出しの場所で「この型は条件を満たしていない」と報告されます。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <print>

struct Base {};
struct Derived : Base {};

int main() {
  std::println("int, float                         -> {}", std::convertible_to<int, float>);
  std::println("float, int                         -> {}", std::convertible_to<float, int>);
  std::println("Derived*, Base*                    -> {}", std::convertible_to<Derived*, Base*>);
  std::println("Base*, Derived*                    -> {}", std::convertible_to<Base*, Derived*>);
  std::println("int, Base                          -> {}", std::convertible_to<int, Base>);
}
```

```text title="実行結果"
int, float                         -> true
float, int                         -> true
Derived*, Base*                    -> true
Base*, Derived*                    -> false
int, Base                          -> false
```

## ゲームでの使いどころ

テンプレートの引数を制限します。

```cpp
template <std::convertible_to T>
void Process(T value) {
  // T は convertible_to を満たす型だけ
}
```

## よくあるミス

??? failure "参照や `const` が付いた型で、期待と違う結果になる"
    `std::remove_cvref_t<T>` で外してから調べます。

??? failure "C++17 以前で使おうとする"
    コンセプトは C++20 の機能です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_convertible`](../type_traits/is_convertible.md) | 型特性版 |
| [`same_as`](same_as.md) | 同じ型 |

## コンパイラ対応

C++20 の機能です。GCC 10 以降、Clang 10 以降、Visual Studio 2019 16.3 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::convertible_to<From, To>` は、`From` が `To` に暗黙にも明示にも変換できるか
    - [x] テンプレートの引数に直接書ける
    - [x] `static_assert` と `if constexpr` にも使える

## 関連ページ

- [cpprefjp: std::convertible_to](https://cpprefjp.github.io/reference/concepts/convertible_to.html)
- [cppreference: std::convertible_to](https://en.cppreference.com/w/cpp/concepts/convertible_to)

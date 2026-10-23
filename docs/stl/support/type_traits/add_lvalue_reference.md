---
title: std::add_lvalue_reference
summary: "左辺値参照を付け足す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::add_lvalue_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型に左辺値参照を付けたい。`std::add_lvalue_reference` は、<strong>型に `&` を付けた型</strong>を返します。`void` のように参照を作れない型でも、エラーにならないのが、`T&` と直接書く場合との違いです。

!!! tip "ポイント"
    - `std::add_lvalue_reference_t<int>` は `int&`
    - `void` ではエラーにならず、そのまま `void`
    - 参照の畳み込みに従う
    - `T&` と書けないジェネリックなコードで使う

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::add_lvalue_reference_t {#add_lvalue_reference}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using add_lvalue_reference_t = typename add_lvalue_reference<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int` なら `int&` を返します。`T` がすでに参照なら、参照の畳み込み（`int&&` は `int&`）に従います。`void` のように参照を作れない型には、元の型をそのまま返します。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::add_lvalue_reference<T>::type` と書いても同じ型ですが、C++14 以降の `std::add_lvalue_reference_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::add_lvalue_reference_t<int> は int& : {}", std::is_same_v<std::add_lvalue_reference_t<int>, int&>);
  std::println("std::add_lvalue_reference_t<int&&> は int& : {}", std::is_same_v<std::add_lvalue_reference_t<int&&>, int&>);
  std::println("std::add_lvalue_reference_t<void> は void : {}", std::is_same_v<std::add_lvalue_reference_t<void>, void>);
}
```

```text title="実行結果"
std::add_lvalue_reference_t<int> は int& : true
std::add_lvalue_reference_t<int&&> は int& : true
std::add_lvalue_reference_t<void> は void : true
```

## ゲームでの使いどころ

型を加工するテンプレートで使います。ゲームのコードで直接書く機会は多くありませんが、汎用のテンプレート（コンテナ、イベントシステム、ECS）の内部ではよく登場します。

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`add_rvalue_reference`](add_rvalue_reference.md) | 右辺値参照を付ける |
| [`remove_reference`](remove_reference.md) | 参照を外す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::add_lvalue_reference_t<int>` は `int&`
    - [x] `void` ではエラーにならず、そのまま `void`
    - [x] 参照の畳み込みに従う

## 関連ページ

- [cpprefjp: std::add_lvalue_reference](https://cpprefjp.github.io/reference/type_traits/add_lvalue_reference.html)
- [cppreference: std::add_lvalue_reference](https://en.cppreference.com/w/cpp/types/add_lvalue_reference)

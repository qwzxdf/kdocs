---
title: std::add_rvalue_reference
summary: "右辺値参照を付け足す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::add_rvalue_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型に右辺値参照を付けたい。`std::add_rvalue_reference` は、<strong>型に `&&` を付けた型</strong>を返します。`std::declval` の戻り値の型として使われます。

!!! tip "ポイント"
    - `std::add_rvalue_reference_t<int>` は `int&&`
    - `void` ではそのまま `void`
    - `int&` は変化しない（参照の畳み込み）
    - `std::declval` の戻り値の型

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::add_rvalue_reference_t {#add_rvalue_reference}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using add_rvalue_reference_t = typename add_rvalue_reference<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int` なら `int&&` を返します。参照の畳み込みに従い、`int&` は `int&` のままです。`void` のような型は、そのまま返します。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::add_rvalue_reference<T>::type` と書いても同じ型ですが、C++14 以降の `std::add_rvalue_reference_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::add_rvalue_reference_t<int> は int&& : {}", std::is_same_v<std::add_rvalue_reference_t<int>, int&&>);
  std::println("std::add_rvalue_reference_t<int&> は int& : {}", std::is_same_v<std::add_rvalue_reference_t<int&>, int&>);
  std::println("std::add_rvalue_reference_t<void> は void : {}", std::is_same_v<std::add_rvalue_reference_t<void>, void>);
}
```

```text title="実行結果"
std::add_rvalue_reference_t<int> は int&& : true
std::add_rvalue_reference_t<int&> は int& : true
std::add_rvalue_reference_t<void> は void : true
```

## ゲームでの使いどころ

値を作らず、型だけを式の中で使うための `std::declval` の実装に使われています。`T` が `void` のときも、エラーにならず `void` のままです。

```cpp
template <class T>
std::add_rvalue_reference_t<T> MyDeclval() noexcept;   // 宣言だけ。呼ばない

// Player を作らずに、メンバー関数の戻り値の型だけを知る
using HpType = decltype(MyDeclval<Player>().GetHp());
```

## よくあるミス

??? failure "declval を実際に呼ぶ"
    `declval` は宣言だけで、定義がありません。`decltype` や `sizeof` の中でだけ使えます。呼ぶとコンパイルエラー（リンクエラー）です。

??? failure "左辺値参照から変えたつもりになる"
    `int&` に使うと、参照の折りたたみで `int&` のままです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`add_lvalue_reference`](add_lvalue_reference.md) | 左辺値参照を付ける |
| [`remove_reference`](remove_reference.md) | 参照を外す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::add_rvalue_reference_t<int>` は `int&&`
    - [x] `void` ではそのまま `void`
    - [x] `int&` は変化しない（参照の畳み込み）

## 関連ページ

- [cpprefjp: std::add_rvalue_reference](https://cpprefjp.github.io/reference/type_traits/add_rvalue_reference.html)
- [cppreference: std::add_rvalue_reference](https://en.cppreference.com/w/cpp/types/add_rvalue_reference)

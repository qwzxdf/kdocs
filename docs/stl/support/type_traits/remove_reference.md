---
title: std::remove_reference
summary: "参照を取り除く。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_reference

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

参照型 `int&` から、参照を取り除いた `int` を得たい。`std::remove_reference` は、<strong>参照を外した型</strong>を返します。`std::move` の内部でも使われています。

!!! tip "ポイント"
    - `std::remove_reference_t<int&>` は `int`
    - 左辺値参照も右辺値参照も外す
    - `const` は外れない
    - `std::move` の実装に使われる

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_reference_t {#remove_reference}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using remove_reference_t = typename remove_reference<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int&` でも `int&&` でも、`int` を返します。参照でない型は、そのまま返します。

`const` は外れません。`const int&` は `const int` になります。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::remove_reference<T>::type` と書いても同じ型ですが、C++14 以降の `std::remove_reference_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::remove_reference_t<int&> は int : {}", std::is_same_v<std::remove_reference_t<int&>, int>);
  std::println("std::remove_reference_t<int&&> は int : {}", std::is_same_v<std::remove_reference_t<int&&>, int>);
  std::println("std::remove_reference_t<const int&> は const int : {}", std::is_same_v<std::remove_reference_t<const int&>, const int>);
}
```

```text title="実行結果"
std::remove_reference_t<int&> は int : true
std::remove_reference_t<int&&> は int : true
std::remove_reference_t<const int&> は const int : true
```

## ゲームでの使いどころ

型を加工するテンプレートで使います。ゲームのコードで直接書く機会は多くありませんが、汎用のテンプレート（コンテナ、イベントシステム、ECS）の内部ではよく登場します。

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cvref`](remove_cvref.md) | `const` と `volatile` も外す |
| [`add_lvalue_reference`](add_lvalue_reference.md) | 参照を付ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::remove_reference_t<int&>` は `int`
    - [x] 左辺値参照も右辺値参照も外す
    - [x] `const` は外れない

## 関連ページ

- [cpprefjp: std::remove_reference](https://cpprefjp.github.io/reference/type_traits/remove_reference.html)
- [cppreference: std::remove_reference](https://en.cppreference.com/w/cpp/types/remove_reference)

---
title: std::add_pointer
summary: "ポインタを付け足す。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::add_pointer

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

型にポインタを付けたい。`std::add_pointer` は、<strong>型を指すポインタの型</strong>を返します。参照型の場合は、参照を外してからポインタにする点が `T*` と直接書く場合との違いです。

!!! tip "ポイント"
    - `std::add_pointer_t<int>` は `int*`
    - 参照は外してからポインタにする
    - ポインタのポインタも作れる
    - `T*` と書けないジェネリックなコードで使う

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::add_pointer_t {#add_pointer}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using add_pointer_t = typename add_pointer<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `int` なら `int*` を返します。`T` が `int&` なら、参照を外した `int*` を返します（`int&*` は書けないため）。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::add_pointer<T>::type` と書いても同じ型ですが、C++14 以降の `std::add_pointer_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::add_pointer_t<int> は int* : {}", std::is_same_v<std::add_pointer_t<int>, int*>);
  std::println("std::add_pointer_t<int&> は int* : {}", std::is_same_v<std::add_pointer_t<int&>, int*>);
  std::println("std::add_pointer_t<int*> は int** : {}", std::is_same_v<std::add_pointer_t<int*>, int**>);
}
```

```text title="実行結果"
std::add_pointer_t<int> は int* : true
std::add_pointer_t<int&> は int* : true
std::add_pointer_t<int*> は int** : true
```

## ゲームでの使いどころ

型を加工するテンプレートで使います。ゲームのコードで直接書く機会は多くありませんが、汎用のテンプレート（コンテナ、イベントシステム、ECS）の内部ではよく登場します。

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_pointer`](remove_pointer.md) | ポインタを外す |
| [`add_lvalue_reference`](add_lvalue_reference.md) | 参照を付ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::add_pointer_t<int>` は `int*`
    - [x] 参照は外してからポインタにする
    - [x] ポインタのポインタも作れる

## 関連ページ

- [cpprefjp: std::add_pointer](https://cpprefjp.github.io/reference/type_traits/add_pointer.html)
- [cppreference: std::add_pointer](https://en.cppreference.com/w/cpp/types/add_pointer)

---
title: std::remove_const
summary: "`const` を取り除く。"
order: 900
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_const

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <type_traits>`
</div>

`const` が付いた型から `const` を外したい。たとえば、`const int` を `int` として扱って変数を作りたい。`std::remove_const` は、<strong>型の最上位の `const` を外した型</strong>を返します。

!!! tip "ポイント"
    - `std::remove_const_t<const int>` は `int`
    - 最上位の `const` だけを外す
    - `const int*` の指す先の `const` は外れない
    - `volatile` も外すなら `remove_cv`

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_const_t {#remove_const}

<span class="ver ver-11">C++11</span>

```cpp
template <class T>
using remove_const_t = typename remove_const<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `const int` なら `int` を返します。`const` が付いていない型は、そのまま返します。

ポインタが指す先の `const`（`const int*`）は、型の最上位ではなく、外れません。ポインタ自体の `const`（`int* const`）だけが外れます。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::remove_const<T>::type` と書いても同じ型ですが、C++14 以降の `std::remove_const_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::remove_const_t<const int> は int : {}", std::is_same_v<std::remove_const_t<const int>, int>);
  std::println("std::remove_const_t<int> は int : {}", std::is_same_v<std::remove_const_t<int>, int>);
  std::println("std::remove_const_t<const int*> は const int* : {}", std::is_same_v<std::remove_const_t<const int*>, const int*>);
}
```

```text title="実行結果"
std::remove_const_t<const int> は int : true
std::remove_const_t<int> は int : true
std::remove_const_t<const int*> は const int* : true
```

## ゲームでの使いどころ

`const` な値を、変更できるコピーとして持つ型を作ります。入力が `const` の型でも、内部で書き換える作業用の変数を用意するときに使います。

```cpp
template <class T>
auto Process(T&& input) {
  std::remove_const_t<std::remove_reference_t<T>> work = input;   // const でないコピー
  work.Normalize();
  return work;
}
```

## よくあるミス

??? failure "const_cast と混同する"
    `remove_const` は型の変換だけです。実際のオブジェクトの `const` を外して書き換えるわけではありません。元の値を変更したいときは、`const_cast` が要りますが、元が本当に `const` なら未定義動作です。

??? failure "参照や、ポインターの先の const を外せると思う"
    最上位の `const` だけが外れます。参照は先に `remove_reference_t` で外し、ポインターの先の `const` は外れません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cv`](remove_cv.md) | `const` と `volatile` の両方を外す |
| [`add_const`](add_const.md) | `const` を付ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::remove_const_t<const int>` は `int`
    - [x] 最上位の `const` だけを外す
    - [x] `const int*` の指す先の `const` は外れない

## 関連ページ

- [cpprefjp: std::remove_const](https://cpprefjp.github.io/reference/type_traits/remove_const.html)
- [cppreference: std::remove_const](https://en.cppreference.com/w/cpp/types/remove_const)

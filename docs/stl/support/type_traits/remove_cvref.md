---
title: std::remove_cvref
summary: "`const`・`volatile`・参照をすべて外した型にする。"
order: 14
group: 型の性質（<type_traits>）
tags:
  - 型・言語サポート
---

# std::remove_cvref

<div class="page-badges" markdown>
<span class="rank rank-often">よく使う</span>
<span class="ver ver-20">C++20</span>
`#include <type_traits>`
</div>

転送参照を使ったテンプレートでは、引数の型 `T` が `const int&` や `int&&` のように、参照や `const` を含んで推論されます。型そのものを知りたいときは、これらを全部外す必要があります。`std::remove_cvref` は、<strong>参照と `const` と `volatile` を全部外した型</strong>を返します。

!!! tip "ポイント"
    - `std::remove_cvref_t<const int&>` は `int`
    - 参照と `const` と `volatile` を全部外す
    - ポインタの指す先の `const` は外れない
    - 型の性質を調べる前にこのユーティリティを通す

!!! info "このページを読む前に"
    [`<type_traits>`](../type_traits.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remove_cvref_t {#remove_cvref}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
using remove_cvref_t = typename remove_cvref<T>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 変換元の型 |

`T` が `const int&` なら `int` を返します。参照を外してから `const` と `volatile` を外す、`remove_cv_t<remove_reference_t<T>>` と同じです。

C++20 で追加された、便利な型の変換です。テンプレートの中で、引数の素の型を調べる前処理として、最も頻繁に使われます。

戻り値は型です。実行時には何も起きず、コンパイル時に型が決まります。`std::remove_cvref<T>::type` と書いても同じ型ですが、C++14 以降の `std::remove_cvref_t<T>` のほうが短く書けます。

## 実際に動かしてみる

```cpp
#include <print>
#include <type_traits>

int main() {
  std::println("std::remove_cvref_t<const int&> は int : {}", std::is_same_v<std::remove_cvref_t<const int&>, int>);
  std::println("std::remove_cvref_t<int&&> は int : {}", std::is_same_v<std::remove_cvref_t<int&&>, int>);
  std::println("std::remove_cvref_t<const int*> は const int* : {}", std::is_same_v<std::remove_cvref_t<const int*>, const int*>);
}
```

```text title="実行結果"
std::remove_cvref_t<const int&> は int : true
std::remove_cvref_t<int&&> は int : true
std::remove_cvref_t<const int*> は const int* : true
```

## ゲームでの使いどころ

型の性質を調べる前に素の型にそろえます。

```cpp
template <class T>
void Save(T&& value) {
  using Plain = std::remove_cvref_t<T>;   // 参照や const を外す
  static_assert(std::is_trivially_copyable_v<Plain>);
}
```

## よくあるミス

??? failure "変換後の型を実行時の値と混同する"
    これは型を返します。値を作るには、その型で変数を宣言します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remove_cv`](remove_cv.md) | 参照は外さない |
| [`remove_reference`](remove_reference.md) | 参照だけ外す |
| [`decay`](decay.md) | 配列や関数をポインタにも変える |

## コンパイラ対応

C++20 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::remove_cvref_t<const int&>` は `int`
    - [x] 参照と `const` と `volatile` を全部外す
    - [x] ポインタの指す先の `const` は外れない

## 関連ページ

- [cpprefjp: std::remove_cvref](https://cpprefjp.github.io/reference/type_traits/remove_cvref.html)
- [cppreference: std::remove_cvref](https://en.cppreference.com/w/cpp/types/remove_cvref)

---
title: std::indirectly_writable
summary: "`*it = value` で値を書き込める型を要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_writable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータの先へ値を書く。`*it = value;` が書けることを表すのが `std::indirectly_writable<Out, T>` です。コピー先の範囲を受け取る `std::ranges::copy` などの、出力側の引数が、これを満たす必要があります。

!!! tip "ポイント"
    - `*out = value;` が書ける
    - 値の型 `T` ごとに判定する（`<Out, T>`）
    - `const int*` は満たさない（const 要素には書けない）
    - `back_insert_iterator` や `ostream_iterator` も満たす

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_writable {#indirectly_writable}

<span class="ver ver-20">C++20</span>

```cpp
template <class Out, class T>
concept indirectly_writable = requires(Out&& o, T&& t) {
  *o = std::forward<T>(t);
  *std::forward<Out>(o) = std::forward<T>(t);
  const_cast<const std::iter_reference_t<Out>&&>(*o) = std::forward<T>(t);
};
```

満たすべき条件は、次のとおりです。

- `*o = std::forward<T>(t)` が書ける
- `*std::forward<Out>(o) = std::forward<T>(t)` が書ける（右辺値の `o` でも）
- `const_cast` したものも、書ける

`output_iterator<I, T>` は、`indirectly_writable<I, T>` を要求します。

型 `T` から要素の型への変換が暗黙にできなければ、満たしません。`int*` に `std::string` は書けません。

## 実際に動かしてみる

```cpp
#include <concepts>
#include <deque>
#include <forward_list>
#include <iterator>
#include <list>
#include <print>
#include <sstream>
#include <vector>
#include <algorithm>
#include <memory>
#include <string>

int main() {
  std::println("int* に int: {}", std::indirectly_writable<int*, int>);
  std::println("const int* に int: {}", std::indirectly_writable<const int*, int>);
  std::println("int* に string: {}", std::indirectly_writable<int*, std::string>);
  std::println("back_insert_iterator に int: {}",
               std::indirectly_writable<std::back_insert_iterator<std::vector<int>>, int>);
}
```

```text title="実行結果"
int* に int: true
const int* に int: false
int* に string: false
back_insert_iterator に int: true
```

## ゲームでの使いどころ

出力先の範囲を引数に取る関数で、書き込める型の条件を表します。

## よくあるミス

??? failure "const の範囲に書こうとする"
    コンセプトを満たさず、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_readable`](indirectly_readable.md) | 読める条件 |
| [`output_iterator`](output_iterator.md) | これを土台にしたイテレータ |
| [`indirectly_copyable`](indirectly_copyable.md) | 読んで、別へ書ける |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirectly_writable](https://cpprefjp.github.io/reference/iterator/indirectly_writable.html)
- [cppreference: std::indirectly_writable](https://en.cppreference.com/w/cpp/iterator/indirectly_writable)

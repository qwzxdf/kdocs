---
title: std::indirectly_copyable
summary: "あるイテレータから別のイテレータへ、要素をコピーできることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_copyable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`std::ranges::copy` が成り立つための条件が `std::indirectly_copyable<In, Out>` です。`In` から読んだ値を、`Out` の先へ、コピーして書き込めることを表します。コピーできない型（`unique_ptr`）の範囲は、満たしません。

!!! tip "ポイント"
    - `In` から読んだ値を、`Out` にコピーして書ける
    - 要素の型が、暗黙に変換できればよい（`int` から `long`）
    - `unique_ptr` の範囲は満たさない
    - `std::ranges::copy` の引数の条件

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_copyable {#indirectly_copyable}

<span class="ver ver-20">C++20</span>

```cpp
template <class In, class Out>
concept indirectly_copyable = std::indirectly_readable<In>
    && std::indirectly_writable<Out, std::iter_reference_t<In>>;
```

満たすべき条件は、次のとおりです。

- `std::indirectly_readable<In>`
- `std::indirectly_writable<Out, std::iter_reference_t<In>>`

`indirectly_movable` は右辺値として書き込めるか、こちらは左辺値の参照として書き込めるかを調べます。

要素の型が違っても（`int` を `long` に）、暗黙に変換できれば満たします。`std::string` から `int` へは、変換できないので満たしません。

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
  using Int = std::vector<int>::iterator;
  using Long = std::vector<long>::iterator;
  using UPtr = std::vector<std::unique_ptr<int>>::iterator;

  std::println("int → int: {}", std::indirectly_copyable<Int, Int>);
  std::println("int → long: {}", std::indirectly_copyable<Int, Long>);
  std::println("unique_ptr → unique_ptr: {}", std::indirectly_copyable<UPtr, UPtr>);
  std::println("string* → int*: {}", std::indirectly_copyable<std::string*, int*>);
}
```

```text title="実行結果"
int → int: true
int → long: true
unique_ptr → unique_ptr: false
string* → int*: false
```

## ゲームでの使いどころ

`copy` を使う前に、コピーできない要素が混ざっていないかを、コンパイル時に確かめられます。

## よくあるミス

??? failure "unique_ptr の範囲を copy する"
    満たさず、コンパイル エラーです。`move` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_movable`](indirectly_movable.md) | ムーブして書く |
| [`indirectly_readable`](indirectly_readable.md) | 読める条件 |
| [`indirectly_writable`](indirectly_writable.md) | 書ける条件 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirectly_copyable](https://cpprefjp.github.io/reference/iterator/indirectly_copyable.html)
- [cppreference: std::indirectly_copyable](https://en.cppreference.com/w/cpp/iterator/indirectly_copyable)

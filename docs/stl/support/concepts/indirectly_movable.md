---
title: std::indirectly_movable
summary: "あるイテレータから別のイテレータへ、要素をムーブできることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_movable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

要素を、別の範囲の先へムーブしたい。`std::ranges::move` のようなアルゴリズムが成り立つための条件が `std::indirectly_movable<In, Out>` です。`In` から読んだ要素を、右辺値として `Out` に書き込めることを表します。

!!! tip "ポイント"
    - `In` の要素を、右辺値として読める（`iter_rvalue_reference_t`）
    - その右辺値を、`Out` に書ける
    - コピーできない型（`unique_ptr`）でも満たせる
    - `std::ranges::move` の引数の条件

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_movable {#indirectly_movable}

<span class="ver ver-20">C++20</span>

```cpp
template <class In, class Out>
concept indirectly_movable = std::indirectly_readable<In>
    && std::indirectly_writable<Out, std::iter_rvalue_reference_t<In>>;
```

満たすべき条件は、次のとおりです。

- `std::indirectly_readable<In>`
- `std::indirectly_writable<Out, std::iter_rvalue_reference_t<In>>`

`indirectly_copyable` との違いは、読む側を右辺値として扱うことです。コピーできない型でも、ムーブできれば満たします。

`std::ranges::move(in, out)` は、この条件が満たされるときだけコンパイルできます。

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
  using UPtr = std::vector<std::unique_ptr<int>>::iterator;
  std::println("int* → int*: {}", std::indirectly_movable<int*, int*>);
  std::println("const int* → int*: {}", std::indirectly_movable<const int*, int*>);
  std::println("int* → const int*: {}", std::indirectly_movable<int*, const int*>);
  std::println("unique_ptr → unique_ptr: {}", std::indirectly_movable<UPtr, UPtr>);
}
```

```text title="実行結果"
int* → int*: true
const int* → int*: true
int* → const int*: false
unique_ptr → unique_ptr: true
```

## ゲームでの使いどころ

`std::ranges::move` を使う前に、コピーできない要素の範囲でも動くかを確かめるのに使います。

## よくあるミス

??? failure "書き込み先が const"
    書けないので、満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_copyable`](indirectly_copyable.md) | コピーして書く |
| [`indirectly_swappable`](indirectly_swappable.md) | 入れ替える |
| [`permutable`](permutable.md) | 並べ替えられる条件 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirectly_movable](https://cpprefjp.github.io/reference/iterator/indirectly_movable.html)
- [cppreference: std::indirectly_movable](https://en.cppreference.com/w/cpp/iterator/indirectly_movable)

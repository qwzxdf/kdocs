---
title: std::contiguous_iterator
summary: "要素がメモリ上で連続して並ぶことを保証するイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::contiguous_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

`std::vector` や配列は、要素がメモリ上に隙間なく並びます。そのため、イテレータから生のポインターを取り出し、C の API にそのまま渡せます。この「メモリ上で連続した要素を指す」ことを保証するイテレータが、`std::contiguous_iterator` です。`vector`、`string`、`array`、`span` のイテレータが満たします。

!!! tip "ポイント"
    - 要素がメモリ上で連続して並ぶ
    - `std::to_address(it)` で生のポインターを取り出せる
    - `vector` と `array` と `string` のイテレータが満たす
    - `deque` と `vector<bool>` は満たさない

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::contiguous_iterator {#contiguous_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept contiguous_iterator = std::random_access_iterator<I>
    && std::derived_from</* ITER_CONCEPT(I) */, std::contiguous_iterator_tag>
    && std::is_lvalue_reference_v<std::iter_reference_t<I>>
    && std::same_as<std::iter_value_t<I>, std::remove_cvref_t<std::iter_reference_t<I>>>
    && requires(const I& i) {
      { std::to_address(i) } -> std::same_as<std::add_pointer_t<std::iter_reference_t<I>>>;
    };
```

満たすべき条件は、次のとおりです。

- `std::random_access_iterator<I>`
- `iterator_concept` が `std::contiguous_iterator_tag` から派生している
- 参照型が実際の参照で、`std::to_address(i)` が要素のアドレスを返す

`std::memcpy` や `std::fwrite` に、範囲をまとめて渡せるのは、連続していることが保証されている場合だけです。`std::span` が、`vector` や配列から作れるのも、この性質のためです。

`vector<bool>` は、要素が 1 ビットに詰められ、参照が実際の参照ではないので、満たしません。

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

#include <array>
#include <string>

int main() {
  std::println("vector: {}", std::contiguous_iterator<std::vector<int>::iterator>);
  std::println("array: {}", std::contiguous_iterator<std::array<int, 3>::iterator>);
  std::println("string: {}", std::contiguous_iterator<std::string::iterator>);
  std::println("deque: {}", std::contiguous_iterator<std::deque<int>::iterator>);
  std::println("vector<bool>: {}", std::contiguous_iterator<std::vector<bool>::iterator>);
}
```

```text title="実行結果"
vector: true
array: true
string: true
deque: false
vector<bool>: false
```

## ゲームでの使いどころ

C の API に範囲を渡す関数で、「生のポインターにできるか」を制約に書くときに使います。

## よくあるミス

??? failure "deque を memcpy に渡す"
    連続していないので、壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`random_access_iterator`](random_access_iterator.md) | 連続性は要求しない |
| [`contiguous_iterator_tag`](../iterator/contiguous_iterator_tag.md) | タグ型 |
| [`to_address`](../../memory/to_address.md) | ポインターの取り出し |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::contiguous_iterator](https://cpprefjp.github.io/reference/iterator/contiguous_iterator.html)
- [cppreference: std::contiguous_iterator](https://en.cppreference.com/w/cpp/iterator/contiguous_iterator)

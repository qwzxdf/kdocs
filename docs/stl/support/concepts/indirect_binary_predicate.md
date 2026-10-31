---
title: std::indirect_binary_predicate
summary: "2 つのイテレータが指す値で、2 引数の述語を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirect_binary_predicate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

2 つの範囲の要素を組み合わせて、条件を調べたい。`std::ranges::equal` や `mismatch` の比較の述語が成り立つ条件が `std::indirect_binary_predicate<Pred, I1, I2>` です。`Pred` を、2 つのイテレータの先の要素で呼んで、`bool` を得られることを表します。

!!! tip "ポイント"
    - 述語を、2 つの要素（値と参照のすべての組み合わせ）で呼べる
    - 結果が `bool` として使える
    - `std::ranges::equal` や `mismatch` の述語の条件
    - 同じ範囲どうしでも、違う範囲でもよい

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirect_binary_predicate {#indirect_binary_predicate}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class I1, class I2>
concept indirect_binary_predicate = std::indirectly_readable<I1> && std::indirectly_readable<I2>
    && std::copy_constructible<F>
    && std::predicate<F&, std::iter_value_t<I1>&, std::iter_value_t<I2>&>
    && std::predicate<F&, std::iter_value_t<I1>&, std::iter_reference_t<I2>>
    && std::predicate<F&, std::iter_reference_t<I1>, std::iter_value_t<I2>&>
    && std::predicate<F&, std::iter_reference_t<I1>, std::iter_reference_t<I2>>;
```

満たすべき条件は、次のとおりです。

- `std::indirectly_readable<I1>`、`std::indirectly_readable<I2>`、`std::copy_constructible<Pred>`
- `std::predicate<Pred&, iter_value_t<I1>&, iter_value_t<I2>&>` など、値と参照の組み合わせすべて

`std::ranges::equal_to` や `std::ranges::less` は、この条件を満たします。

型の違う 2 つの範囲（`int` と `long`）を比べるときは、比べる述語が、両方の型を受け取れる必要があります。`std::equal_to<>` のような透過的な関数オブジェクトが向きます。

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
  auto same_length = [](const std::string& a, const std::string& b) { return a.size() == b.size(); };

  std::println("equal_to × int*, int*: {}",
               std::indirect_binary_predicate<std::ranges::equal_to, int*, int*>);
  std::println("same_length × string*, string*: {}",
               std::indirect_binary_predicate<decltype(same_length), std::string*, std::string*>);
  std::println("same_length × int*, int*: {}",
               std::indirect_binary_predicate<decltype(same_length), int*, int*>);
}
```

```text title="実行結果"
equal_to × int*, int*: true
same_length × string*, string*: true
same_length × int*, int*: false
```

## ゲームでの使いどころ

2 つの範囲を比べるアルゴリズムを自作するときの、述語の制約に使います。

## よくあるミス

??? failure "片方の型にしか対応しない述語を渡す"
    型が違う範囲では、満たしません。透過的な関数オブジェクトにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirect_unary_predicate`](indirect_unary_predicate.md) | 1 つの要素の述語 |
| [`indirect_equivalence_relation`](indirect_equivalence_relation.md) | 同値関係 |
| [`indirectly_comparable`](indirectly_comparable.md) | 2 つの範囲を比べる条件 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirect_binary_predicate](https://cpprefjp.github.io/reference/iterator/indirect_binary_predicate.html)
- [cppreference: std::indirect_binary_predicate](https://en.cppreference.com/w/cpp/iterator/indirect_binary_predicate)

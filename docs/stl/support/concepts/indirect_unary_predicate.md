---
title: std::indirect_unary_predicate
summary: "イテレータが指す値で、1 引数の述語を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirect_unary_predicate

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

イテレータの先の要素について、条件（述語）を調べたい。`std::ranges::find_if` や `count_if` が成り立つ条件が `std::indirect_unary_predicate<Pred, I>` です。`Pred` を要素に適用して、`bool` に変換できる結果を得られることを表します。

!!! tip "ポイント"
    - 述語を、イテレータの先の値や参照で呼べて、結果が `bool` として使える
    - `std::ranges::find_if`、`count_if`、`all_of` などの条件
    - ラムダで `bool` を返すものが典型
    - `void` を返す関数は満たさない

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirect_unary_predicate {#indirect_unary_predicate}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class I>
concept indirect_unary_predicate = std::indirectly_readable<I> && std::copy_constructible<F>
    && std::predicate<F&, std::iter_value_t<I>&>
    && std::predicate<F&, std::iter_reference_t<I>>;
```

満たすべき条件は、次のとおりです。

- `std::indirectly_readable<I>`、`std::copy_constructible<Pred>`
- `std::predicate<Pred&, iter_value_t<I>&>` と `predicate<Pred&, iter_reference_t<I>>`

結果が `bool` に変換できれば足ります。整数を返す関数（0 以外が真）も満たします。

述語は、要素を変更してはいけません（引数は const 参照が望ましい）。アルゴリズムは、1 つの要素に何度か述語を呼ぶことがあるからです。

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
  auto is_positive = [](int x) { return x > 0; };
  auto returns_void = [](int) {};

  std::println("bool を返す: {}", std::indirect_unary_predicate<decltype(is_positive), int*>);
  std::println("void を返す: {}", std::indirect_unary_predicate<decltype(returns_void), int*>);
}
```

```text title="実行結果"
bool を返す: true
void を返す: false
```

## ゲームでの使いどころ

`find_if` のような、条件で要素を探す関数を自作するときの、制約に使います。

## よくあるミス

??? failure "述語の中で要素を書き換える"
    アルゴリズムが複数回呼ぶと、結果が変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirect_binary_predicate`](indirect_binary_predicate.md) | 2 つの要素を取る |
| [`predicate`](predicate.md) | 一般の述語 |
| [`indirect_strict_weak_order`](indirect_strict_weak_order.md) | 順序を表す述語 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirect_unary_predicate](https://cpprefjp.github.io/reference/iterator/indirect_unary_predicate.html)
- [cppreference: std::indirect_unary_predicate](https://en.cppreference.com/w/cpp/iterator/indirect_unary_predicate)

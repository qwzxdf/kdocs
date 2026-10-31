---
title: std::indirectly_swappable
summary: "2 つのイテレータが指す要素を、入れ替えられることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirectly_swappable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

2 つの範囲の要素を、入れ替えたい。`std::ranges::swap_ranges` が成り立つ条件が `std::indirectly_swappable<I1, I2>` です。`I1` と `I2` が指す要素どうしを、`ranges::iter_swap` で入れ替えられることを表します。

!!! tip "ポイント"
    - 両方のイテレータの先を、読んで書ける
    - `std::ranges::iter_swap(a, b)` が使える
    - `const int*` どうしは満たさない（const 要素は入れ替えられない）
    - `std::ranges::swap_ranges` の引数の条件

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirectly_swappable {#indirectly_swappable}

<span class="ver ver-20">C++20</span>

```cpp
template <class I1, class I2 = I1>
concept indirectly_swappable = std::indirectly_readable<I1> && std::indirectly_readable<I2>
    && requires(const I1 i1, const I2 i2) {
      std::ranges::iter_swap(i1, i1);
      std::ranges::iter_swap(i2, i2);
      std::ranges::iter_swap(i1, i2);
      std::ranges::iter_swap(i2, i1);
    };
```

満たすべき条件は、次のとおりです。

- `std::indirectly_readable<I1>` と `std::indirectly_readable<I2>`
- `std::ranges::iter_swap(i1, i2)`、`iter_swap(i2, i1)`、`iter_swap(i1, i1)`、`iter_swap(i2, i2)` が書ける

`std::ranges::reverse` や `std::ranges::partition` のように、要素の入れ替えで動くアルゴリズムは、この条件を要求します。

`permutable` は、`indirectly_swappable` と `indirectly_movable_storable` の両方を、要求する条件です。

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
  std::println("int*: {}", std::indirectly_swappable<int*, int*>);
  std::println("const int*: {}", std::indirectly_swappable<const int*, const int*>);
  std::println("vector のイテレータ: {}",
               std::indirectly_swappable<std::vector<int>::iterator, std::vector<int>::iterator>);
}
```

```text title="実行結果"
int*: true
const int*: false
vector のイテレータ: true
```

## ゲームでの使いどころ

要素を入れ替えるアルゴリズムを自作するときに、引数の制約として使います。

## よくあるミス

??? failure "const の範囲を入れ替えようとする"
    満たさず、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`indirectly_movable`](indirectly_movable.md) | ムーブして書く |
| [`permutable`](permutable.md) | 並べ替えの条件 |
| [`iter_swap`](../../algorithms/iter_swap.md) | 2 つの要素を入れ替える |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirectly_swappable](https://cpprefjp.github.io/reference/iterator/indirectly_swappable.html)
- [cppreference: std::indirectly_swappable](https://en.cppreference.com/w/cpp/iterator/indirectly_swappable)

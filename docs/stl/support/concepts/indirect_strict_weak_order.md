---
title: std::indirect_strict_weak_order
summary: "2 つのイテレータが指す値で、厳密な弱順序を呼べることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::indirect_strict_weak_order

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

並べ替えの比較（`<`）は、「狭義の弱順序」という性質を満たす必要があります。非反射（`a < a` は偽）、推移的、等価の推移的、などです。`std::indirect_strict_weak_order<R, I>` は、`R` をイテレータの先の要素に適用でき、狭義の弱順序であることを約束する条件です。`std::ranges::sort` が要求します。

!!! tip "ポイント"
    - 比較の述語を、要素の値と参照で呼べる
    - 狭義の弱順序であること（意味の約束）
    - `std::ranges::sort`、`lower_bound`、`max_element` などが要求する
    - `<=` のような「等しい場合も真」の比較は、満たさない

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::indirect_strict_weak_order {#indirect_strict_weak_order}

<span class="ver ver-20">C++20</span>

```cpp
template <class F, class I>
concept indirect_strict_weak_order = std::indirectly_readable<I> && std::copy_constructible<F>
    && std::strict_weak_order<F&, std::iter_value_t<I>&, std::iter_value_t<I>&>
    /* ほかの組み合わせも */;
```

満たすべき条件は、次のとおりです。

- `std::indirectly_readable<I>`、`std::copy_constructible<R>`
- `std::strict_weak_order<R&, 値と参照のすべての組み合わせ>`

`<=` を比較に渡すと、`a <= a` が真になり、非反射の約束を破ります。`std::sort` が範囲の外へ読み出して、クラッシュすることがあります。必ず `<` を使います。

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
  std::println("ranges::less × int*: {}",
               std::indirect_strict_weak_order<std::ranges::less, int*>);
  std::println("ranges::greater × int*: {}",
               std::indirect_strict_weak_order<std::ranges::greater, int*>);
  std::println("less × string*: {}",
               std::indirect_strict_weak_order<std::ranges::less, std::string*>);
}
```

```text title="実行結果"
ranges::less × int*: true
ranges::greater × int*: true
less × string*: true
```

## ゲームでの使いどころ

`sort` のようなアルゴリズムを自作するときの、比較の述語の制約に使います。

## よくあるミス

??? failure "<= を比較に渡す"
    狭義の弱順序でなく、`sort` が壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strict_weak_order`](strict_weak_order.md) | 一般の狭義の弱順序 |
| [`sortable`](sortable.md) | 整列できる条件 |
| [`indirect_equivalence_relation`](indirect_equivalence_relation.md) | 同値関係 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::indirect_strict_weak_order](https://cpprefjp.github.io/reference/iterator/indirect_strict_weak_order.html)
- [cppreference: std::indirect_strict_weak_order](https://en.cppreference.com/w/cpp/iterator/indirect_strict_weak_order)

---
title: std::random_access_iterator
summary: "添字で好きな位置へ飛べるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::random_access_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

リストの 1000 番目の要素へ行くには、1000 回 `++` しなければなりません。配列なら、`it + 1000` で一度に飛べます。この「任意の距離を、一度に（O(1) で）動ける」イテレータが `std::random_access_iterator` です。`vector`、`deque`、配列のイテレータが満たします。

!!! tip "ポイント"
    - `it + n`、`it - n`、`it[n]`、距離 `it1 - it2` が使える
    - 大小の比較（`<`）ができる
    - `std::ranges::sort` が要求する
    - `std::list` は満たさない

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::random_access_iterator {#random_access_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept random_access_iterator = std::bidirectional_iterator<I>
    && std::derived_from</* ITER_CONCEPT(I) */, std::random_access_iterator_tag>
    && std::totally_ordered<I> && std::sized_sentinel_for<I, I>
    && requires(I i, const I j, std::iter_difference_t<I> n) {
      { i += n } -> std::same_as<I&>;
      { j + n } -> std::same_as<I>;
      { j[n] } -> std::same_as<std::iter_reference_t<I>>;
    };
```

満たすべき条件は、次のとおりです。

- `std::bidirectional_iterator<I>`
- `std::totally_ordered<I>`
- `std::sized_sentinel_for<I, I>`
- `i += n`、`i + n`、`i -= n`、`i - n`、`i[n]` が使える

`std::sort` は、昔から、ランダム アクセス イテレータだけを受け付けます。`std::list` を `std::sort` に渡せない（`list::sort` を使う）のは、このためです。

`std::deque` のイテレータは、ランダム アクセスですが、連続したメモリではありません。連続性が要るなら `contiguous_iterator` です。

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

int main() {
  std::println("vector: {}", std::random_access_iterator<std::vector<int>::iterator>);
  std::println("deque: {}", std::random_access_iterator<std::deque<int>::iterator>);
  std::println("list: {}", std::random_access_iterator<std::list<int>::iterator>);
  std::println("int*: {}", std::random_access_iterator<int*>);
}
```

```text title="実行結果"
vector: true
deque: true
list: false
int*: true
```

## ゲームでの使いどころ

`sort` のような、位置への直接アクセスを前提とするアルゴリズムの引数に、制約を付けます。

## よくあるミス

??? failure "list を sort に渡す"
    ランダム アクセスでないので、コンパイルできません。`list::sort` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`bidirectional_iterator`](bidirectional_iterator.md) | 1 つずつ戻れる |
| [`contiguous_iterator`](contiguous_iterator.md) | 連続したメモリ |
| [`sized_sentinel_for`](sized_sentinel_for.md) | 距離を O(1) で求められる |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::random_access_iterator](https://cpprefjp.github.io/reference/iterator/random_access_iterator.html)
- [cppreference: std::random_access_iterator](https://en.cppreference.com/w/cpp/iterator/random_access_iterator)

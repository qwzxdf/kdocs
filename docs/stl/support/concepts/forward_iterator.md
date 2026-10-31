---
title: std::forward_iterator
summary: "何度でも読み返せて、一方向に進むイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::forward_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

入力イテレータは、1 度進めると、元の位置にはもう戻れません。`forward_iterator` は、<strong>同じ範囲を何度でもたどれる</strong>イテレータです。コピーを残して、片方だけ進めても、コピーは元の位置を指し続けます。`std::forward_list` のイテレータや、`vector` のイテレータが満たします。

!!! tip "ポイント"
    - 複数回たどれる（コピーを残して進められる）
    - `input_iterator` と `incrementable` を満たす
    - `sentinel_for` として自分自身と比べられる
    - `std::list`、`std::vector` などのイテレータが満たす

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::forward_iterator {#forward_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept forward_iterator = std::input_iterator<I>
    && std::derived_from</* ITER_CONCEPT(I) */, std::forward_iterator_tag>
    && std::incrementable<I> && std::sentinel_for<I, I>;
```

満たすべき条件は、次のとおりです。

- `std::input_iterator<I>`
- `std::incrementable<I>`
- `std::sentinel_for<I, I>`
- `iterator_concept` が `std::forward_iterator_tag` から派生している

`std::ranges::sort` のように、範囲を何度もたどるアルゴリズムは、`forward_iterator` 以上を要求します。さらに強い `random_access_iterator` を要求するものもあります。

イテレータの強さは、`input_iterator` ← `forward_iterator` ← `bidirectional_iterator` ← `random_access_iterator` ← `contiguous_iterator` の順に、機能が増えていきます。

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
  std::println("forward_list: {}", std::forward_iterator<std::forward_list<int>::iterator>);
  std::println("vector: {}", std::forward_iterator<std::vector<int>::iterator>);
  std::println("istream_iterator: {}", std::forward_iterator<std::istream_iterator<int>>);
  std::println("back_insert_iterator: {}",
               std::forward_iterator<std::back_insert_iterator<std::vector<int>>>);
}
```

```text title="実行結果"
forward_list: true
vector: true
istream_iterator: false
back_insert_iterator: false
```

## ゲームでの使いどころ

範囲を 2 回以上たどるアルゴリズムを自作するときの、引数の制約に使います。

## よくあるミス

??? failure "入力ストリームのイテレータを渡す"
    1 度しかたどれないので、満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_iterator`](input_iterator.md) | 1 度だけたどる |
| [`bidirectional_iterator`](bidirectional_iterator.md) | 後ろにも進める |
| [`incrementable`](incrementable.md) | 構文上の条件 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::forward_iterator](https://cpprefjp.github.io/reference/iterator/forward_iterator.html)
- [cppreference: std::forward_iterator](https://en.cppreference.com/w/cpp/iterator/forward_iterator)

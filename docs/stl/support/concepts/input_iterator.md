---
title: std::input_iterator
summary: "要素を読みながら進められるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::input_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

標準入力やファイルのように、1 度だけ前に進みながら読んでいくデータがあります。そのイテレータを受け取る関数に、「読めて、進められるイテレータ」という条件を付けるコンセプトが `std::input_iterator` です。`vector` のイテレータも、`istream_iterator` も満たします。

!!! tip "ポイント"
    - `*it` で要素を読める（`indirectly_readable`）
    - `++it` で進められる
    - 複数回たどれることは要求しない
    - 前方イテレータ以上は、すべてこれを満たす

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::input_iterator {#input_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept input_iterator = std::input_or_output_iterator<I> && std::indirectly_readable<I>
    && requires { typename /* ITER_CONCEPT(I) */; }
    && std::derived_from</* ITER_CONCEPT(I) */, std::input_iterator_tag>;
```

満たすべき条件は、次のとおりです。

- `std::input_or_output_iterator<I>` と `std::indirectly_readable<I>` を満たす
- `iterator_concept` が `std::input_iterator_tag` から派生している

コンセプトが調べる `ITER_CONCEPT(I)` は、`I::iterator_concept` があればそれ、なければ `iterator_category` です。この値で、イテレータの強さが決まります。

`std::ranges::for_each` のように、1 度だけ全体をたどるアルゴリズムは、`input_iterator` で足ります。2 度以上たどるアルゴリズム（`std::ranges::adjacent_find` など）は、`forward_iterator` を要求します。

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

template <std::input_iterator It>
int CountElements(It first, It last) {
  int n = 0;
  for (; first != last; ++first) ++n;
  return n;
}

int main() {
  std::println("int*: {}", std::input_iterator<int*>);
  std::println("istream_iterator: {}", std::input_iterator<std::istream_iterator<int>>);
  std::println("back_insert_iterator: {}",
               std::input_iterator<std::back_insert_iterator<std::vector<int>>>);

  std::istringstream in("1 2 3 4");
  std::println("{}", CountElements(std::istream_iterator<int>(in), std::istream_iterator<int>()));
}
```

```text title="実行結果"
int*: true
istream_iterator: true
back_insert_iterator: false
4
```

## ゲームでの使いどころ

1 回きりの入力（ファイル、ストリーム）も、`vector` も受け付ける関数を、同じテンプレートで書けます。

## よくあるミス

??? failure "2 回たどる関数に input_iterator を指定する"
    入力イテレータは、2 回目にたどれません。`forward_iterator` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`forward_iterator`](forward_iterator.md) | 複数回たどれる |
| [`output_iterator`](output_iterator.md) | 書き込み用 |
| [`indirectly_readable`](indirectly_readable.md) | 読める条件 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::input_iterator](https://cpprefjp.github.io/reference/iterator/input_iterator.html)
- [cppreference: std::input_iterator](https://en.cppreference.com/w/cpp/iterator/input_iterator)

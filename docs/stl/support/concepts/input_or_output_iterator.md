---
title: std::input_or_output_iterator
summary: "イテレータとして最低限の操作ができることを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::input_or_output_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

読み出しにも書き込みにも使える、「イテレータらしさ」の最小の条件が `std::input_or_output_iterator` です。`*it` で参照でき、`++it` で進められる。ポインターも、`vector` のイテレータも、`istream_iterator` も、`back_insert_iterator` も満たします。

!!! tip "ポイント"
    - `*i` が書ける（参照できる型を返す）
    - `weakly_incrementable` を満たす
    - 読み出し専用か、書き込み専用かは問わない
    - `sentinel_for` の `I` に要求される

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::input_or_output_iterator {#input_or_output_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept input_or_output_iterator = requires(I i) {
  { *i } -> /* 参照可能な型 */;
} && std::weakly_incrementable<I>;
```

満たすべき条件は、次のとおりです。

- `weakly_incrementable<I>` を満たす
- `*i` が参照可能な型（`void` でない）を返す

`int` は `weakly_incrementable` ですが、`*i` が書けないので、`input_or_output_iterator` は満たしません。

このコンセプトを満たすことが、範囲ライブラリの `begin()` が返す型への、最低限の要求です。`std::ranges::begin(r)` は、戻り値が `input_or_output_iterator` であることを、検査します。

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
  std::println("int*: {}", std::input_or_output_iterator<int*>);
  std::println("list のイテレータ: {}", std::input_or_output_iterator<std::list<int>::iterator>);
  std::println("back_insert_iterator: {}",
               std::input_or_output_iterator<std::back_insert_iterator<std::vector<int>>>);
  std::println("int: {}", std::input_or_output_iterator<int>);
}
```

```text title="実行結果"
int*: true
list のイテレータ: true
back_insert_iterator: true
int: false
```

## ゲームでの使いどころ

範囲を受け取る関数のテンプレートで、イテレータの最低限の条件を表します。

## よくあるミス

??? failure "`int` もイテレータだと思う"
    `*i` ができないので、満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_iterator`](input_iterator.md) | 読めるイテレータ |
| [`output_iterator`](output_iterator.md) | 書けるイテレータ |
| [`weakly_incrementable`](weakly_incrementable.md) | 土台 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::input_or_output_iterator](https://cpprefjp.github.io/reference/iterator/input_or_output_iterator.html)
- [cppreference: std::input_or_output_iterator](https://en.cppreference.com/w/cpp/iterator/input_or_output_iterator)

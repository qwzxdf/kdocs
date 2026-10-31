---
title: std::output_iterator
summary: "指定した型の値を書き込めるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::output_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

結果を書き出す先（コンテナの末尾への挿入、ストリームへの出力）を受け取る関数には、「型 `T` の値を書き込めるイテレータ」という条件を付けられます。`std::output_iterator<I, T>` は、`*it++ = value;` が書けるかを調べます。

!!! tip "ポイント"
    - `*it = value;` で書き込める（`indirectly_writable<I, T>`）
    - `it++` で進められ、`*it++ = value;` の形で使える
    - 書くだけで、読めることは要求しない
    - `back_insert_iterator` や `ostream_iterator` が典型

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::output_iterator {#output_iterator}

<span class="ver ver-20">C++20</span>

```cpp
template <class I, class T>
concept output_iterator = std::input_or_output_iterator<I> && std::indirectly_writable<I, T>
    && requires(I i, T&& t) { *i++ = std::forward<T>(t); };
```

満たすべき条件は、次のとおりです。

- `std::input_or_output_iterator<I>` を満たす
- `std::indirectly_writable<I, T>` を満たす
- `*i++ = std::forward<T>(t)` が書ける

`const int*` は、`int` を書き込めないので、満たしません。`int*` は満たします。

`std::ranges::copy` や `transform` の出力先に渡すイテレータは、このコンセプトで検査されます。出力先の要素の型が値の型に変換できなければ、コンパイルが通りません。

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

template <std::output_iterator<int> Out>
void Fill3(Out out) {
  for (int i = 1; i <= 3; ++i) *out++ = i;
}

int main() {
  std::println("back_insert_iterator: {}",
               std::output_iterator<std::back_insert_iterator<std::vector<int>>, int>);
  std::println("int*: {}", std::output_iterator<int*, int>);
  std::println("const int*: {}", std::output_iterator<const int*, int>);

  std::vector<int> v;
  Fill3(std::back_inserter(v));
  std::println("{}", v);
}
```

```text title="実行結果"
back_insert_iterator: true
int*: true
const int*: false
[1, 2, 3]
```

## ゲームでの使いどころ

結果を出力する先を、配列にも `vector` にも切り替えられる関数を書くときに使います。

## よくあるミス

??? failure "const のイテレータを渡す"
    書き込めないので、コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`input_iterator`](input_iterator.md) | 読み込み用 |
| [`indirectly_writable`](indirectly_writable.md) | 書ける条件 |
| [`back_inserter`](../iterator/back_inserter.md) | 末尾に挿入する出力イテレータ |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::output_iterator](https://cpprefjp.github.io/reference/iterator/output_iterator.html)
- [cppreference: std::output_iterator](https://en.cppreference.com/w/cpp/iterator/output_iterator)

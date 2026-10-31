---
title: std::permutable
summary: "要素を並べ替えられるイテレータを要求する。"
order: 900
group: コンセプト（<concepts>）
tags:
  - 型・言語サポート
---

# std::permutable

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iterator>`
</div>

要素の並びを入れ替える（並べ替える）アルゴリズムのための、イテレータの条件が `std::permutable<I>` です。`std::ranges::reverse`、`rotate`、`unique` などが要求します。複数回たどれて、要素をムーブして、入れ替えられることを表します。

!!! tip "ポイント"
    - 前方イテレータ以上で、要素をムーブして、入れ替えられる
    - `const` の要素の範囲は満たさない
    - `unique_ptr` のようなムーブ専用の型の範囲も満たす
    - `sortable` の土台になる条件

!!! info "このページを読む前に"
    [イテレータ](../../../basics/iterator.md) と [`<iterator>`](../iterator.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::permutable {#permutable}

<span class="ver ver-20">C++20</span>

```cpp
template <class I>
concept permutable = std::forward_iterator<I>
    && std::indirectly_movable_storable<I, I> && std::indirectly_swappable<I, I>;
```

満たすべき条件は、次のとおりです。

- `std::forward_iterator<I>`
- `std::indirectly_movable_storable<I, I>`（ムーブして、保存できる）
- `std::indirectly_swappable<I, I>`

要素の並び替えを行うには、要素を読んで、書き戻せる必要があります。const の範囲は書き戻せないので、満たしません。

`std::ranges::sort` のようなアルゴリズムは、`sortable`（これに比較の条件を足したもの）を要求します。

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
  std::println("int*: {}", std::permutable<int*>);
  std::println("const int*: {}", std::permutable<const int*>);
  std::println("forward_list: {}", std::permutable<std::forward_list<int>::iterator>);
  std::println("unique_ptr: {}", std::permutable<std::vector<std::unique_ptr<int>>::iterator>);
  std::println("istream_iterator: {}", std::permutable<std::istream_iterator<int>>);
}
```

```text title="実行結果"
int*: true
const int*: false
forward_list: true
unique_ptr: true
istream_iterator: false
```

## ゲームでの使いどころ

要素を並べ替えるアルゴリズムを自作するときの、イテレータの制約に使います。

## よくあるミス

??? failure "const の範囲に使う"
    書き戻せないので、満たしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sortable`](sortable.md) | 比較も要求する |
| [`indirectly_swappable`](indirectly_swappable.md) | 入れ替えの条件 |
| [`indirectly_movable`](indirectly_movable.md) | ムーブの条件 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::permutable](https://cpprefjp.github.io/reference/iterator/permutable.html)
- [cppreference: std::permutable](https://en.cppreference.com/w/cpp/iterator/permutable)

---
title: std::make_move_iterator
summary: "参照外しするとムーブされるイテレータ。"
order: 13
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::make_move_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::make_move_iterator(it)` は、**`*it` を右辺値（ムーブ可能）として返すイテレータ**を作ります。コピーのアルゴリズムに渡すと、コピーではなくムーブになります。C++20 以降は [`views::as_rvalue`](../../algorithms/views/as_rvalue.md) でも書けます。

!!! tip "ポイント"
    - `std::vector<std::string> b(make_move_iterator(a.begin()), make_move_iterator(a.end()));` で中身を移す。
    - 元の要素は不定になる。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::make_move_iterator {#make_move_iterator}

```cpp
template <class Iter>
std::move_iterator<Iter> make_move_iterator(Iter i);
```

- 読むたびに要素を**ムーブ**するイテレータ。別の vector へ中身をムーブで移すときに使います

```cpp
#include <algorithm>
#include <deque>
#include <iterator>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> from = {"sword", "shield"};
  std::vector<std::string> to(std::make_move_iterator(from.begin()),
                              std::make_move_iterator(from.end()));
  std::deque<int> d;
  std::ranges::copy(std::vector<int>{1, 2, 3}, std::front_inserter(d));
  std::println("{} / {}", to, d);
}
```

```text title="実行結果"
["sword", "shield"] / [3, 2, 1]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 巨大な文字列の配列を別のコンテナへ移す | `dst.insert(dst.end(), make_move_iterator(...), ...)` |

## よくあるミス

??? failure "移したあとの元を読む"
    不定です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::as_rvalue`](../../algorithms/views/as_rvalue.md) | C++23 の書き方 |
| [`std::ranges::move`](../../algorithms/move.md) | 範囲を移す |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] *it を右辺値にする
    - [x] コピーがムーブになる
    - [x] 元は不定になる

## 関連ページ

- [cpprefjp: std::make_move_iterator](https://cpprefjp.github.io/reference/iterator/move_iterator.html)
- [cppreference: std::make_move_iterator](https://en.cppreference.com/w/cpp/iterator/move_iterator)

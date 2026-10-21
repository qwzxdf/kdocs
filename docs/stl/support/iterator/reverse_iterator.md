---
title: std::reverse_iterator
summary: "逆向きに進むイテレータ（rbegin / rend が返す型）。"
order: 14
group: イテレータの道具（<iterator>）
tags:
  - 型・言語サポート
---

# std::reverse_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iterator>`
</div>

`std::reverse_iterator` は、**逆向きにたどるイテレータ**です。`v.rbegin()` と `v.rend()` が返す型で、`++` すると前へ進みます。自分で作る機会は少なく、範囲 for で逆順に回す [`views::reverse`](../../algorithms/views/reverse.md) のほうが簡単です。

!!! tip "ポイント"
    - `rbegin()` は最後の要素、`rend()` は先頭の前。
    - `base()` で、元の順方向のイテレータに戻せる（1 つずれる）。
    - 逆順の走査は `views::reverse`。

!!! info "このページを読む前に"
    [`<iterator>`](../iterator.md) の概要を先に読むと分かりやすいです。[イテレータ](../../../basics/iterator.md) の基本が前提です。

## 関数の詳しい説明

### std::reverse_iterator {#reverse_iterator}

```cpp
template <class Iter>
class reverse_iterator;
```

- `++` すると前に進むイテレータ。`rbegin()` / `rend()` が返すのはこれです。`.base()` で普通のイテレータに戻せます

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};
  std::vector<int> rev(v.rbegin(), v.rend());  // rbegin / rend は reverse_iterator
  std::println("{}", rev);
}
```

```text title="実行結果"
[3, 2, 1]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 末尾から条件に合う要素を探す | `std::find_if(v.rbegin(), v.rend(), pred)` |

## よくあるミス

??? failure "base() の位置がずれる"
    `rit.base()` は、指している要素の次を指します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::reverse`](../../algorithms/views/reverse.md) | 簡単な書き方 |

## コンパイラ対応

C++11 から使えます。`ssize` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 逆向きのイテレータ
    - [x] rbegin / rend
    - [x] base() は 1 つずれる

## 関連ページ

- [cpprefjp: std::reverse_iterator](https://cpprefjp.github.io/reference/iterator/reverse_iterator.html)
- [cppreference: std::reverse_iterator](https://en.cppreference.com/w/cpp/iterator/reverse_iterator)

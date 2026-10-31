---
title: std::ranges::swap_ranges
summary: "2 つの範囲の要素を、先頭から順に入れ替える。"
order: 51
tags:
  - アルゴリズム
---

# std::ranges::swap_ranges

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

2 つの範囲の中身を、丸ごと入れ替えたい。`std::swap_ranges(first1, last1, first2)` は、1 つ目の範囲の各要素と、2 つ目の範囲の対応する要素を `swap` します。2 つのコンテナの先頭から数個を入れ替える、といった使い方ができます。

!!! tip "ポイント"
    - 2 つの範囲の対応する要素を、順に `swap` する
    - 2 つ目は、先頭だけを渡す。1 つ目と同じ長さが要る
    - 2 つの範囲が重なっていると、未定義動作
    - 戻り値は、2 つ目の範囲の最後の次の位置

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::swap_ranges {#swap_ranges}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class ForwardIt1, class ForwardIt2>
ForwardIt2 swap_ranges(ForwardIt1 first1, ForwardIt1 last1, ForwardIt2 first2);
```

要素ごとに `std::iter_swap` を呼ぶのと同じです。

コンテナ全体の入れ替えは、`a.swap(b)`（ポインターの付け替えだけで速い）を使います。`swap_ranges` は、要素の値を 1 つずつ入れ替えるので、コンテナの一部を入れ替えるときに使います。

C++20 の `std::ranges::swap_ranges` は、範囲を直接渡せます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 2, 3, 4};
  std::vector<int> b = {10, 20, 30, 40};

  // 先頭の 2 個ずつを入れ替える
  std::swap_ranges(a.begin(), a.begin() + 2, b.begin());

  std::println("{}", a);
  std::println("{}", b);
}
```

```text title="実行結果"
[10, 20, 3, 4]
[1, 2, 30, 40]
```

## ゲームでの使いどころ

2 つのバッファの一部の内容を交換するときに使います。全体の入れ替えは `swap` です。

## よくあるミス

??? failure "範囲が重なる"
    未定義動作です。

??? failure "2 つ目の範囲が短い"
    範囲の外を触ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`iter_swap`](iter_swap.md) | 2 つの要素だけを入れ替える |
| `std::swap` | 2 つの値を入れ替える |
| [`reverse`](reverse.md) | 並びを逆にする |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::swap_ranges](https://cpprefjp.github.io/reference/algorithm/ranges_swap_ranges.html)
- [cppreference: std::ranges::swap_ranges](https://en.cppreference.com/w/cpp/algorithm/ranges/swap_ranges)

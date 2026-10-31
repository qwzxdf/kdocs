---
title: std::ranges::sort_heap
summary: "ヒープを、小さい順に整列した範囲にする。"
order: 73
tags:
  - アルゴリズム
---

# std::ranges::sort_heap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

ヒープになっている範囲を、昇順に並べ替えたい。`std::sort_heap` は、ヒープから最大を順に取り出して、後ろから詰めていくことで、整列を完成させます。ヒープソートの後半の処理です。

!!! tip "ポイント"
    - ヒープの範囲を、昇順に並べ替える
    - 事前条件: 範囲がヒープであること
    - 計算量は O(n log n)
    - 終わったあとは、ヒープではなくなる

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::sort_heap {#sort_heap}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class RandomIt>
void sort_heap(RandomIt first, RandomIt last);

template <class RandomIt, class Compare>
void sort_heap(RandomIt first, RandomIt last, Compare comp);
```

`make_heap` で範囲をヒープにしたあと、`sort_heap` を呼ぶと、ヒープソートが完成します。

安定ではありません（同じ値の順序は保たれない）。通常の整列は `std::sort`（平均で速い）を使います。ヒープソートは、最悪でも O(n log n) が保証される点が特徴です。

比較は、`make_heap` に渡したものと同じものを渡します。違うと、整列の結果が不定です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 1, 4, 1, 5, 9, 2, 6};

  std::make_heap(v.begin(), v.end());
  std::sort_heap(v.begin(), v.end());

  std::println("{}", v);
}
```

```text title="実行結果"
[1, 1, 2, 3, 4, 5, 6, 9]
```

## ゲームでの使いどころ

普段は `sort` を使います。最悪の計算量を保証したい、組み込み的な場面で使われます。

## よくあるミス

??? failure "ヒープでない範囲に使う"
    結果が不定です。先に `make_heap` します。

??? failure "比較が make_heap と違う"
    整列が壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`make_heap`](make_heap.md) | 範囲をヒープにする |
| [`push_heap`](push_heap.md) | 要素を足す |
| [`sort`](sort.md) | 通常の整列 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::sort_heap](https://cpprefjp.github.io/reference/algorithm/ranges_sort_heap.html)
- [cppreference: std::ranges::sort_heap](https://en.cppreference.com/w/cpp/algorithm/ranges/sort_heap)

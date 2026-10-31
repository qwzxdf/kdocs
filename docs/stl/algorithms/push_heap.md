---
title: std::ranges::push_heap
summary: "末尾に足した要素を、ヒープに入れる。"
order: 71
tags:
  - アルゴリズム
---

# std::ranges::push_heap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

優先度つきキューを、`std::priority_queue` を使わずに、`vector` の上で作りたい。ヒープは、先頭が最大の要素になる並び方です。末尾に要素を足したあと、その要素を正しい位置に押し上げて、ヒープの性質を保つのが `std::push_heap` です。

!!! tip "ポイント"
    - `push_back` で末尾に足したあとに、`push_heap` を呼ぶ
    - 範囲全体で、末尾の要素だけがヒープの条件を破っている状態から直す
    - 計算量は O(log n)
    - 先頭（`front()`）が常に最大

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::push_heap {#push_heap}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class RandomIt>
void push_heap(RandomIt first, RandomIt last);

template <class RandomIt, class Compare>
void push_heap(RandomIt first, RandomIt last, Compare comp);
```

事前条件は、`[first, last - 1)` がすでにヒープであることです。`last - 1` の要素が新しく足されたもので、これを押し上げます。

既定の比較は `<` で、先頭が最大の「最大ヒープ」です。最小ヒープにするには、`std::greater<>` を比較に渡します。

`std::priority_queue` は、内部でこれらの関数を使っています。ヒープに触れる必要があるとき（要素を後から取り出す、中身を走査する）は、`vector` と `push_heap` の組み合わせが便利です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {9, 5, 7};
  std::make_heap(v.begin(), v.end());

  v.push_back(8);
  std::push_heap(v.begin(), v.end());
  std::println("最大: {}", v.front());

  v.push_back(20);
  std::push_heap(v.begin(), v.end());
  std::println("最大: {}", v.front());
}
```

```text title="実行結果"
最大: 9
最大: 20
```

## ゲームでの使いどころ

経路探索（A*）の優先度つきキューを、自作の `vector` ベースで作るときに使います。

## よくあるミス

??? failure "push_back を忘れて呼ぶ"
    末尾の要素が足されていないと、意味がありません。

??? failure "ヒープでない範囲に使う"
    事前条件を満たさず、結果が不定です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`pop_heap`](pop_heap.md) | 最大を取り出す |
| [`make_heap`](make_heap.md) | 範囲をヒープにする |
| [`sort_heap`](sort_heap.md) | ヒープを並べ替える |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::push_heap](https://cpprefjp.github.io/reference/algorithm/ranges_push_heap.html)
- [cppreference: std::ranges::push_heap](https://en.cppreference.com/w/cpp/algorithm/ranges/push_heap)

---
title: std::ranges::partition_point
summary: "`partition` 済みの範囲で、境目を二分探索で見つける。"
order: 48
tags:
  - アルゴリズム
---

# std::ranges::partition_point

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

述語で分かれている範囲（真の要素が先、偽があと）で、その境目の位置を知りたい。`std::partition_point` は、二分探索で、最初に偽になる要素の位置を O(log n) で求めます。`std::partition` の結果の境目を、あとから求めるのにも使えます。

!!! tip "ポイント"
    - 境目（最初に述語が偽になる要素）のイテレータを返す
    - 範囲は、述語で分かれていること（`is_partitioned` が真）
    - 二分探索なので O(log n)
    - 全部が真なら `last`、全部が偽なら `first`

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::partition_point {#partition_point}

<span class="ver ver-11">C++11</span>

```cpp
template <class ForwardIt, class UnaryPred>
ForwardIt partition_point(ForwardIt first, ForwardIt last, UnaryPred pred);
```

`lower_bound` の一般化です。`lower_bound(v, x)` は、`partition_point(v, [&](auto e){ return e < x; })` と同じ結果です。

範囲が分かれていないと、結果は不定です。事前に `is_partitioned` で確かめるか、`partition` で分けた直後の範囲に使います。

ランダム アクセスのイテレータなら O(log n) ですが、前方イテレータだけなら、進める操作が O(n) になり、全体は O(n) です。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {2, 4, 6, 1, 3};  // 偶数が先
  auto is_even = [](int x) { return x % 2 == 0; };

  const auto it = std::partition_point(v.begin(), v.end(), is_even);
  std::println("境目の位置: {}", it - v.begin());
  std::println("最初の奇数: {}", *it);

  // 並べ替えたあとの境目
  std::vector<int> w = {5, 2, 7, 4};
  const auto mid = std::partition(w.begin(), w.end(), is_even);
  std::println("partition と同じ: {}", std::partition_point(w.begin(), w.end(), is_even) == mid);
}
```

```text title="実行結果"
境目の位置: 3
最初の奇数: 1
partition と同じ: true
```

## ゲームでの使いどころ

ソート済みのデータで、「ある条件を満たす区間の末尾」を、速く求めるときに使います。

## よくあるミス

??? failure "分かれていない範囲に使う"
    結果が不定です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`is_partitioned`](is_partitioned.md) | 分かれているかの確認 |
| [`lower_bound`](lower_bound.md) | 値の位置の探索 |
| [`partition`](partition.md) | 分ける |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::partition_point](https://cpprefjp.github.io/reference/algorithm/ranges_partition_point.html)
- [cppreference: std::ranges::partition_point](https://en.cppreference.com/w/cpp/algorithm/ranges/partition_point)

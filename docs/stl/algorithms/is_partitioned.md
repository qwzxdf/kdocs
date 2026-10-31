---
title: std::ranges::is_partitioned
summary: "範囲が、条件で分けられているかを調べる。"
order: 49
tags:
  - アルゴリズム
---

# std::ranges::is_partitioned

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::partition` は、条件を満たす要素を前に、満たさない要素を後ろに、分けます。その結果、または元からそうなっているかを調べたい。`std::is_partitioned` は、範囲が、述語の真の要素が先、偽の要素があと、という形に分かれているかを返します。

!!! tip "ポイント"
    - 述語が真の要素がすべて、偽の要素より前にあれば `true`
    - 空の範囲や、全部が真・全部が偽の範囲も `true`
    - 分かれていれば、`partition_point` で境目を二分探索できる
    - 計算量は O(n)

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::is_partitioned {#is_partitioned}

<span class="ver ver-11">C++11</span>

```cpp
template <class InputIt, class UnaryPred>
bool is_partitioned(InputIt first, InputIt last, UnaryPred pred);
```

`partition_point` や、二分探索の前提条件を、デバッグ ビルドで確かめるのに使います。

```cpp
assert(std::is_partitioned(v.begin(), v.end(), pred));
```

並び替える `partition` と違い、範囲を変えません。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  auto is_even = [](int x) { return x % 2 == 0; };

  const std::vector<int> a = {2, 4, 6, 1, 3};
  const std::vector<int> b = {2, 1, 4, 3};

  std::println("偶数が先に集まっている: {}", std::is_partitioned(a.begin(), a.end(), is_even));
  std::println("混ざっている: {}", std::is_partitioned(b.begin(), b.end(), is_even));
}
```

```text title="実行結果"
偶数が先に集まっている: true
混ざっている: false
```

## ゲームでの使いどころ

`partition_point` を使う前に、データが分かれているかを検査するときに使います。

## よくあるミス

??? failure "空の範囲を false だと思う"
    空は `true` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`partition_point`](partition_point.md) | 境目を探す |
| [`partition`](partition.md) | 分ける |
| [`stable_partition`](stable_partition.md) | 順序を保って分ける |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::is_partitioned](https://cpprefjp.github.io/reference/algorithm/ranges_is_partitioned.html)
- [cppreference: std::ranges::is_partitioned](https://en.cppreference.com/w/cpp/algorithm/ranges/is_partitioned)

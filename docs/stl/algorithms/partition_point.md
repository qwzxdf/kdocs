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

`std::ranges::partition_point` は、**すでに条件で分けられている範囲（前が条件に合い、後ろが合わない）から、その境目の位置を二分探索で見つける**アルゴリズムです。整列済みの範囲での [`lower_bound`](lower_bound.md) の、条件版です。

!!! tip "ポイント"
    - 範囲は**すでに分けられている**必要がある。
    - 計算量は O(log n)。
    - 「しきい値を超えた最初の要素」を探すのに使える。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::partition_point {#partition_point}

```cpp
template <forward_range R, class Proj = identity, class Pred>
constexpr borrowed_iterator_t<R> partition_point(R&& r, Pred pred, Proj proj = {});
```

- すでに分かれている範囲の、分かれ目（最初に `pred` が false になる位置）を二分探索で探します

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 10, 20};   // 5 未満が前、5 以上が後ろに分かれている
  auto it = std::ranges::partition_point(v, [](int x) { return x < 5; });
  std::println("{}", it - v.begin());
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 整列した経験値の表から、レベルアップした最初の位置を探す | `partition_point(table, 到達していない)` |

## よくあるミス

??? failure "分けられていない範囲に使う"
    分けられていない範囲では、結果は不定です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::partition`](partition.md) | 分ける |
| [`std::ranges::lower_bound`](lower_bound.md) | 値で二分探索する |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 分けられた範囲の境目を O(log n) で探す
    - [x] 前提: 前が条件に合い、後ろが合わない
    - [x] `lower_bound` の条件版

## 関連ページ

- [cpprefjp: std::ranges::partition_point](https://cpprefjp.github.io/reference/algorithm/ranges_partition_point.html)
- [cppreference: std::ranges::partition_point](https://en.cppreference.com/w/cpp/algorithm/ranges/partition_point)

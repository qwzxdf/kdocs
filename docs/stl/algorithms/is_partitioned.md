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

`std::ranges::is_partitioned` は、**範囲が条件で分けられているか**（条件に合う要素がすべて、合わない要素より前にあるか）を調べます。`partition` や `partition_point` の前提を確かめるのに使います。

!!! tip "ポイント"
    - 全部が条件に合う、または 1 つも合わない範囲も「分けられている」扱い。
    - 計算量は O(n)。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::is_partitioned {#is_partitioned}

```cpp
template <input_range R, class Proj = identity, class Pred>
constexpr bool is_partitioned(R&& r, Pred pred, Proj proj = {});
```

- `pred` が true の要素が全部 false の要素より前にあれば `true`

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  auto even = [](int x) { return x % 2 == 0; };
  std::vector<int> a = {2, 4, 1, 3};
  std::vector<int> b = {1, 2};
  std::println("{} {}", std::ranges::is_partitioned(a, even), std::ranges::is_partitioned(b, even));
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `partition` の結果のデバッグ確認 | `assert(is_partitioned(v, 条件))` |

## よくあるミス

??? failure "整列と混同する"
    分けられているだけで、整列されているわけではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::partition`](partition.md) | 分ける |
| [`std::ranges::is_sorted`](is_sorted.md) | 整列しているか |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 分けられているかを調べる
    - [x] 全部合う・1 つも合わないも true
    - [x] `partition_point` の前提を確かめる

## 関連ページ

- [cpprefjp: std::ranges::is_partitioned](https://cpprefjp.github.io/reference/algorithm/ranges_is_partitioned.html)
- [cppreference: std::ranges::is_partitioned](https://en.cppreference.com/w/cpp/algorithm/ranges/is_partitioned)

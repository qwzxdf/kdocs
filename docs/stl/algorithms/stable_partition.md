---
title: std::ranges::stable_partition
summary: "元の順序を保ったまま、条件に合う要素を前に、合わない要素を後ろに分ける。"
order: 47
tags:
  - アルゴリズム
---

# std::ranges::stable_partition

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::stable_partition` は、[`partition`](partition.md) と同じく 2 つのグループに分けますが、**それぞれのグループの中で、元の順序を保ちます**。描画順やメニューの並びのように、順番に意味があるときに使います。

!!! tip "ポイント"
    - `partition` より少し遅いが、順序が保たれる。
    - 内部で追加のメモリを使うことがある。
    - 計算量は O(n)（メモリが足りれば）、そうでなければ O(n log n)。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md)、[イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::stable_partition {#stable_partition}

```cpp
template <bidirectional_range R, class Proj = identity, class Pred>
borrowed_subrange_t<R> stable_partition(R&& r, Pred pred, Proj proj = {});
```

- partition と同じですが、**それぞれのグループの中の順番が元のまま**です。追加のメモリが取れれば O(n)

<div class="anim" data-label="std::stable_partition(b, e, is_even)">
1 2 3 4 5 6 # v
1 *2 3 *4 5 *6 # 条件に合うものを前へ集める
>2 >4 >6 >1 >3 >5 # それぞれの中の順番は元のまま
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 5, 6};
  std::vector<int> stable = v;
  std::ranges::partition(v, [](int x) { return x % 2 == 0; });  // 偶数を前に（順番は不定）
  std::ranges::stable_partition(stable, [](int x) { return x % 2 == 0; });
  std::println("偶数が前？ {} / stable {}",
               std::ranges::is_partitioned(v, [](int x) { return x % 2 == 0; }), stable);
}
```

```text title="実行結果"
偶数が前？ true / stable [2, 4, 6, 1, 3, 5]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 表示する項目を前に集めつつ、元の並びを保つ | `stable_partition(items, 表示する)` |
| 描画リストを「不透明」「半透明」に分ける | `stable_partition(draw_list, 不透明)` |

## よくあるミス

??? failure "順序が大事なのに partition を使う"
    `partition` は順序を崩します。並びを保ちたいなら `stable_partition` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::partition`](partition.md) | 順序は保たない。速い |
| [`std::ranges::stable_sort`](stable_sort.md) | 順序を保ったまま整列する |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 順序を保ったまま 2 つに分ける
    - [x] `partition` より少し遅い
    - [x] 描画順などに使う

## 関連ページ

- [cpprefjp: std::ranges::stable_partition](https://cpprefjp.github.io/reference/algorithm/ranges_stable_partition.html)
- [cppreference: std::ranges::stable_partition](https://en.cppreference.com/w/cpp/algorithm/ranges/stable_partition)

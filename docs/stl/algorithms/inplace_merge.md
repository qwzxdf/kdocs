---
title: std::ranges::inplace_merge
summary: "1 つの範囲の前半・後半（どちらも整列済み）を、その場で併合する。"
order: 86
tags:
  - アルゴリズム
---

# std::ranges::inplace_merge

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::inplace_merge` は、**1 つの範囲の前半と後半（それぞれ整列済み）をその場で 1 つの整列済みの範囲に併合する**アルゴリズムです。`vector` の末尾に整列済みの要素を足したあと、全体を整え直すときに使えます。

!!! tip "ポイント"
    - `merge` は別の場所に書くが、`inplace_merge` は**同じ範囲の中**で併合する。
    - 前半と後半は、それぞれ整列済みであること。
    - 内部で一時メモリを使うことがある。使えなければ遅くなる（O(n log n)）。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。2 つの範囲は、**整列済み**でなければいけません。

## 関数の詳しい説明

### std::ranges::inplace_merge {#inplace_merge}

```cpp
template <bidirectional_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> inplace_merge(R&& r, iterator_t<R> middle, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 前半 `[begin, middle)` と後半 `[middle, end)` が、それぞれ整列済み |  |
| `middle` | イテレータ | 前半と後半の境目 |  |
| `comp` | 関数 | 整列した順の比較 | `<` |

- 戻り値: 範囲の終わり
- 計算量: 余分なメモリを使えれば O(n)、使えなければ O(n log n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 4, 6, 2, 3, 5};  // 前半 {1,4,6} と後半 {2,3,5} が整列済み

  std::ranges::inplace_merge(v, v.begin() + 3);
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5, 6]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 整列済みの一覧に整列済みの新規データを追加して整える | `insert` → `inplace_merge` |
| マージソートを自作する | 前半・後半を整列 → `inplace_merge` |

## よくあるミス

??? failure "境目が間違っている"
    `middle` で区切った前半・後半のどちらかが整列していないと、結果は整列されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::merge`](merge.md) | 別の場所に書き出す |
| [`std::ranges::sort`](sort.md) | 全体を整列し直す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 前半・後半をその場で併合する
    - [x] 両方が整列済みであること
    - [x] 一時メモリが使えれば O(n)

## 関連ページ

- [cpprefjp: std::ranges::inplace_merge](https://cpprefjp.github.io/reference/algorithm/ranges_inplace_merge.html)
- [cppreference: std::ranges::inplace_merge](https://en.cppreference.com/w/cpp/algorithm/ranges/inplace_merge)

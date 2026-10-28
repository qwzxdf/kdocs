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

`std::ranges::sort_heap` は、**ヒープを小さい順に整列した範囲にする**アルゴリズムです。「ヒープソート」の後半にあたります。整列後はもうヒープではありません。

!!! tip "ポイント"
    - `make_heap` → `sort_heap` で、ヒープソートになる。
    - 計算量は O(n log n)。普通は `sort` のほうが速い。
    - 整列したあとは、ヒープとして使えない。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md)、[ヒープ](../../basics/heap.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::sort_heap {#sort_heap}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> sort_heap(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | ヒープとして扱う範囲（ランダムアクセスできること） |  |
| `comp` | 関数 | 並べる順の比較 | `<`（最大が先頭） |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 範囲の終わり
- 計算量: O(n log n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 1, 4, 1, 5};
  std::ranges::make_heap(v);
  std::ranges::sort_heap(v);  // 小さい順になる
  std::println("{}", v);
}
```

```text title="実行結果"
[1, 1, 3, 4, 5]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ヒープに入れた結果を一度だけ整列して表示する | `sort_heap` |

## よくあるミス

??? failure "整列後もヒープだと思う"
    `sort_heap` のあとは昇順の配列で、ヒープではありません。続けて `push_heap` するには、もう一度 `make_heap` が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::sort`](sort.md) | 普通の整列。ほとんどの場合これでよい |
| [`std::ranges::make_heap`](make_heap.md) | ヒープを作る |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープを昇順に整列する
    - [x] そのあとはヒープではない
    - [x] 普通は `sort` を使う

## 関連ページ

- [cpprefjp: std::ranges::sort_heap](https://cpprefjp.github.io/reference/algorithm/ranges_sort_heap.html)
- [cppreference: std::ranges::sort_heap](https://en.cppreference.com/w/cpp/algorithm/ranges/sort_heap)

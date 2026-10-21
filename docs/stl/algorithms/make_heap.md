---
title: std::ranges::make_heap
summary: "範囲を、最大の要素が先頭に来るヒープに並べ替える。"
order: 70
tags:
  - アルゴリズム
---

# std::ranges::make_heap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::make_heap` は、**範囲をヒープ（最大の要素がいつも先頭にある並び）に並べ替える**アルゴリズムです。ヒープにしておくと、最大の要素をすぐ取り出せ、追加や取り出しも速くできます。普段は [`std::priority_queue`](../containers/priority_queue.md) を使えば足りますが、`vector` を自分で管理したいときにこの関数を使います。

!!! tip "ポイント"
    - `vector` の上でヒープを自分で管理するための関数。1 つの値の追加は `push_heap`、最大の取り出しは `pop_heap`。
    - 先頭が**最大**になる（`std::greater{}` を渡すと最小が先頭）。
    - `priority_queue` は内部でこれらの関数を使っている。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md)、[ヒープ](../../basics/heap.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::make_heap {#make_heap}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> make_heap(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | ヒープとして扱う範囲（ランダムアクセスできること） |  |
| `comp` | 関数 | 並べる順の比較 | `<`（最大が先頭） |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 範囲の終わり（`end()` 相当）
- 計算量: O(n)（n は要素数）

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 1, 4, 1, 5, 9, 2, 6};

  std::ranges::make_heap(v);
  std::println("最大は {}", v.front());  // 先頭が最大になる
}
```

```text title="実行結果"
最大は 9
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 優先度つきの処理待ち（自分で vector を管理する場合） | `make_heap` → `push_heap` / `pop_heap` |
| A* の探索で、コストが最小のノードを取り出す | `std::greater{}` を渡した `make_heap` |

## よくあるミス

??? failure "ヒープの中身が整列していると思う"
    ヒープは**先頭が最大**というだけで、全体は整列していません。整列したいなら `sort_heap` か、最初から `sort` です。

??? failure "比較関数を途中で変える"
    `make_heap`・`push_heap`・`pop_heap` には、**同じ比較関数**を渡し続けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::priority_queue`](../containers/priority_queue.md) | ヒープを包んだコンテナアダプター。普段はこちらで足りる |
| [`std::ranges::push_heap`](push_heap.md) | 末尾に足した要素をヒープに入れる |
| [`std::ranges::sort_heap`](sort_heap.md) | ヒープを整列済みにする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大が先頭に来るように並べる
    - [x] 追加は `push_heap`、取り出しは `pop_heap`
    - [x] 普段は `priority_queue`

## 関連ページ

- [cpprefjp: std::ranges::make_heap](https://cpprefjp.github.io/reference/algorithm/ranges_make_heap.html)
- [cppreference: std::ranges::make_heap](https://en.cppreference.com/w/cpp/algorithm/ranges/make_heap)

---
title: std::ranges::make_heap / push_heap / pop_heap
tags:
  - アルゴリズム
---

# std::ranges::make_heap / push_heap / pop_heap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

**ヒープ**は、**「一番大きい要素がいつも先頭にある」ように並べた配列**です。`make_heap` で vector をヒープの形に並べ、`push_heap` で追加、`pop_heap` で一番大きいものを取り出せます。[`std::priority_queue`](../containers/priority_queue.md) の中身はこれで、priority_queue では足りないとき（中身を全部見たい、途中で並べ直したい）に、vector とヒープ操作を直接使います。

!!! tip "結論"
    - 普段は [`std::priority_queue`](../containers/priority_queue.md) を使えば十分。
    - 中身を回したい・まとめて作り直したいときだけ、vector + ヒープ関数。
    - `push_heap` は **`push_back` のあと**、`pop_heap` は **`pop_back` の前**に呼ぶ。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::make_heap`](#make_heap) | <span class="rank rank-rare">知ってるだけ</span> | 範囲をヒープにする | O(n) |
| [`std::ranges::push_heap`](#push_heap) | <span class="rank rank-rare">知ってるだけ</span> | 末尾の要素をヒープに加える | O(log n) |
| [`std::ranges::pop_heap`](#pop_heap) | <span class="rank rank-rare">知ってるだけ</span> | 先頭（最大）を末尾に移す | O(log n) |
| [`std::ranges::sort_heap`](#sort_heap) | <span class="rank rank-rare">知ってるだけ</span> | ヒープを小さい順に並べる | O(n log n) |
| [`std::ranges::is_heap`](#is_heap) | <span class="rank rank-rare">知ってるだけ</span> | ヒープになっているか | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> heap = {3, 1, 4, 1, 5};
  std::ranges::make_heap(heap);
  std::println("最大: {}", heap.front());

  heap.push_back(9);              // 1. 末尾に入れて
  std::ranges::push_heap(heap);   // 2. ヒープを直す
  std::println("最大: {}", heap.front());

  std::ranges::pop_heap(heap);    // 1. 最大を末尾に移して
  int top = heap.back();
  heap.pop_back();                // 2. 末尾を消す
  std::println("取り出した {} / 次の最大 {}", top, heap.front());
}
```

```text title="実行結果"
最大: 5
最大: 9
取り出した 9 / 次の最大 5
```

## 関数の詳しい説明

### std::ranges::make_heap {#make_heap}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> make_heap(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 対象 | 省略不可 |
| `comp` | 比較関数 | 大小の決め方。`std::greater{}` で最小が先頭に | `<`（最大が先頭） |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

### std::ranges::push_heap {#push_heap}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> push_heap(R&& r, Comp comp = {}, Proj proj = {});
```

- 「最後の要素以外はヒープ」になっている範囲に、最後の要素を正しく加えます

### std::ranges::pop_heap {#pop_heap}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> pop_heap(R&& r, Comp comp = {}, Proj proj = {});
```

- 先頭（最大）を末尾に移し、残りをヒープに直します。値はまだ消えていないので、`back()` で取って `pop_back()` します

### std::ranges::sort_heap {#sort_heap}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> sort_heap(R&& r, Comp comp = {}, Proj proj = {});
```

- ヒープを小さい順に並べ替えます（ヒープではなくなります）

### std::ranges::is_heap {#is_heap}

```cpp
template <random_access_range R, class Proj = identity, class Comp = ranges::less>
constexpr bool is_heap(R&& r, Comp comp = {}, Proj proj = {});
```

- ヒープの形になっていれば `true`

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {5, 2, 8, 1};
  std::ranges::make_heap(v, std::greater{});  // 最小が先頭のヒープ
  std::println("最小 {} / ヒープ？ {}", v.front(), std::ranges::is_heap(v, std::greater{}));
  std::ranges::make_heap(v);
  std::ranges::sort_heap(v);
  std::println("{}", v);
}
```

```text title="実行結果"
最小 1 / ヒープ？ true
[1, 2, 5, 8]
```

## フラグ・オプション

`comp` に `std::greater{}` を渡すと、最小が先頭のヒープになります（経路探索のオープンリストなど）。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| A* のオープンリスト | priority_queue の代わりに vector で持ち、まとめて並べ直す |
| 上位 N 件を保つ | 最小ヒープで N 個だけ保持する |

## よくあるミス

??? failure "push_heap の前に push_back しない"
    `push_heap` は「末尾の要素を加える」関数なので、先に `push_back` が必要です。

??? failure "pop_heap だけして pop_back しない"
    最大は末尾に移っただけで、まだ範囲の中にあります。

## 理解度チェック

!!! question "Q1. priority_queue ではなくヒープ関数を直接使う理由は？"
    <div class="spoiler" markdown>

    **答え:** 中の vector を直接見られる（全部回す、途中の要素を書き換えて make_heap し直す）からです。普段は priority_queue で十分です。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 普段は priority_queue
    - [x] push_back → push_heap、pop_heap → pop_back

## 関連ページ

- [std::priority_queue](../containers/priority_queue.md)
- [cppreference: std::ranges::make_heap](https://en.cppreference.com/w/cpp/algorithm/ranges/make_heap)

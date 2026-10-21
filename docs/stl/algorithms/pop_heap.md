---
title: std::ranges::pop_heap
summary: "ヒープの最大の要素を末尾に動かして、残りをヒープに保つ。"
order: 72
tags:
  - アルゴリズム
---

# std::ranges::pop_heap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::pop_heap` は、**ヒープの先頭（最大）の要素を末尾に移して、残りをヒープに整え直す**アルゴリズムです。要素は消えません。取り出したあと、`pop_back` で消します。

!!! tip "ポイント"
    - 手順は 2 つ: `std::ranges::pop_heap(v)` → `v.back()` で最大を取る → `v.pop_back()`。
    - `pop_heap` のあと、末尾の要素は「ヒープから外れた」扱い。
    - 計算量は O(log n)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md)、[ヒープ](../../basics/heap.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::pop_heap {#pop_heap}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> pop_heap(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | ヒープとして扱う範囲（ランダムアクセスできること） |  |
| `comp` | 関数 | 並べる順の比較 | `<`（最大が先頭） |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 範囲の終わり
- 計算量: O(log n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {3, 1, 4, 1, 5};
  std::ranges::make_heap(v);

  std::ranges::pop_heap(v);        // 最大(5)が末尾に動く
  int top = v.back();
  v.pop_back();                    // 末尾を消す
  std::println("取り出した {} / 次の最大 {}", top, v.front());
}
```

```text title="実行結果"
取り出した 5 / 次の最大 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 優先度の一番高いイベントを取り出す | `pop_heap` → `back()` → `pop_back()` |
| A* のオープンリストから最小コストを取り出す | `std::greater{}` を渡した `pop_heap` |

## よくあるミス

??? failure "pop_heap だけで消えたと思う"
    `pop_heap` は要素を末尾へ動かすだけです。`pop_back` を忘れると、取り出した要素が範囲に残ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::push_heap`](push_heap.md) | 要素を足す |
| [`std::priority_queue::pop`](../containers/priority_queue.md) | 取り出しまで 1 行 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最大を末尾へ動かす
    - [x] `back()` で取って `pop_back()`
    - [x] 計算量は O(log n)

## 関連ページ

- [cpprefjp: std::ranges::pop_heap](https://cpprefjp.github.io/reference/algorithm/ranges_pop_heap.html)
- [cppreference: std::ranges::pop_heap](https://en.cppreference.com/w/cpp/algorithm/ranges/pop_heap)

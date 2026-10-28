---
title: std::ranges::push_heap
summary: "末尾に足した要素を、ヒープに入れる。"
order: 71
tags:
  - アルゴリズム
---

# std::ranges::push_heap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::push_heap` は、**`vector` の末尾に足した要素をヒープの正しい位置まで押し上げる**アルゴリズムです。まず `push_back` で値を足し、そのあとに呼びます。

!!! tip "ポイント"
    - 手順は 2 つ: `v.push_back(x)` → `std::ranges::push_heap(v)`。
    - 範囲全体が「最後の 1 つを除いてヒープ」になっていることが前提。
    - 計算量は O(log n)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md)、[ヒープ](../../basics/heap.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::push_heap {#push_heap}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> push_heap(R&& r, Comp comp = {}, Proj proj = {});
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
  std::vector<int> v = {3, 1, 4};
  std::ranges::make_heap(v);

  v.push_back(10);                // 末尾に足す
  std::ranges::push_heap(v);      // ヒープに入れる
  std::println("最大は {}", v.front());
}
```

```text title="実行結果"
最大は 10
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 優先度つきのキューに新しいイベントを入れる | `push_back` → `push_heap` |

## よくあるミス

??? failure "push_back を忘れる"
    `push_heap` は要素を足しません。先に自分で `push_back` します。

??? failure "ヒープでない範囲に使う"
    先に `make_heap` で整えておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::pop_heap`](pop_heap.md) | 最大の要素を取り出す |
| [`std::priority_queue::push`](../containers/priority_queue.md) | 同じ処理を 1 行で |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `push_back` → `push_heap`
    - [x] 計算量は O(log n)
    - [x] ヒープ前提

## 関連ページ

- [cpprefjp: std::ranges::push_heap](https://cpprefjp.github.io/reference/algorithm/ranges_push_heap.html)
- [cppreference: std::ranges::push_heap](https://en.cppreference.com/w/cpp/algorithm/ranges/push_heap)

---
title: std::ranges::is_heap
summary: "範囲がヒープになっているかを調べる（どこまでかを調べる版もある）。"
order: 74
tags:
  - アルゴリズム
---

# std::ranges::is_heap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::is_heap` は、**範囲がヒープになっているか**を調べます。`is_heap_until` は、ヒープの条件が崩れる最初の位置を返します。ヒープの操作がうまくいかないときのデバッグに役立ちます。

!!! tip "ポイント"
    - `assert(std::ranges::is_heap(v))` のように、デバッグ時の確認に使う。
    - `comp` は、`make_heap` に渡したのと**同じもの**を渡す。
    - 計算量は O(n)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md)、[ヒープ](../../basics/heap.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::is_heap {#is_heap}

```cpp
template <random_access_range R, class Proj = identity, class Comp = ranges::less>
constexpr bool is_heap(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 調べる範囲 |  |
| `comp` | 関数 | 並べる順の比較 | `<` |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: ヒープなら `true`
- 計算量: O(n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {9, 5, 4, 1};  // 親が子以上になっている
  std::vector<int> b = {1, 2, 3};
  std::println("{} {}", std::ranges::is_heap(a), std::ranges::is_heap(b));
}
```

```text title="実行結果"
true false
```

### std::ranges::is_heap_until {#is_heap_until}

```cpp
template <random_access_range R, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> is_heap_until(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 調べる範囲 |

- 戻り値: ヒープの条件が崩れる最初の要素のイテレータ。全部ヒープなら `end()`
- 計算量: O(n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {9, 5, 4, 1, 7};  // 7 は親(5)より大きいのでヒープが崩れる
  auto it = std::ranges::is_heap_until(v);
  std::println("{} 個目までヒープ", it - v.begin());
}
```

```text title="実行結果"
4 個目までヒープ
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ヒープ操作のデバッグ | `assert(is_heap(queue))` |

## よくあるミス

??? failure "整列済みなら true だと思う"
    昇順の配列 `{1, 2, 3}` はヒープではありません（最大が先頭に無い）。降順の配列 `{3, 2, 1}` はヒープです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::make_heap`](make_heap.md) | ヒープに並べ替える |
| [`std::ranges::is_sorted`](is_sorted.md) | 整列しているか |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ヒープになっているか調べる
    - [x] デバッグ時の確認に使う
    - [x] `is_heap_until` は崩れる位置を返す

## 関連ページ

- [cpprefjp: std::ranges::is_heap](https://cpprefjp.github.io/reference/algorithm/ranges_is_heap.html)
- [cppreference: std::ranges::is_heap](https://en.cppreference.com/w/cpp/algorithm/ranges/is_heap)

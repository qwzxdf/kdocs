---
title: std::ranges::is_sorted
summary: "範囲が並んでいるか（または、どこまで並んでいるか）を調べる。"
order: 62
tags:
  - アルゴリズム
---

# std::ranges::is_sorted

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`lower_bound` や `binary_search` は、範囲が整列済みであることが前提です。整列していない範囲に使うと、黙って間違った結果を返します。`std::ranges::is_sorted` は、範囲が小さい順（または指定した順）に並んでいるかを調べます。`is_sorted_until` は、「どこまで並んでいるか」の位置を返します。

!!! tip "ポイント"
    - 二分探索（`lower_bound` など）の前に `assert(std::ranges::is_sorted(v))` で確かめると安心。
    - 等しい要素が続いていても「並んでいる」扱い（`{1, 2, 2, 3}` は `true`）。
    - 空の範囲、要素 1 つの範囲は `true`。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::is_sorted {#is_sorted}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr bool is_sorted(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 調べる範囲 |  |
| `comp` | 関数 | 「小さい」の判定（逆順を調べるなら `std::greater{}`） | `<` |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 並んでいれば `true`
- 計算量: O(n)

<div class="anim" data-label="std::ranges::is_sorted(v)">
1 3 5 4 # 整列しているか
*1 *3 5 4 # 1 ≤ 3 ならOK
1 *3 *5 4 # 3 ≤ 5 ならOK
1 3 *5 *4 # 5 > 4 なので false
</div>

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> asc = {1, 3, 5, 5, 8};
  std::vector<int> mixed = {1, 3, 5, 4};

  std::println("{} {}", std::ranges::is_sorted(asc), std::ranges::is_sorted(mixed));
  std::println("{}", std::ranges::is_sorted(std::vector{9, 5, 2}, std::greater{}));
}
```

```text title="実行結果"
true false
true
```

### std::ranges::is_sorted_until {#is_sorted_until}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> is_sorted_until(R&& r, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 調べる範囲 |  |
| `comp` | 関数 | 「小さい」の判定 | `<` |

- 戻り値: 並びが崩れる**最初の要素**のイテレータ。全部並んでいれば `end()`
- 計算量: O(n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 5, 3, 4};
  auto it = std::ranges::is_sorted_until(v);
  std::println("{} 個目まで並んでいる。崩れた要素は {}", it - v.begin(), *it);
}
```

```text title="実行結果"
3 個目まで並んでいる。崩れた要素は 3
```

## ゲームでの使いどころ

二分探索の前に、`assert(std::ranges::is_sorted(v))` で前提を確かめておくと安心です。デバッグビルドだけで検査しておけば、リリースビルドの速さは落ちません。

並べ替えのテストにも使います。`sort` した結果が、本当に並んでいるかを、テストコードで確かめます。

すでに並んでいるデータに `sort` を呼ぶのは無駄になる場合があります。`is_sorted` で先に調べて、並んでいるなら省く、という使い方もあります。ただし `is_sorted` 自体が O(n) なので、`sort` のほうが十分に速い小さな範囲では効果がありません。

## よくあるミス

??? failure "降順に並んでいるのに false になる"
    既定は昇順（`<`）で調べます。降順なら `std::greater{}` を渡します。

??? failure "等しい要素が続くと並んでいないと思う"
    `{1, 2, 2, 3}` は、並んでいる扱いで `true` です。「厳密に増えている」ことを調べたいなら、`adjacent_find` で等しい隣を探します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::sort`](sort.md) | 並べ替える |
| [`std::ranges::adjacent_find`](adjacent_find.md) | 隣り合う条件を調べる |
| [`std::ranges::lower_bound`](lower_bound.md) | 並んでいる前提で探す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 並んでいるかは `is_sorted`、どこまでかは `is_sorted_until`
    - [x] 降順なら `std::greater{}`
    - [x] 二分探索の前に確かめる

## 関連ページ

- [cpprefjp: std::ranges::is_sorted](https://cpprefjp.github.io/reference/algorithm/ranges_is_sorted.html)
- [cppreference: std::ranges::is_sorted](https://en.cppreference.com/w/cpp/algorithm/ranges/is_sorted)

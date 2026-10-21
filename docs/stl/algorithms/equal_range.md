---
title: std::ranges::equal_range
summary: "整列済みの範囲で、値と等しい要素の範囲を、二分探索で求める。"
order: 41
tags:
  - アルゴリズム
---

# std::ranges::equal_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::equal_range` は、**整列済みの範囲から、指定した値と等しい要素が並んでいる範囲**を返します。`lower_bound` と `upper_bound` を一度に求めたものです。範囲の長さが「その値の個数」になります。

!!! tip "ポイント"
    - 範囲は**整列済み**でなければならない。
    - 戻り値は部分範囲（`subrange`）。`.size()` が個数、`.empty()` ならその値はない。
    - `lower_bound` と `upper_bound` を別々に呼ぶより、1 回の探索で済む。

!!! info "このページを読む前に"
    [二分探索](../../basics/big-o.md) の考え方が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::equal_range {#equal_range}

```cpp
template <forward_range R, class T, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_subrange_t<R> equal_range(R&& r, const T& value, Comp comp = {}, Proj proj = {});
```

- 戻り値: `value` と等しい要素の範囲（`lower_bound` から `upper_bound` まで）

<div class="anim" data-label="std::ranges::equal_range(v, 5)">
1 3 5 5 7 9 # 整列済み
1 3 *5 *5 7 9 # 5 と等しい範囲をまとめて返す
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 2, 2, 5};
  auto same = std::ranges::equal_range(v, 2);
  std::println("2 は {} 個", same.size());
}
```

```text title="実行結果"
2 は 3 個
```


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-sometimes">たまに</span> | `std::greater{}` | 降順に並んでいる範囲を探す（**並べた順と同じ比較**を渡す） |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバで探す |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 同じスコアの人数を数える | `equal_range(scores, 100).size()` |
| 同じ ID のイベントをまとめて取り出す | `equal_range(events, id, {}, &Event::id)` |

## パフォーマンス

O(log n) で探します。100 万件でも約 20 回の比較で済みます。ただし**範囲が整列済み**であることが前提で、整列されていないと結果は不定です。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 整列されていない範囲に使う | 結果は不定（未定義動作ではないが、正しい答えは返らない） |
| 整列したときと違う `comp` を渡す | 結果は不定 |

## よくあるミス

??? failure "範囲を作らずに size() を使う"
    戻り値の `subrange` は、`.size()` が使えます（ランダムアクセスのとき）。リストなど遅い範囲では O(n) になることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::lower_bound`](lower_bound.md) | 範囲の先頭だけ |
| [`std::ranges::upper_bound`](upper_bound.md) | 範囲の終わりだけ |
| `std::multimap::equal_range` | メンバ関数版 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 値と等しい要素の範囲を返す
    - [x] `.size()` が個数
    - [x] 整列済みが前提

## 関連ページ

- [cpprefjp: std::ranges::equal_range](https://cpprefjp.github.io/reference/algorithm/ranges_equal_range.html)
- [cppreference: std::ranges::equal_range](https://en.cppreference.com/w/cpp/algorithm/ranges/equal_range)

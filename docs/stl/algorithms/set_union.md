---
title: std::ranges::set_union
summary: "整列済みの 2 つの範囲の「和集合」を作る。"
order: 80
tags:
  - アルゴリズム
---

# std::ranges::set_union

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::set_union` は、**整列済みの 2 つの範囲の、どちらかに入っている要素**（和集合）を整列したまま作ります。両方に入っている要素は 1 つだけ残ります。

!!! tip "ポイント"
    - 入力の 2 つは**整列済み**であること。出力も整列済みになる。
    - 結果の書き出し先は十分な大きさに。`std::back_inserter` が安全。
    - 重複を認める「足し合わせ」が欲しいなら [`merge`](merge.md)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。2 つの範囲は、**整列済み**でなければいけません。

## 関数の詳しい説明

### std::ranges::set_union {#set_union}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, class Comp = ranges::less,
          class Proj1 = identity, class Proj2 = identity>
constexpr set_union_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
set_union(R1&& r1, R2&& r2, O result, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1`, `r2` | 範囲 | **整列済み**の 2 つの範囲 |  |
| `result` | 出力イテレータ | 結果の書き出し先。`std::back_inserter(out)` が安全 |  |
| `comp` | 関数 | 整列した順の比較 | `<` |

- 戻り値: `in1`、`in2`、`out`（結果の書き出しの終わり）を持つ構造体
- 計算量: O(n + m)

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 2, 3, 4, 5};
  std::vector<int> b = {3, 4, 5, 6, 7};
  std::vector<int> out;

  std::ranges::set_union(a, b, std::back_inserter(out));
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5, 6, 7]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 人のフレンドの持っているアイテムを合わせた一覧 | `set_union(items_a, items_b, out)` |
| 更新前後の ID 表を統合する | `set_union(old_ids, new_ids, out)` |

## よくあるミス

??? failure "整列していない範囲に使う"
    整列済みでないと、結果は不正です。先に `sort` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::merge`](merge.md) | 重複も残して併合 |
| [`std::ranges::set_intersection`](set_intersection.md) | 共通部分 |
| `std::set` の `insert` | `set` にまとめて入れる方法もある |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整列済み 2 つの和集合
    - [x] 共通の要素は 1 つにまとまる
    - [x] 入力は整列済みであること

## 関連ページ

- [cpprefjp: std::ranges::set_union](https://cpprefjp.github.io/reference/algorithm/ranges_set_union.html)
- [cppreference: std::ranges::set_union](https://en.cppreference.com/w/cpp/algorithm/ranges/set_union)

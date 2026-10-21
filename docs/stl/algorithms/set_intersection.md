---
title: std::ranges::set_intersection
summary: "整列済みの 2 つの範囲の「共通部分」を作る。"
order: 81
tags:
  - アルゴリズム
---

# std::ranges::set_intersection

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::set_intersection` は、**整列済みの 2 つの範囲の、両方に入っている要素**（共通部分）を作ります。「2 人が共通して持っているアイテム」のような判定に使えます。

!!! tip "ポイント"
    - 入力の 2 つは**整列済み**であること。
    - 結果の書き出し先は十分な大きさに。`std::back_inserter` が安全。
    - 共通部分が空かだけ知りたいなら、結果を作らず `std::ranges::any_of` と二分探索の組み合わせもある。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。2 つの範囲は、**整列済み**でなければいけません。

## 関数の詳しい説明

### std::ranges::set_intersection {#set_intersection}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, class Comp = ranges::less,
          class Proj1 = identity, class Proj2 = identity>
constexpr set_intersection_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
set_intersection(R1&& r1, R2&& r2, O result, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
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

  std::ranges::set_intersection(a, b, std::back_inserter(out));
  std::println("{}", out);
}
```

```text title="実行結果"
[3, 4, 5]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 人が共通して持つアイテム | `set_intersection(items_a, items_b, out)` |
| 両方のフィルターに合う ID | `set_intersection(ids1, ids2, out)` |

## よくあるミス

??? failure "整列していない範囲に使う"
    整列済みでないと、結果は不正です。先に `sort` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::set_union`](set_union.md) | 和集合 |
| [`std::ranges::set_difference`](set_difference.md) | 差集合 |
| [`std::ranges::includes`](includes.md) | 片方がもう片方を含むか |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 両方に入っている要素を作る
    - [x] 入力は整列済み
    - [x] 結果も整列済み

## 関連ページ

- [cpprefjp: std::ranges::set_intersection](https://cpprefjp.github.io/reference/algorithm/ranges_set_intersection.html)
- [cppreference: std::ranges::set_intersection](https://en.cppreference.com/w/cpp/algorithm/ranges/set_intersection)

---
title: 集合演算（set_union / set_intersection など）
tags:
  - アルゴリズム
---

# 集合演算（set_union / set_intersection など）

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

集合演算のアルゴリズムは、**ソート済みの 2 つの範囲**について、「両方に入っているもの」（共通部分）、「どちらかに入っているもの」（和）、「片方にだけ入っているもの」（差）を求めます。`std::ranges::merge` は 2 つのソート済み範囲を 1 つのソート済み範囲にまとめ、`includes` は片方がもう片方を全部含んでいるかを調べます。**入力は必ずソート済み**である必要があります。

!!! tip "結論"
    - 入力は**ソート済み**（vector なら先に sort、set ならそのまま使える）。
    - 結果は `std::back_inserter(v)` で別の vector に書き込む。
    - 「必要なアイテムを全部持っているか」は `includes`、「共通のタグ」は `set_intersection`。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::includes`](#includes) | <span class="rank rank-sometimes">たまに</span> | 片方がもう片方を全部含むか | O(n + m) |
| [`std::ranges::set_intersection`](#set_intersection) | <span class="rank rank-sometimes">たまに</span> | 両方にあるもの（共通部分） | O(n + m) |
| [`std::ranges::set_difference`](#set_difference) | <span class="rank rank-sometimes">たまに</span> | 1 つ目にだけあるもの（差） | O(n + m) |
| [`std::ranges::set_union`](#set_union) | <span class="rank rank-rare">知ってるだけ</span> | どちらかにあるもの（和） | O(n + m) |
| [`std::ranges::merge`](#merge) | <span class="rank rank-rare">知ってるだけ</span> | 2 つのソート済み範囲をまとめる（重複も残す） | O(n + m) |
| [`std::ranges::set_symmetric_difference`](#set_symmetric_difference) | <span class="rank rank-rare">知ってるだけ</span> | 片方にだけあるもの | O(n + m) |

<div class="mem">
<div class="mem-step"><span class="mem-label">A = {1, 2, 3, 4}</span><span class="mem-note">B = {3, 4, 5}</span></div>
<div class="mem-step"><span class="mem-label">共通部分</span><span class="mem-cells"><span>3</span><span>4</span></span></div>
<div class="mem-step"><span class="mem-label">和</span><span class="mem-cells"><span>1</span><span>2</span><span>3</span><span>4</span><span>5</span></span></div>
<div class="mem-step"><span class="mem-label">差（A − B）</span><span class="mem-cells"><span>1</span><span>2</span></span></div>
<div class="mem-step"><span class="mem-label">対称差</span><span class="mem-cells"><span>1</span><span>2</span><span>5</span></span></div>
</div>

## よくある使い方

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <set>
#include <vector>

int main() {
  std::set<int> have = {101, 102, 205, 330};  // 持っているアイテム ID（set はソート済み）
  std::set<int> recipe = {102, 205};          // 合成に必要なアイテム
  std::println("合成できる？ {}", std::ranges::includes(have, recipe));

  std::set<int> need = {102, 400, 500};
  std::vector<int> missing;
  std::ranges::set_difference(need, have, std::back_inserter(missing));
  std::println("足りないもの: {}", missing);
}
```

```text title="実行結果"
合成できる？ true
足りないもの: [400, 500]
```

## 関数の詳しい説明

### std::ranges::includes {#includes}

```cpp
template <input_range R1, input_range R2, class Proj1 = identity, class Proj2 = identity,
          class Comp = ranges::less>
constexpr bool includes(R1&& r1, R2&& r2, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

- `r2` の要素が全部 `r1` に含まれていれば `true`

### std::ranges::set_intersection {#set_intersection}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, class Comp = ranges::less,
          class Proj1 = identity, class Proj2 = identity>
constexpr set_intersection_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
set_intersection(R1&& r1, R2&& r2, O result, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r1`, `r2` | ソート済みの範囲 | 入力 |
| `result` | 出力イテレータ | 結果を書く先 |
| `comp` | 比較関数 | ソートに使ったのと同じもの |

- 両方に入っている要素を、ソートされた順で書き込みます

### std::ranges::set_difference {#set_difference}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, /* ... */>
constexpr set_difference_result<borrowed_iterator_t<R1>, O>
set_difference(R1&& r1, R2&& r2, O result, /* comp, proj1, proj2 */);
```

- `r1` にあって `r2` に無い要素を書き込みます

### std::ranges::set_union {#set_union}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, /* ... */>
constexpr set_union_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
set_union(R1&& r1, R2&& r2, O result, /* comp, proj1, proj2 */);
```

- どちらかにある要素を、重複をまとめて書き込みます

### std::ranges::merge {#merge}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, /* ... */>
constexpr merge_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
merge(R1&& r1, R2&& r2, O result, /* comp, proj1, proj2 */);
```

- 2 つのソート済み範囲を、ソートされた 1 つの範囲にまとめます。**重複も全部残ります**（set_union との違い）

### std::ranges::set_symmetric_difference {#set_symmetric_difference}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, /* ... */>
constexpr set_symmetric_difference_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
set_symmetric_difference(R1&& r1, R2&& r2, O result, /* comp, proj1, proj2 */);
```

- どちらか片方にだけある要素を書き込みます（「変化したもの」を見つけるのに使える）

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 2, 3, 4};
  std::vector<int> b = {3, 4, 5};
  std::vector<int> i, u, m, s;
  std::ranges::set_intersection(a, b, std::back_inserter(i));
  std::ranges::set_union(a, b, std::back_inserter(u));
  std::ranges::merge(a, b, std::back_inserter(m));
  std::ranges::set_symmetric_difference(a, b, std::back_inserter(s));
  std::println("共通 {} / 和 {} / merge {} / 対称差 {}", i, u, m, s);
}
```

```text title="実行結果"
共通 [3, 4] / 和 [1, 2, 3, 4, 5] / merge [1, 2, 3, 3, 4, 4, 5] / 対称差 [1, 2, 5]
```

## フラグ・オプション

`comp` / `proj` で比べ方を変えられます。ソートしたときと同じものを渡します。

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| 合成・クエストの素材がそろっているか | `includes` |
| 足りない素材の一覧 | `set_difference` |
| 2 人が共通して持っているカード | `set_intersection` |
| 前フレームとの差分（増えた・減ったもの） | `set_difference` / `set_symmetric_difference` |

## よくあるミス

??? failure "ソートせずに使う"
    ソートされていない vector を渡すと、結果がでたらめになります。先に `std::ranges::sort` します。

## 理解度チェック

!!! question "Q1. 前フレームに見えていた敵 {1, 3, 5} と、今見えている敵 {3, 5, 7}。新しく見えた敵を出すには？"
    <div class="spoiler" markdown>

    **答え:** `set_difference(今, 前, out)` で `{7}`。消えた敵は `set_difference(前, 今, out)` で `{1}` です。

    </div>

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入力はソート済み
    - [x] 含むか includes、共通 intersection、差 difference

## 関連ページ

- [std::set](../containers/set.md)
- [cppreference: std::ranges::set_intersection](https://en.cppreference.com/w/cpp/algorithm/ranges/set_intersection)

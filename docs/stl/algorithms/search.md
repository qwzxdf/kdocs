---
title: std::ranges::search / adjacent_find / is_sorted
tags:
  - アルゴリズム
---

# std::ranges::search / adjacent_find / is_sorted

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

このページでは、[`find`](find.md) では探せない**並びのパターン**を探すアルゴリズムをまとめます。`search` は**連続した並び**（部分列）を探し、`adjacent_find` は**隣り合う 2 つが同じ**ところを探し、`is_sorted` は**並んでいるか**を調べます。C++23 の `starts_with` / `ends_with` は、範囲が特定の並びで始まる・終わるかを調べます。

!!! tip "ポイント"
    - 連続した並びを探すなら `search`（文字列なら `string::find` で十分）。
    - 「同じものが 2 つ続いた」は `adjacent_find`。
    - ソートされているかのチェック（デバッグ・二分探索の前の確認）は `is_sorted`。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::search`](#search) | <span class="rank rank-sometimes">たまに</span> | 連続した並びを探す | O(n·m) |
| [`std::ranges::adjacent_find`](#adjacent_find) | <span class="rank rank-sometimes">たまに</span> | 隣り合う 2 つが同じ（条件を満たす）所 | O(n) |
| [`std::ranges::is_sorted`](#is_sorted) | <span class="rank rank-sometimes">たまに</span> | 並んでいるか | O(n) |
| [`std::ranges::starts_with`](#starts_with) | <span class="rank rank-rare">知ってるだけ</span> | 特定の並びで始まるか <span class="ver ver-23">C++23</span> | O(m) |
| [`std::ranges::ends_with`](#ends_with) | <span class="rank rank-rare">知ってるだけ</span> | 特定の並びで終わるか <span class="ver ver-23">C++23</span> | O(m) |
| [`std::ranges::is_sorted_until`](#is_sorted_until) | <span class="rank rank-rare">知ってるだけ</span> | どこまで並んでいるか | O(n) |
| [`std::ranges::search_n`](#search_n) | <span class="rank rank-rare">知ってるだけ</span> | 同じ値が n 個続く所 | O(n) |
| [`std::ranges::find_first_of`](#find_first_of) | <span class="rank rank-rare">知ってるだけ</span> | 候補のどれかが最初に出る所 | O(n·m) |

## よくある使い方

### 格闘ゲームのコマンド判定

```cpp
#include <algorithm>
#include <array>
#include <print>
#include <vector>

enum class In { kDown, kDownRight, kRight, kPunch, kKick };

int main() {
  // 入力履歴の中に「↓ ↘ → P」の並びがあるか
  std::vector<In> history = {In::kKick, In::kDown, In::kDownRight, In::kRight, In::kPunch};
  constexpr std::array kHadouken = {In::kDown, In::kDownRight, In::kRight, In::kPunch};

  auto found = std::ranges::search(history, kHadouken);
  std::println("波動拳？ {}", !found.empty());
  std::println("最後がこの並び？ {}", std::ranges::ends_with(history, kHadouken));
}
```

```text title="実行結果"
波動拳？ true
最後がこの並び？ true
```

## 関数の詳しい説明

### std::ranges::search {#search}

```cpp
template <forward_range R1, forward_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr borrowed_subrange_t<R1> search(R1&& r1, R2&& r2, Pred pred = {}, Proj1 proj1 = {},
                                         Proj2 proj2 = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r1` | 範囲 | 探す場所 |
| `r2` | 範囲 | 探す並び |

- 戻り値: 見つかった部分の範囲。見つからなければ空（`.empty()` が true）

<div class="anim" data-label="std::ranges::search(v, sub)">
a b c d b c # v から "bc" を探す
*a b c d b c # 先頭から比べる
a *b *c d b c # 見つかる。最初の位置を返す
</div>

### std::ranges::adjacent_find {#adjacent_find}

```cpp
template <forward_range R, class Proj = identity, class Pred = ranges::equal_to>
constexpr borrowed_iterator_t<R> adjacent_find(R&& r, Pred pred = {}, Proj proj = {});
```

- 隣り合う 2 つが等しい（または `pred(a, b)` が true）最初の位置。無ければ `end()`

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> rolls = {3, 5, 5, 2, 6, 6, 6};
  auto it = std::ranges::adjacent_find(rolls);
  std::println("最初のゾロ目は {} 回目", it - rolls.begin() + 1);
  auto three = std::ranges::search_n(rolls, 3, 6);  // 6 が 3 回続く所
  std::println("6 が 3 連続？ {}", !three.empty());
}
```

```text title="実行結果"
最初のゾロ目は 2 回目
6 が 3 連続？ true
```

### std::ranges::is_sorted {#is_sorted}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr bool is_sorted(R&& r, Comp comp = {}, Proj proj = {});
```

- 並んでいれば `true`。二分探索の前に `assert(std::ranges::is_sorted(v))` で確かめると安心です

<div class="anim" data-label="std::ranges::is_sorted(v)">
1 3 5 4 # 整列しているか
*1 *3 3 4 # 1 ≤ 3 ならOK
1 *3 *5 4 # 3 ≤ 5 ならOK
1 3 *5 *4 # 5 > 4 なので false
</div>

### std::ranges::starts_with {#starts_with}

<span class="ver ver-23">C++23</span>

```cpp
template <input_range R1, input_range R2, /* pred, proj1, proj2 */>
constexpr bool starts_with(R1&& r1, R2&& r2, /* ... */);
```

- `r1` が `r2` の並びで始まれば `true`

### std::ranges::ends_with {#ends_with}

<span class="ver ver-23">C++23</span>

```cpp
template <input_range R1, input_range R2, /* pred, proj1, proj2 */>
constexpr bool ends_with(R1&& r1, R2&& r2, /* ... */);
```

- `r1` が `r2` の並びで終われば `true`

### std::ranges::is_sorted_until {#is_sorted_until}

```cpp
template <forward_range R, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> is_sorted_until(R&& r, Comp comp = {}, Proj proj = {});
```

- 先頭からどこまで並んでいるか（並びが崩れる最初の位置）

### std::ranges::search_n {#search_n}

```cpp
template <forward_range R, class T, class Pred = ranges::equal_to, class Proj = identity>
constexpr borrowed_subrange_t<R> search_n(R&& r, std::ranges::range_difference_t<R> count,
                                          const T& value, Pred pred = {}, Proj proj = {});
```

- `value` が `count` 個続く所を探します

### std::ranges::find_first_of {#find_first_of}

```cpp
template <input_range R1, forward_range R2, /* pred, proj1, proj2 */>
constexpr borrowed_iterator_t<R1> find_first_of(R1&& r1, R2&& r2, /* ... */);
```

- `r1` の中で、`r2` のどれかと等しい最初の要素

```cpp
#include <algorithm>
#include <array>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 5, 3, 4};
  std::array prefix = {1, 2};
  std::array targets = {7, 3, 5};
  std::println("{} {} {} {}", std::ranges::is_sorted(v), std::ranges::starts_with(v, prefix),
               *std::ranges::is_sorted_until(v), *std::ranges::find_first_of(v, targets));
}
```

```text title="実行結果"
false true 3 5
```

## フラグ・オプション

`pred` / `proj` で比べ方を変えられます。

## ゲームでの使いどころ

| 場面 | 関数 |
| --- | --- |
| コマンド入力の判定 | `search` / `ends_with` |
| 同じ色が連続（パズルの連鎖） | `adjacent_find` / `search_n` |
| デバッグで並びを確認 | `is_sorted` |

## よくあるミス

??? failure "search の結果を end() と比べる"
    ranges 版の `search` は範囲を返します。見つかったかは `.empty()` で確かめ、位置は `.begin()` です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 並びを探すのは search、隣同士は adjacent_find
    - [x] 並んでいるかは is_sorted

## 関連ページ

- [std::ranges::find](find.md)
- [cppreference: std::ranges::search](https://en.cppreference.com/w/cpp/algorithm/ranges/search)

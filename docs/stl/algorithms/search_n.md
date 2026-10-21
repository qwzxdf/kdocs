---
title: std::ranges::search_n
summary: "同じ値が n 個続いている場所を探す。"
order: 60
tags:
  - アルゴリズム
---

# std::ranges::search_n

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::search_n` は、**同じ値が n 個連続している場所**を探す関数です。「サイコロで 6 が 3 回続いたか」「空きマスが 3 つ並んでいるか」のような判定に使えます。

!!! tip "ポイント"
    - `search_n(r, 3, 6)` は「6 が 3 つ続く所」。個数を先に、値を後に書く。
    - 戻り値は `search` と同じ、見つかった部分の範囲。
    - `count` に 0 を渡すと、必ず「見つかった（空の範囲）」になる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::search_n {#search_n}

```cpp
template <forward_range R, class T, class Pred = ranges::equal_to, class Proj = identity>
constexpr borrowed_subrange_t<R> search_n(R&& r, range_difference_t<R> count,
                                          const T& value, Pred pred = {}, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 探す場所 |
| `count` | 整数 | 連続してほしい個数 |
| `value` | T | 続けて並んでほしい値 |
| `pred` | 関数 | 「等しい」の判定（省略時は `==`） |

- 戻り値: 見つかった部分の範囲。見つからなければ空（`.empty()` が `true`）
- 計算量: O(n)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> rolls = {3, 5, 5, 2, 6, 6, 6};

  auto three = std::ranges::search_n(rolls, 3, 6);  // 6 が 3 回続く所
  if (!three.empty()) {
    std::println("6 が 3 連続。位置 {}", three.begin() - rolls.begin());
  }
}
```

```text title="実行結果"
6 が 3 連続。位置 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| サイコロで同じ目が続いたか | `search_n(rolls, 3, 6)` |
| 空きマスが連続して並んでいるか（座席・配置） | `search_n(slots, 3, kEmpty)` |
| 連続ログイン日数の判定 | `search_n(days, 7, true)` |

## よくあるミス

??? failure "個数と値を逆に書く"
    `search_n(rolls, 6, 3)` は「3 が 6 個続く所」です。個数が先、値が後です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::search`](search.md) | 決まった並びを探す |
| [`std::ranges::adjacent_find`](adjacent_find.md) | 隣り合う 2 つが同じ所を探す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 同じ値が n 個続く所を探す
    - [x] 個数が先、値が後
    - [x] 戻り値は部分範囲

## 関連ページ

- [cpprefjp: std::ranges::search_n](https://cpprefjp.github.io/reference/algorithm/ranges_search_n.html)
- [cppreference: std::ranges::search_n](https://en.cppreference.com/w/cpp/algorithm/ranges/search_n)

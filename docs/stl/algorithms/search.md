---
title: std::ranges::search
summary: "別の範囲の「連続した並び」が、含まれている場所を探す。"
order: 31
tags:
  - アルゴリズム
---

# std::ranges::search

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::search` は、**ある範囲の中から、別の範囲と同じ並びが連続している場所を探す**関数です。文字列の部分一致（`find`）を、任意のコンテナに広げたものです。格闘ゲームの入力履歴から「↓↘→P」の並びを見つける、といった判定に使えます。

!!! tip "ポイント"
    - 1 つの値を探すなら [`find`](find.md)、**並び**を探すなら `search`。
    - 戻り値は「見つかった部分の範囲」。`.empty()` で見つかったか確かめる。
    - 素朴な探し方なので、最悪 O(n·m)。大きな文字列の検索なら `std::string::find` や `std::boyer_moore_searcher` のほうが速い。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::search {#search}

```cpp
template <forward_range R1, forward_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr borrowed_subrange_t<R1> search(R1&& r1, R2&& r2, Pred pred = {},
                                         Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1` | 範囲 | 探す場所 | 省略不可 |
| `r2` | 範囲 | 探す並び | 省略不可 |
| `pred` | 関数 | 「等しい」の判定 | `==` |
| `proj1`, `proj2` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 見つかった部分を表す範囲（`subrange`）。見つからなければ、空の範囲（`r1` の終わり）
- 計算量: 最悪 O(n·m)（n は `r1` の長さ、m は `r2` の長さ）

<div class="anim" data-label="std::ranges::search(v, sub)">
a b c d b c # v から "bc" を探す
*a b c d b c # 先頭から比べる
a *b *c d b c # 見つかる。最初に見つかった所を返す
</div>

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
}
```

```text title="実行結果"
波動拳？ true
```

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4, 2, 3};
  std::vector<int> sub = {2, 3};

  auto found = std::ranges::search(v, sub);
  // found は部分範囲。begin() で先頭の位置が取れる
  std::println("最初に見つかった位置: {}", found.begin() - v.begin());
}
```

```text title="実行結果"
最初に見つかった位置: 1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| コマンド入力（コンボ）の判定 | `search(history, command)` |
| ログから特定のイベントの並びを探す | `search(events, pattern)` |

## よくあるミス

??? failure "戻り値を bool として使う"
    戻り値は範囲です。見つかったかは `!found.empty()` で調べます（`if (found)` とは書けません）。

??? failure "文字列の検索に使う"
    `std::string` なら `s.find("abc")` のほうが短くて速いです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::find`](find.md) | 1 つの値や条件を探す |
| [`std::ranges::search_n`](search_n.md) | 同じ値が n 個続く所を探す |
| [`std::ranges::contains_subrange`](contains.md) | 含まれているかだけを調べる（C++23） |
| `std::string::find` | 文字列の部分一致。こちらが速い |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] **並び**を探すなら `search`
    - [x] 見つからなければ空の範囲
    - [x] 最悪 O(n·m)

## 関連ページ

- [cpprefjp: std::ranges::search](https://cpprefjp.github.io/reference/algorithm/ranges_search.html)
- [cppreference: std::ranges::search](https://en.cppreference.com/w/cpp/algorithm/ranges/search)

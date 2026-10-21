---
title: std::ranges::adjacent_find
summary: "隣り合う 2 つの要素が等しい（または条件を満たす）最初の場所を探す。"
order: 61
tags:
  - アルゴリズム
---

# std::ranges::adjacent_find

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::adjacent_find` は、**隣り合う 2 つの要素が等しい最初の場所**を探します。条件を渡せば、「隣り合う 2 つが条件を満たす最初の場所」を探せます。重複を調べたり、「ここで値が減った」という場所を探したりするときに使います。

!!! tip "ポイント"
    - 戻り値は**1 つ目の要素**を指すイテレータ（2 つ目ではない）。
    - 見つからなければ `end()`。
    - 条件版では、`pred(前, 後)` の形で書く。値が減った所は `pred = [](a, b) { return a > b; }`。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::adjacent_find {#adjacent_find}

```cpp
template <forward_range R, class Proj = identity,
          indirect_binary_predicate<projected<iterator_t<R>, Proj>,
                                    projected<iterator_t<R>, Proj>> Pred = ranges::equal_to>
constexpr borrowed_iterator_t<R> adjacent_find(R&& r, Pred pred = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 探す場所 |  |
| `pred` | 関数 | 隣り合う 2 つ（前, 後）を受け取って `bool` を返す | `==` |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 条件を満たす最初の「隣り合う組」の 1 つ目を指すイテレータ。無ければ `end()`
- 計算量: O(n)

<div class="anim" data-label="std::ranges::adjacent_find(v)">
1 3 3 5 # 隣り合う 2 つが同じ所を探す
*1 *3 3 5 # 1 と 3 は違う
1 *3 *3 5 # 3 と 3 が同じ。1 つ目の位置を返す
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> rolls = {3, 5, 5, 2, 6, 6, 6};
  auto it = std::ranges::adjacent_find(rolls);
  if (it != rolls.end()) {
    std::println("最初のゾロ目は {} 回目", it - rolls.begin() + 1);
  }
}
```

```text title="実行結果"
最初のゾロ目は 2 回目
```

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  // 毎秒の HP。いつ減ったか？
  std::vector<int> hp = {10, 12, 15, 9, 20};

  // 前より後ろが小さい（= 減った）最初の場所
  auto it = std::ranges::adjacent_find(hp, [](int a, int b) { return a > b; });
  if (it != hp.end()) {
    std::println("{} の次で減った", *it);
  }
}
```

```text title="実行結果"
15 の次で減った
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 同じ入力が連続した（連打） | `adjacent_find(inputs)` |
| スコアが初めて下がった場所 | `adjacent_find(scores, 前 > 後)` |
| 重複の有無（並べ替えてから） | `sort` のあとに `adjacent_find` |

## よくあるミス

??? failure "見つかった位置を「2 つ目」だと思う"
    返るのは**前のほう**の要素です。`{3, 5, 5}` なら最初の 5（添字 1）です。後ろは `std::next(it)` で取れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::unique`](unique.md) | 隣り合う重複を詰める |
| [`std::ranges::search_n`](search_n.md) | 同じ値が n 個続く所を探す |
| [`std::ranges::is_sorted`](is_sorted.md) | 並んでいるかを調べる |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 隣り合う 2 つが同じ（または条件を満たす）最初の場所
    - [x] 戻り値は前のほう
    - [x] 無ければ `end()`

## 関連ページ

- [cpprefjp: std::ranges::adjacent_find](https://cpprefjp.github.io/reference/algorithm/ranges_adjacent_find.html)
- [cppreference: std::ranges::adjacent_find](https://en.cppreference.com/w/cpp/algorithm/ranges/adjacent_find)

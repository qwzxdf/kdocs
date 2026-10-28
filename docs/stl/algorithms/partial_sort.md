---
title: std::ranges::partial_sort
summary: "全部は並べず、先頭の N 件だけを整列させる。"
order: 36
tags:
  - アルゴリズム
---

# std::ranges::partial_sort

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::partial_sort` は、**範囲の先頭 N 件だけを小さい順に整列させる**アルゴリズムです。ランキングの上位 10 件だけが欲しいときに、全体を [`sort`](sort.md) するより速く済みます。残りの要素の順番は不定です。

!!! tip "ポイント"
    - 「上位 N 件が欲しい」ときに使う。全体を並べるより速い（O(n log N)）。
    - 第 2 引数は「**整列させたい範囲の終わり**」。`v.begin() + 3` なら上位 3 件。
    - 元を変えたくないなら、整列結果を別の場所に作る `partial_sort_copy`。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::partial_sort {#partial_sort}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> partial_sort(R&& r, iterator_t<R> middle,
                                              Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 対象の範囲 |  |
| `middle` | イテレータ | 整列させる範囲の終わり。`[begin, middle)` が整列される |  |
| `comp` | 関数 | 並べる順（既定は小さい順） | `<` |
| `proj` | プロジェクション | 比べる前の変換 | そのまま |

- 戻り値: 範囲の終わり（`end()` 相当）
- 計算量: O(n log N)（N は `middle - begin`）

<div class="anim" data-label="std::ranges::partial_sort(v, v.begin() + 2)">
5 1 4 2 3 # 小さい順に 2 件だけ整列
*1 *2 5 4 3 # 先頭 2 件は整列済み。残りは不定
</div>

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {40, 90, 10, 70, 100, 30, 60};

  // 点数が高い順に上位 3 件だけを先頭に並べる
  std::ranges::partial_sort(scores, scores.begin() + 3, std::greater{});
  std::println("上位 3 件: {} {} {}", scores[0], scores[1], scores[2]);
}
```

```text title="実行結果"
上位 3 件: 100 90 70
```

### std::ranges::partial_sort_copy {#partial_sort_copy}

```cpp
template <input_range R1, random_access_range R2, class Comp = ranges::less,
          class Proj1 = identity, class Proj2 = identity>
constexpr partial_sort_copy_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>>
partial_sort_copy(R1&& r, R2&& result_r, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

- 元を変えずに、上位 `result_r.size()` 個を並べて `result_r` に書き込みます

```cpp
#include <algorithm>
#include <array>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> scores = {40, 95, 70, 88, 15};
  std::array<int, 2> top{};
  std::ranges::partial_sort_copy(scores, top, std::greater{});
  std::println("{} / 元はそのまま {}", top, scores);
}
```

```text title="実行結果"
[95, 88] / 元はそのまま [40, 95, 70, 88, 15]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ランキングの上位 10 件 | `partial_sort(scores, scores.begin() + 10, std::greater{})` |
| 近い敵の上位 3 体だけ並べる | `partial_sort(enemies, enemies.begin() + 3, {}, 距離)` |

## よくあるミス

??? failure "残りの要素の順番を当てにする"
    `middle` から後ろの要素は、並んでいません（不定）。全体を整列したいなら `sort` です。

??? failure "N が範囲の大半なのに使う"
    N が大きいと `sort` のほうが速いことがあります。N が全体の 1 割以下のときに効果が出ます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::nth_element`](nth_element.md) | N 番目の要素だけを正しい位置にする（前半は未整列） |
| [`std::ranges::sort`](sort.md) | 全部を並べる |
| [`std::priority_queue`](../containers/priority_queue.md) | 上位 N 件を常に保つ |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭 N 件だけを整列させる
    - [x] 残りは不定
    - [x] 全体の 1 割以下のとき効果が出る

## 関連ページ

- [cpprefjp: std::ranges::partial_sort](https://cpprefjp.github.io/reference/algorithm/ranges_partial_sort.html)
- [cppreference: std::ranges::partial_sort](https://en.cppreference.com/w/cpp/algorithm/ranges/partial_sort)

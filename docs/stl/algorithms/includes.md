---
title: std::ranges::includes
summary: "整列済みの範囲が、別の整列済みの範囲を全部含んでいるかを調べる。"
order: 84
tags:
  - アルゴリズム
---

# std::ranges::includes

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::includes` は、**整列済みの範囲が、別の整列済みの範囲の要素を全部含んでいるか**（部分集合か）を調べます。「レシピに必要な素材が全部そろっているか」のような判定に使えます。

!!! tip "ポイント"
    - `includes(持ち物, 必要なもの)` と、**大きいほうが先**。
    - 2 つの範囲は**整列済み**であること。
    - 結果は `bool`。要素は作らないので、速い（O(n + m)）。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。2 つの範囲は、**整列済み**でなければいけません。

## 関数の詳しい説明

### std::ranges::includes {#includes}

```cpp
template <input_range R1, input_range R2, class Proj1 = identity, class Proj2 = identity,
          class Comp = ranges::less>
constexpr bool includes(R1&& r1, R2&& r2, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1` | 範囲 | 含む側（整列済み） |  |
| `r2` | 範囲 | 含まれる側（整列済み） |  |
| `comp` | 関数 | 整列した順の比較 | `<` |

- 戻り値: `r2` の全要素が `r1` に入っていれば `true`。`r2` が空なら `true`
- 計算量: O(n + m)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> inventory = {1, 2, 3, 5, 8};  // 所持素材の ID（整列済み）
  std::vector<int> recipe_a = {2, 5};
  std::vector<int> recipe_b = {2, 6};

  std::println("レシピ A は作れる？ {}", std::ranges::includes(inventory, recipe_a));
  std::println("レシピ B は作れる？ {}", std::ranges::includes(inventory, recipe_b));
}
```

```text title="実行結果"
レシピ A は作れる？ true
レシピ B は作れる？ false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| クラフトの素材がそろっているか | `includes(inventory, recipe)` |
| 必要なフラグがすべて立っているか | `includes(flags, required)` |

## よくあるミス

??? failure "引数の順番を逆にする"
    `includes(recipe, inventory)` は「素材のほうがレシピを含むか」になり、意図と逆の判定になります。

??? failure "個数を考慮すると思う"
    重複する要素は、個数を数えて比べます（`{1, 1}` を含むには、`1` が 2 個必要）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::set_intersection`](set_intersection.md) | 共通部分を作る |
| [`std::ranges::all_of`](all_of.md) | 全部が条件を満たすか（整列していなくてよい） |
| `std::set` の `contains` | 1 つずつ調べる |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整列済みの部分集合かを調べる
    - [x] 大きいほうが先
    - [x] 個数も考慮される

## 関連ページ

- [cpprefjp: std::ranges::includes](https://cpprefjp.github.io/reference/algorithm/ranges_includes.html)
- [cppreference: std::ranges::includes](https://en.cppreference.com/w/cpp/algorithm/ranges/includes)

---
title: std::ranges::lower_bound
summary: "整列済みの範囲で、値以上の最初の要素の位置を、二分探索で探す。"
order: 38
tags:
  - アルゴリズム
---

# std::ranges::lower_bound

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::lower_bound` は、**整列済みの範囲から、指定した値「以上」になる最初の要素の位置**を、二分探索で探します。見つかった位置は、その値を**整列を保ったまま挿入できる位置**でもあります。

!!! tip "ポイント"
    - 範囲は**整列済み**でなければならない。
    - 「値以上の最初」を返す。同じ値がある場合は、その先頭。
    - 戻り値は位置。**値が見つかったか**は `it != end && *it == value` で確かめる。

!!! info "このページを読む前に"
    [二分探索](../../basics/big-o.md) の考え方が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::lower_bound {#lower_bound}

```cpp
template <forward_range R, class T, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> lower_bound(R&& r, const T& value, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | **ソート済み**の範囲 | 省略不可 |
| `value` | `const T&` | 探す値 | 省略不可 |
| `comp` | 比較関数 | ソートに使ったのと同じ比較 | `<` |
| `proj` | プロジェクション | ソートに使ったのと同じ変換 | そのまま |

- 戻り値: `value` **以上**（比較的に「前ではない」）の最初の要素。無ければ `end()`
- 計算量: O(log n)（vector などランダムアクセスできる範囲の場合）

<div class="anim" data-label="std::ranges::lower_bound(v, 5)">
1 3 5 5 7 9 # 整列済み。5 以上で最初の要素を探す
1 3 *5 5 7 9 # 真ん中を見る。5 以上なので左半分に絞る
1 *3 5 5 7 9 # 3 は 5 より小さいので右に絞る
1 3 *5 5 7 9 # 5 が見つかる。同じ値の最初の位置
</div>

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

struct Item {
  int id;
  std::string name;
};

int main() {
  // id でソート済み
  std::vector<Item> items = {{100, "薬"}, {200, "剣"}, {300, "盾"}};
  auto it = std::ranges::lower_bound(items, 200, {}, &Item::id);
  if (it != items.end() && it->id == 200) {
    std::println("見つかった: {}", it->name);
  }
}
```

```text title="実行結果"
見つかった: 剣
```

!!! note "実際は"
    `lower_bound` は「見つかった」とは限りません（値が無ければ、その値を入れるべき位置が返る）。見つかったか確かめるなら、`it != end()` と「値が等しいか」の両方を見ます。


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-sometimes">たまに</span> | `std::greater{}` | 降順に並んでいる範囲を探す（**並べた順と同じ比較**を渡す） |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバで探す |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ランキングに新しいスコアを挿入する位置 | `lower_bound(scores, new_score)` |
| ソート済みの ID 表から探す | `lower_bound(table, id, {}, &Row::id)` |
| レベルアップに必要な経験値の表から、レベルを求める | `upper_bound` と組み合わせる |

## パフォーマンス

O(log n) で探します。100 万件でも約 20 回の比較で済みます。ただし**範囲が整列済み**であることが前提で、整列されていないと結果は不定です。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 整列されていない範囲に使う | 結果は不定（未定義動作ではないが、正しい答えは返らない） |
| 整列したときと違う `comp` を渡す | 結果は不定 |

## よくあるミス

??? failure "見つからなくても end() 以外が返る"
    `lower_bound` は「値以上の最初」を返すので、値そのものがなくても `end()` とは限りません。`*it == value` まで調べてください。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::upper_bound`](upper_bound.md) | 値より**大きい**最初の位置 |
| [`std::ranges::binary_search`](binary_search.md) | あるかないかだけ |
| [`std::ranges::equal_range`](equal_range.md) | 同じ値の範囲を返す |
| [`std::ranges::find`](find.md) | 整列されていなくても使える（O(n)） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整列済みの範囲で、値以上の最初の位置を探す
    - [x] 挿入位置としても使える
    - [x] 見つかったかは `*it == value` で確かめる

## 関連ページ

- [cpprefjp: std::ranges::lower_bound](https://cpprefjp.github.io/reference/algorithm/ranges_lower_bound.html)
- [cppreference: std::ranges::lower_bound](https://en.cppreference.com/w/cpp/algorithm/ranges/lower_bound)

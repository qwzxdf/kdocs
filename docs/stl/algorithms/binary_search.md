---
title: std::ranges::binary_search
summary: "整列済みの範囲に、値があるかを、二分探索で調べる。"
order: 40
tags:
  - アルゴリズム
---

# std::ranges::binary_search

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::binary_search` は、**整列済みの範囲に、指定した値があるか**を `bool` で答えます。二分探索なので O(log n) で、`find` や `contains`（O(n)）より大きな範囲で速くなります。

!!! tip "ポイント"
    - 範囲は**整列済み**でなければならない。
    - 答えは `bool` だけ。位置が欲しいなら [`lower_bound`](lower_bound.md)。
    - 何度も調べるなら、整列済みの `vector` に `binary_search`、または `unordered_set` の `contains`。

!!! info "このページを読む前に"
    [二分探索](../../basics/big-o.md) の考え方が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::binary_search {#binary_search}

```cpp
template <forward_range R, class T, class Proj = identity, class Comp = ranges::less>
constexpr bool binary_search(R&& r, const T& value, Comp comp = {}, Proj proj = {});
```

- 戻り値: `value` と等しい要素があれば `true`。**位置は分からない**

<div class="anim" data-label="std::ranges::binary_search(v, 5)">
1 3 5 5 7 9 # 整列済み。5 があるか
1 3 *5 5 7 9 # 半分ずつに絞って探す。あれば true
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> walls = {3, 7, 12, 20};  // ソート済み
  std::println("{} {}", std::ranges::binary_search(walls, 12),
               std::ranges::binary_search(walls, 5));
}
```

```text title="実行結果"
true false
```


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-sometimes">たまに</span> | `std::greater{}` | 降順に並んでいる範囲を探す（**並べた順と同じ比較**を渡す） |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバで探す |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 整列済みの ID の表に、IDがあるか | `binary_search(ids, id)` |
| 禁止ワードの辞書に含まれているか | `binary_search(banned, word)` |

## パフォーマンス

O(log n) で探します。100 万件でも約 20 回の比較で済みます。ただし**範囲が整列済み**であることが前提で、整列されていないと結果は不定です。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 整列されていない範囲に使う | 結果は不定（未定義動作ではないが、正しい答えは返らない） |
| 整列したときと違う `comp` を渡す | 結果は不定 |

## よくあるミス

??? failure "整列していない範囲に使う"
    整列していないと、あるのに `false` が返ります。先に `sort` するか、[`is_sorted`](is_sorted.md) で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::lower_bound`](lower_bound.md) | 位置を返す |
| [`std::ranges::contains`](contains.md) | 整列していなくてもよい（O(n)） |
| `std::set::contains` | 木を使うコンテナ |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整列済みの範囲に値があるか、を `bool` で返す
    - [x] 整列済みが前提
    - [x] 位置が欲しいなら `lower_bound`

## 関連ページ

- [cpprefjp: std::ranges::binary_search](https://cpprefjp.github.io/reference/algorithm/ranges_binary_search.html)
- [cppreference: std::ranges::binary_search](https://en.cppreference.com/w/cpp/algorithm/ranges/binary_search)

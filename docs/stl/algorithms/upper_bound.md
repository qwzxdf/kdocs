---
title: std::ranges::upper_bound
summary: "整列済みの範囲で、値より大きい最初の要素の位置を、二分探索で探す。"
order: 39
tags:
  - アルゴリズム
---

# std::ranges::upper_bound

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::upper_bound` は、**整列済みの範囲から、指定した値「より大きい」最初の要素の位置**を、二分探索で探します。同じ値が並んでいるとき、その**一番後ろの次**を指します。

!!! tip "ポイント"
    - 範囲は**整列済み**でなければならない。
    - `lower_bound` との違いは「以上」か「より大きい」か。
    - 同じ値が複数あるとき、その直後に挿入したいなら `upper_bound`。

!!! info "このページを読む前に"
    [二分探索](../../basics/big-o.md) の考え方が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::upper_bound {#upper_bound}

```cpp
template <forward_range R, class T, class Proj = identity, class Comp = ranges::less>
constexpr borrowed_iterator_t<R> upper_bound(R&& r, const T& value, Comp comp = {}, Proj proj = {});
```

- 戻り値: `value` **より大きい**最初の要素。無ければ `end()`

<div class="anim" data-label="std::ranges::upper_bound(v, 5)">
1 3 5 5 7 9 # 整列済み。5 より大きい最初の要素
1 3 5 5 *7 9 # 7 が答え。同じ値の最後の次の位置
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  // 経験値のしきい値（レベル 1, 2, 3, 4 の開始）
  std::vector<int> thresholds = {0, 100, 300, 700};
  int exp = 450;
  auto it = std::ranges::upper_bound(thresholds, exp);
  std::println("Lv.{}", it - thresholds.begin());
}
```

```text title="実行結果"
Lv.3
```


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-sometimes">たまに</span> | `std::greater{}` | 降順に並んでいる範囲を探す（**並べた順と同じ比較**を渡す） |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバで探す |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 同点のスコアの**後ろ**に新記録を挿入する | `upper_bound(scores, new_score)` |
| 経験値の表から現在のレベルを求める | `upper_bound(thresholds, exp) - begin` |

## パフォーマンス

O(log n) で探します。100 万件でも約 20 回の比較で済みます。ただし**範囲が整列済み**であることが前提で、整列されていないと結果は不定です。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 整列されていない範囲に使う | 結果は不定（未定義動作ではないが、正しい答えは返らない） |
| 整列したときと違う `comp` を渡す | 結果は不定 |

## よくあるミス

??? failure "lower_bound と取り違える"
    同じ値がある範囲では、`lower_bound` はその先頭、`upper_bound` はその次を返します。範囲の個数は `upper_bound - lower_bound`（または `equal_range`）です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::lower_bound`](lower_bound.md) | 値**以上**の最初の位置 |
| [`std::ranges::equal_range`](equal_range.md) | `lower_bound` と `upper_bound` を一度に求める |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整列済みの範囲で、値より大きい最初の位置を探す
    - [x] 同じ値の直後に挿入できる位置
    - [x] `lower_bound` とのペアで使う

## 関連ページ

- [cpprefjp: std::ranges::upper_bound](https://cpprefjp.github.io/reference/algorithm/ranges_upper_bound.html)
- [cppreference: std::ranges::upper_bound](https://en.cppreference.com/w/cpp/algorithm/ranges/upper_bound)

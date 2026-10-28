---
title: std::ranges::merge
summary: "整列済みの 2 つの範囲を、整列を保ったまま 1 つに併合する。"
order: 85
tags:
  - アルゴリズム
---

# std::ranges::merge

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::merge` は、**整列済みの 2 つの範囲を整列を保ったまま 1 つの範囲に併合する**アルゴリズムです。[`set_union`](set_union.md) と違い、**重複もすべて残します**。マージソートの「併合」の部分にあたります。

!!! tip "ポイント"
    - 入力の 2 つは**整列済み**であること。出力も整列済みになる。
    - 要素数は両方の合計になる（重複も残る）。
    - 1 つの `vector` の前半と後半を併合するなら [`inplace_merge`](inplace_merge.md)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。2 つの範囲は、**整列済み**でなければいけません。

## 関数の詳しい説明

### std::ranges::merge {#merge}

```cpp
template <input_range R1, input_range R2, weakly_incrementable O, class Comp = ranges::less,
          class Proj1 = identity, class Proj2 = identity>
constexpr merge_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>, O>
merge(R1&& r1, R2&& r2, O result, Comp comp = {}, Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1`, `r2` | 範囲 | **整列済み**の 2 つの範囲 |  |
| `result` | 出力イテレータ | 結果の書き出し先 |  |
| `comp` | 関数 | 整列した順の比較 | `<` |

- 戻り値: `in1`、`in2`、`out` を持つ構造体
- 計算量: O(n + m)

```cpp
#include <algorithm>
#include <iterator>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 3, 5};
  std::vector<int> b = {2, 4, 6};
  std::vector<int> out;

  std::ranges::merge(a, b, std::back_inserter(out));
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5, 6]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 つのイベントキューを時刻順に併合する | `merge(events_a, events_b, out)` |
| 別々に集めた当たり判定のリストを 1 つにする | `merge(list_a, list_b, out)` |

## よくあるミス

??? failure "整列していない範囲に使う"
    整列済みでないと、結果は整列されません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::inplace_merge`](inplace_merge.md) | 1 つの範囲の前半・後半をその場で併合 |
| [`std::ranges::set_union`](set_union.md) | 重複を 1 つにまとめる |
| [`std::ranges::sort`](sort.md) | 連結してから並べ替える方法もある |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整列済み 2 つを併合する
    - [x] 重複も残る
    - [x] 結果も整列済み

## 関連ページ

- [cpprefjp: std::ranges::merge](https://cpprefjp.github.io/reference/algorithm/ranges_merge.html)
- [cppreference: std::ranges::merge](https://en.cppreference.com/w/cpp/algorithm/ranges/merge)

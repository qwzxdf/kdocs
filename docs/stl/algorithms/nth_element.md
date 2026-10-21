---
title: std::ranges::nth_element
summary: "N 番目に小さい要素を、正しい位置に置く（中央値などを速く求める）。"
order: 37
tags:
  - アルゴリズム
---

# std::ranges::nth_element

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::nth_element` は、**N 番目に来る要素を、整列したときの正しい位置に置く**アルゴリズムです。そのとき、N 番目より前は「N 番目以下の値」、後ろは「N 番目以上の値」になりますが、**それぞれの中は整列されません**。中央値や、上位 10% の境目を求めるときに、全体を `sort` するより速く済みます。

!!! tip "ポイント"
    - 平均 O(n)。`sort`（O(n log n)）より速い。
    - 中央値は `nth_element(v, v.begin() + v.size() / 2)` のあとに `v[v.size() / 2]`。
    - 前半と後半は、**整列されていない**。順番が欲しいなら別途 `sort`。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::nth_element {#nth_element}

```cpp
template <random_access_range R, class Comp = ranges::less, class Proj = identity>
constexpr borrowed_iterator_t<R> nth_element(R&& r, iterator_t<R> nth, Comp comp = {}, Proj proj = {});
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 対象 |
| `nth` | イテレータ | この位置にだけ正しい値を置く |
| `comp` / `proj` | | sort と同じ |

- `*nth` は全部並べたときと同じ値になる。`nth` より前はそれ以下、後ろはそれ以上（それぞれの中の順番はバラバラ）
- 計算量: 平均 O(n)

<div class="mem">
<div class="mem-step"><span class="mem-label">前</span><span class="mem-cells"><span>7</span><span>2</span><span>9</span><span>4</span><span>5</span></span></div>
<div class="mem-step"><span class="mem-label">nth = 2 番目</span><span class="mem-cells"><span>2</span><span>4</span><span class="move">5</span><span>9</span><span>7</span></span><span class="mem-note">5 だけが正しい位置。左は 5 以下、右は 5 以上（順番はバラバラ）</span></div>
</div>

<div class="anim" data-label="std::nth_element(b, b + 2, e)">
7 2 9 1 5 8 # v
2 1 *5 7 9 8 # 5 が 3 番目の位置に来る
</div>

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> ping = {30, 250, 45, 60, 38};
  auto mid = ping.begin() + ping.size() / 2;
  std::ranges::nth_element(ping, mid);
  std::println("中央値 {} ms", *mid);
}
```

```text title="実行結果"
中央値 45 ms
```

!!! note "実際は"
    平均値は 1 つの極端な値（250 ms）に引っ張られますが、中央値は引っ張られにくいので、通信遅延やフレーム時間の評価に向いています。


## フラグ・オプション

| 引数 | 重要度 | 渡すもの | 意味 |
| --- | --- | --- | --- |
| `comp` | <span class="rank rank-sometimes">たまに</span> | `std::greater{}` | 大きい順での N 番目にする |
| `proj` | <span class="rank rank-sometimes">たまに</span> | `&Type::member` | メンバで比べる |

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 中央値のスコアを求める | `nth_element(scores, mid)` のあとに `scores[mid]` |
| 上位 10% に入るしきい値を求める | `nth_element(scores, 90 パーセンタイルの位置)` |
| 近い順に 5 体だけ選ぶ（順番は気にしない） | `nth_element(enemies, begin() + 5, {}, 距離)` |

## よくあるミス

??? failure "結果が全部並ぶと思う"
    並ぶのは N 番目の位置だけです。前半・後半の中は不定です。

??? failure "end() を N に渡す"
    N は `[begin, end)` の中の位置です。`end()` を渡すと何もしません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::partial_sort`](partial_sort.md) | 先頭 N 件を整列させる |
| [`std::ranges::sort`](sort.md) | 全体を整列させる |
| [`std::ranges::min_element`](min_element.md) | 1 番目（最小）だけでよいとき |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] N 番目を正しい位置に置く
    - [x] 前後の中は未整列
    - [x] 平均 O(n) で中央値が取れる

## 関連ページ

- [cpprefjp: std::ranges::nth_element](https://cpprefjp.github.io/reference/algorithm/ranges_nth_element.html)
- [cppreference: std::ranges::nth_element](https://en.cppreference.com/w/cpp/algorithm/ranges/nth_element)

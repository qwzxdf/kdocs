---
title: std::ranges::swap_ranges
summary: "2 つの範囲の要素を、先頭から順に入れ替える。"
order: 51
tags:
  - アルゴリズム
---

# std::ranges::swap_ranges

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::swap_ranges` は、**2 つの範囲の要素を、先頭から順に 1 つずつ入れ替える**アルゴリズムです。同じ長さの 2 つの配列の中身を、丸ごと交換できます。

!!! tip "ポイント"
    - 短いほうの長さまで入れ替える。
    - コンテナ全体を交換するなら、`a.swap(b)` のほうが速い（ポインターを入れ替えるだけ）。
    - 同じ範囲の中で重ねて使ってはいけない。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::swap_ranges {#swap_ranges}

```cpp
template <input_range R1, input_range R2>
constexpr swap_ranges_result<borrowed_iterator_t<R1>, borrowed_iterator_t<R2>>
swap_ranges(R1&& r1, R2&& r2);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r1`, `r2` | 範囲 | 入れ替える 2 つの範囲（重なっていないこと） |

- 戻り値: `in1` と `in2`（入れ替えた最後の次の位置）の組
- 計算量: 短いほうの長さ n に対して n 回の `swap`

```cpp
#include <algorithm>
#include <array>
#include <print>

int main() {
  std::array<int, 3> a = {1, 2, 3};
  std::array<int, 3> b = {7, 8, 9};

  std::ranges::swap_ranges(a, b);
  std::println("{} {}", a, b);
}
```

```text title="実行結果"
[7, 8, 9] [1, 2, 3]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 前のフレームと今のフレームのバッファを入れ替える | `swap_ranges(prev, curr)`（大きいなら `swap`） |
| 2 つのパーティの同じ位置のメンバーを入れ替える | `swap_ranges(party_a, party_b)` |

## よくあるミス

??? failure "長さが違う"
    短いほうの長さまでしか入れ替えません。長いほうの余りは変わらないので、意図しない中身になります。

## 類似

| 名前 | 違い |
| --- | --- |
| `a.swap(b)`（コンテナ） | コンテナ全体を一瞬で交換する |
| [`std::swap`](../utilities/swap.md) | 2 つの値を交換する |
| [`std::ranges::reverse`](reverse.md) | 1 つの範囲の並びを逆にする |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 2 つの範囲を先頭から順に入れ替える
    - [x] 短いほうの長さまで
    - [x] コンテナ全体なら `a.swap(b)`

## 関連ページ

- [cpprefjp: std::ranges::swap_ranges](https://cpprefjp.github.io/reference/algorithm/ranges_swap_ranges.html)
- [cppreference: std::ranges::swap_ranges](https://en.cppreference.com/w/cpp/algorithm/ranges/swap_ranges)

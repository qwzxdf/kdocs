---
title: std::ranges::fold_right_last
summary: "初期値なしで、範囲を右から畳み込む。"
order: 900
tags:
  - アルゴリズム
---

# std::ranges::fold_right_last

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

合計や最大値のように、列を 1 つの値にまとめたいとき、初期値を別に用意するのが面倒なことがあります。`fold_right_last` は最後の要素を初期値にして右から畳み込みます。空の範囲では何も返せないので、戻り値は `optional` です。

!!! tip "ポイント"
    - 初期値の代わりに最後の要素を使う。
    - 戻り値は `std::optional`。空なら `nullopt`。
    - 左から畳むのは [`fold_left_first`](fold_left.md)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_right_last {#fold_right_last}

```cpp
template <ranges::bidirectional_range R, class F>
constexpr auto ranges::fold_right_last(R&& r, F f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 畳み込む範囲（双方向以上） |
| `f` | 関数 | 2 引数の関数。`f(要素, 累積値)` の形で呼ばれる |

- 戻り値: `std::optional<T>`（空の範囲なら `nullopt`）
- 計算量: 線形（`f` を `size - 1` 回呼ぶ）


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  auto sum = std::ranges::fold_right_last(v, std::plus<>{});
  std::println("{}", *sum);
  std::vector<int> empty;
  std::println("{}", std::ranges::fold_right_last(empty, std::plus<>{}).has_value());
}
```

```text title="実行結果"
10
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| リストの要素を右結合で 1 つにまとめる | `std::ranges::fold_right_last(v, std::plus<>{})` |

## よくあるミス

??? failure "空の範囲に `.value()` を呼ぶ"
    空の範囲だと `nullopt` が返ります。`*r` や `.value()` を呼ぶ前に値があるか確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fold_right`](fold_right.md) | 初期値を渡す版 |
| [`fold_left_first`](fold_left.md) | 左から畳む版 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 最後の要素を初期値にして右から畳む
    - [x] 戻り値は optional
    - [x] 空なら nullopt

## 関連ページ

- [cpprefjp: std::ranges::fold_right_last](https://cpprefjp.github.io/reference/algorithm/ranges_fold_right_last.html)
- [cppreference: std::ranges::fold_right_last](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_right_last)

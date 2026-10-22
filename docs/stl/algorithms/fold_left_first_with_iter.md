---
title: std::ranges::fold_left_first_with_iter
summary: "初期値なしで左から畳み込み、結果と読んだ位置を返す。"
order: 900
tags:
  - アルゴリズム
---

# std::ranges::fold_left_first_with_iter

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

`fold_left_with_iter` の、初期値なし版です。先頭の要素を初期値にします。空の範囲では結果が `nullopt` になります。

!!! tip "ポイント"
    - 先頭の要素を初期値にする。
    - 結果は `optional`。終端イテレータと一緒に返る。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_left_first_with_iter {#fold_left_first_with_iter}

```cpp
template <input_iterator I, sentinel_for<I> S, class F>
constexpr auto ranges::fold_left_first_with_iter(I first, S last, F f);

template <input_range R, class F>
constexpr auto ranges::fold_left_first_with_iter(R&& r, F f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last / r` | 範囲 | 畳み込む範囲 |
| `f` | 関数 | `f(累積値, 要素)` の形で呼ばれる |

- 戻り値: `in`（読み終えた位置）と `value`（`std::optional<T>`）をもつ構造体
- 計算量: 線形


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {5, 1, 2};
  auto [it, r] = std::ranges::fold_left_first_with_iter(v, std::plus<>{});
  std::println("{} {}", *r, it == v.end());
}
```

```text title="実行結果"
8 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 先頭を初期値にして合計し、読み終えた位置も使う | `auto [it, r] = std::ranges::fold_left_first_with_iter(v, std::plus<>{});` |

## よくあるミス

??? failure "空の範囲で値を取り出す"
    `r` が `nullopt` のことがあります。`if (r)` で確かめてから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fold_left_with_iter`](fold_left_with_iter.md) | 初期値を渡す版 |
| [`fold_left_first`](fold_left.md) | 結果だけ返す版 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 初期値なしで左から畳む
    - [x] 結果は optional
    - [x] 終端も返る

## 関連ページ

- [cpprefjp: std::ranges::fold_left_first_with_iter](https://cpprefjp.github.io/reference/algorithm/ranges_fold_left_first_with_iter.html)
- [cppreference: std::ranges::fold_left_first_with_iter](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_left_first_with_iter)

---
title: std::ranges::fold_left_with_iter
summary: "左から畳み込み、結果と「どこまで読んだか」の両方を返す。"
order: 900
tags:
  - アルゴリズム
---

# std::ranges::fold_left_with_iter

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

`fold_left` は結果の値だけ返します。入力がイテレータのペア（ストリームなど）のときは、「どこまで読み進めたか」も知りたくなります。`fold_left_with_iter` は、結果と終端イテレータを一緒に返します。

!!! tip "ポイント"
    - 戻り値は `{in, value}` の組（構造化束縛で受けると読みやすい）。
    - 初期値なしの版は [`fold_left_first_with_iter`](fold_left_first_with_iter.md)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_left_with_iter {#fold_left_with_iter}

```cpp
template <input_iterator I, sentinel_for<I> S, class T, class F>
constexpr auto ranges::fold_left_with_iter(I first, S last, T init, F f);

template <input_range R, class T, class F>
constexpr auto ranges::fold_left_with_iter(R&& r, T init, F f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last / r` | 範囲 | 畳み込む範囲 |
| `init` | T | 初期値 |
| `f` | 関数 | `f(累積値, 要素)` の形で呼ばれる |

- 戻り値: `in`（読み終えた位置のイテレータ）と `value`（結果）をもつ構造体
- 計算量: 線形


## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  auto [it, sum] = std::ranges::fold_left_with_iter(v, 0, std::plus<>{});
  std::println("{} {}", sum, it == v.end());
}
```

```text title="実行結果"
10 true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 入力ストリームを合計しつつ、読んだ位置も使う | `auto [it, sum] = std::ranges::fold_left_with_iter(v, 0, std::plus<>{});` |

## よくあるミス

??? failure "戻り値を 1 つの値と思う"
    結果は 2 つの要素をもつ構造体です。値だけ欲しいなら `fold_left` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fold_left`](fold_left.md) | 結果の値だけ返す版 |
| [`fold_left_first_with_iter`](fold_left_first_with_iter.md) | 初期値なしの版 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] fold_left の結果と終端を両方返す
    - [x] 構造化束縛で受ける
    - [x] 初期値は引数で渡す

## 関連ページ

- [cpprefjp: std::ranges::fold_left_with_iter](https://cpprefjp.github.io/reference/algorithm/ranges_fold_left_with_iter.html)
- [cppreference: std::ranges::fold_left_with_iter](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_left_with_iter)

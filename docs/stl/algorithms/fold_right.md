---
title: std::ranges::fold_right
summary: "範囲を右から畳み込んで、1 つの値にする。"
order: 24
tags:
  - アルゴリズム
---

# std::ranges::fold_right

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

右から左へ畳み込む処理が、C++23 の `std::ranges::fold_right` です。`fold_left` が `((init op a) op b) op c` と左から畳むのに対し、`fold_right` は `a op (b op (c op init))` と右から畳みます。演算が結合法則を満たさない（引き算など）とき、結果が違います。

!!! tip "ポイント"
    - 右から左へ畳み込む（`a op (b op (c op init))`）
    - 初期値が必須。なければ `fold_right_last`
    - 演算の引数の順は `(要素, 蓄積した値)`
    - C++23

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_right {#fold_right}

<span class="ver ver-23">C++23</span>

```cpp
template <bidirectional_range R, class T, class F>
constexpr auto fold_right(R&& r, T init, F f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 双方向範囲 | 畳む対象 |
| `init` | `T` | 初期値（一番右に置かれる） |
| `f` | 二項関数 | `f(要素, 蓄積した値)` |

`fold_left` とは、`f` の引数の順番が逆です。`fold_left` は `f(蓄積した値, 要素)`、`fold_right` は `f(要素, 蓄積した値)` です。

`{1, 2, 3}` を引き算で畳むと、`fold_left` は `((0 - 1) - 2) - 3 = -6`、`fold_right` は `1 - (2 - (3 - 0)) = 2` です。

足し算や掛け算のように、結合法則を満たす演算では、どちらでも同じです。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3};

  // 右から畳む: 1 - (2 - (3 - 0))
  std::println("fold_right: {}", std::ranges::fold_right(v, 0, std::minus<>()));
  // 左から畳む: ((0 - 1) - 2) - 3
  std::println("fold_left:  {}", std::ranges::fold_left(v, 0, std::minus<>()));

  // 結合法則を満たす演算なら同じ
  std::println("合計: {}", std::ranges::fold_right(v, 0, std::plus<>()));
}
```

```text title="実行結果"
fold_right: 2
fold_left:  -6
合計: 6
```

## ゲームでの使いどころ

右結合の演算（関数の合成、リストの構築）を畳むときに使います。

## よくあるミス

??? failure "引数の順を fold_left と同じだと思う"
    `(要素, 蓄積した値)` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fold_right_last`](fold_right_last.md) | 初期値なし |
| [`fold_left`](fold_left.md) | 左から畳む |
| [`accumulate`](accumulate.md) | 従来の左畳み込み |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::fold_right](https://cpprefjp.github.io/reference/algorithm/ranges_fold_right.html)
- [cppreference: std::ranges::fold_right](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_right)

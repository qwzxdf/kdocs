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

`fold_left_first_with_iter` は、`fold_left_with_iter` の、初期値なし版です。最初の要素を初期値にして畳み、結果を `std::optional` で、読み終えた位置と一緒に返します。

!!! tip "ポイント"
    - 最初の要素を初期値として、左から畳む
    - 戻り値は、読み終えた位置 `in` と、`std::optional` の `value`
    - 空の範囲では、`value` が空
    - C++23

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_left_first_with_iter {#fold_left_first_with_iter}

<span class="ver ver-23">C++23</span>

```cpp
template <input_range R, class F>
constexpr auto fold_left_first_with_iter(R&& r, F f);
// 戻り値: fold_left_first_with_iter_result<borrowed_iterator_t<R>, optional<...>>
```

`{3, 1, 4}` を `std::max` で畳むと、最初の `3` が初期値で、`max(max(3, 1), 4) = 4` です。

空の範囲では、`value` が `nullopt` で、`in` は `last` です。

`fold_left_first`（`_with_iter` なし）は、値の `optional` だけを返します。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {3, 1, 4, 1, 5};

  const auto [in, value] = std::ranges::fold_left_first_with_iter(v, [](int a, int b) { return a > b ? a : b; });
  std::println("最大: {}", *value);
  std::println("読み終えた位置: {}", in - v.begin());

  const std::vector<int> none;
  std::println("空: {}", std::ranges::fold_left_first_with_iter(none, std::plus<>()).value.has_value());
}
```

```text title="実行結果"
最大: 5
読み終えた位置: 5
空: false
```

## ゲームでの使いどころ

最大・最小のように、初期値が自然に決まらない畳み込みで、位置も使うときに使います。

## よくあるミス

??? failure "空の範囲で * を使う"
    `nullopt` の取り出しは未定義です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fold_left_with_iter`](fold_left_with_iter.md) | 初期値あり |
| [`fold_right_last`](fold_right_last.md) | 右から畳む版 |
| `std::optional` | 空を表す |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::fold_left_first_with_iter](https://cpprefjp.github.io/reference/algorithm/ranges_fold_left_first_with_iter.html)
- [cppreference: std::ranges::fold_left_first_with_iter](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_left_first_with_iter)

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

`fold_right` は初期値が要りますが、`std::ranges::fold_right_last` は、最後の要素を初期値にして、残りを右から畳みます。範囲が空なら、結果がないので `std::optional` で返します。

!!! tip "ポイント"
    - 最後の要素を初期値として、右から畳む
    - 戻り値は `std::optional`（空の範囲は空）
    - `fold_right` の、初期値なし版
    - C++23

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_right_last {#fold_right_last}

<span class="ver ver-23">C++23</span>

```cpp
template <bidirectional_range R, class F>
constexpr auto fold_right_last(R&& r, F f);   // 戻り値は optional<...>
```

`{1, 2, 3, 4}` を引き算で畳むと、`1 - (2 - (3 - 4)) = -2` です。最後の要素 `4` が初期値の役目をします。

要素が 1 つなら、その要素がそのまま結果です。0 個なら `std::nullopt` です。

`fold_left_first` が、同じ考え方の左畳み込みです。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3, 4};
  const auto r = std::ranges::fold_right_last(v, std::minus<>());
  std::println("{}", *r);  // 1 - (2 - (3 - 4))

  const std::vector<int> one = {7};
  std::println("1 要素: {}", *std::ranges::fold_right_last(one, std::minus<>()));

  const std::vector<int> none;
  std::println("空: {}", std::ranges::fold_right_last(none, std::minus<>()).has_value());
}
```

```text title="実行結果"
-2
1 要素: 7
空: false
```

## ゲームでの使いどころ

初期値が自然に決まらない畳み込み（最大値の探索など）で使います。

## よくあるミス

??? failure "空の範囲で * を使う"
    空だと `nullopt` で、値の取り出しが未定義です。`has_value()` で確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fold_right`](fold_right.md) | 初期値あり |
| [`fold_left_first_with_iter`](fold_left_first_with_iter.md) | 左から畳む版 |
| `std::optional` | 空の可能性を表す |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::fold_right_last](https://cpprefjp.github.io/reference/algorithm/ranges_fold_right_last.html)
- [cppreference: std::ranges::fold_right_last](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_right_last)

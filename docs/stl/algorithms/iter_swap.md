---
title: std::iter_swap
summary: "2 つのイテレータが指す要素を入れ替える。"
order: 71
tags:
  - アルゴリズム
---

# std::iter_swap

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <algorithm>`
</div>

`std::iter_swap` は、**2 つのイテレータが指す要素を入れ替える**関数です。`std::swap(*a, *b)` と同じ意味ですが、イテレータの型が違ってもよく、プロキシ型のイテレータ（`vector<bool>` など）にも対応します。

!!! tip "ポイント"
    - 普通は `std::swap(v[i], v[j])` で足りる。
    - ソートなどのアルゴリズムの部品として使われる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::iter_swap {#iter_swap}

```cpp
template <class ForwardIt1, class ForwardIt2>
constexpr void iter_swap(ForwardIt1 a, ForwardIt2 b);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a`, `b` | イテレータ | 入れ替える要素を指す 2 つのイテレータ |

- 戻り値: なし
- 計算量: O(1)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 2};
  std::vector<int> b = {9, 8};

  std::iter_swap(a.begin(), b.begin());  // 先頭どうしを入れ替える
  std::println("{} {}", a, b);
}
```

```text title="実行結果"
[9, 2] [1, 8]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 並べ替えの自作で要素を入れ替える | `std::iter_swap(it1, it2)` |

## よくあるミス

??? failure "同じ要素に使う"
    同じ位置を指していても安全ですが、何も起きません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::swap`](../utilities/swap.md) | 2 つの値を入れ替える |
| [`std::ranges::swap_ranges`](swap_ranges.md) | 範囲どうしを入れ替える |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] イテレータが指す要素を入れ替える
    - [x] `swap(*a, *b)` と同じ
    - [x] 自作アルゴリズムの部品

## 関連ページ

- [cpprefjp: std::iter_swap](https://cpprefjp.github.io/reference/algorithm/iter_swap.html)
- [cppreference: std::iter_swap](https://en.cppreference.com/w/cpp/algorithm/iter_swap)

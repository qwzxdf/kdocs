---
title: std::ranges::find_end
summary: "範囲の中で、別の範囲の並びが最後に現れる場所を探す。"
order: 66
tags:
  - アルゴリズム
---

# std::ranges::find_end

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

`std::ranges::find_end` は、**ある範囲の中から、別の範囲と同じ並びが「最後に」現れる場所**を探します。名前に反して「終わりを探す」のではなく、[`search`](search.md) の「最後の一致」版です。

!!! tip "ポイント"
    - `search` は最初の一致、`find_end` は**最後の一致**。
    - 戻り値は見つかった部分の範囲。見つからなければ空。
    - 名前が紛らわしい（`find_last` は 1 つの値の最後）。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::find_end {#find_end}

```cpp
template <forward_range R1, forward_range R2, class Pred = ranges::equal_to,
          class Proj1 = identity, class Proj2 = identity>
constexpr borrowed_subrange_t<R1> find_end(R1&& r1, R2&& r2, Pred pred = {},
                                           Proj1 proj1 = {}, Proj2 proj2 = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r1` | 範囲 | 探す場所 |  |
| `r2` | 範囲 | 探す並び |  |
| `pred` | 関数 | 「等しい」の判定 | `==` |

- 戻り値: 最後に一致した部分の範囲。見つからなければ空
- 計算量: 最悪 O(n·m)

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 1, 2, 3, 4};
  std::vector<int> sub = {1, 2, 3};

  auto last = std::ranges::find_end(v, sub);
  std::println("最後に現れる位置: {}", last.begin() - v.begin());
}
```

```text title="実行結果"
最後に現れる位置: 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログの中で、最後に「接続」→「切断」の並びが出た場所 | `find_end(log, pattern)` |

## よくあるミス

??? failure "名前から「終わりの位置を返す」と思う"
    返るのは「最後の一致」の範囲です。終わりを返すわけではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::search`](search.md) | 最初の一致を探す |
| [`std::ranges::find_last`](find_last.md) | 1 つの値の最後の一致を探す |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 並びの「最後の一致」を探す
    - [x] 最初の一致は `search`
    - [x] 見つからなければ空の範囲

## 関連ページ

- [cpprefjp: std::ranges::find_end](https://cpprefjp.github.io/reference/algorithm/ranges_find_end.html)
- [cppreference: std::ranges::find_end](https://en.cppreference.com/w/cpp/algorithm/ranges/find_end)

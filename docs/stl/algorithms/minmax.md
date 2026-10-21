---
title: std::minmax
summary: "最小と最大を、1 回の走査で両方求める。"
order: 28
tags:
  - アルゴリズム
---

# std::minmax

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <algorithm>`
</div>

`std::minmax` は、**最小値と最大値を一度に返す**関数です。別々に `min` と `max` を呼ぶより、データを 1 回なめるだけで済みます。C++20 の `std::ranges::minmax` は範囲を丸ごと渡せます。

!!! tip "ポイント"
    - 戻り値は `{最小, 最大}` の組。構造化束縛で受けると読みやすい。
    - 範囲を 2 回なめたくないとき（データが大きいとき）に使う。
    - 2 引数版は**参照の組**を返す。一時的な値を渡して保存すると危険。

## 関数の詳しい説明

### std::minmax {#minmax}

```cpp
template <class T>
constexpr std::pair<const T&, const T&> minmax(const T& a, const T& b);
template <class T>
constexpr std::pair<T, T> minmax(std::initializer_list<T> ilist);
```

- 戻り値: `{小さいほう, 大きいほう}` の `pair`

```cpp
#include <algorithm>
#include <print>

int main() {
  auto [lo, hi] = std::minmax({7, 2, 9, 4});
  std::println("{} 〜 {}", lo, hi);
}
```

```text title="実行結果"
2 〜 9
```

!!! warning
    2 引数版は**参照の pair** を返すので、`auto [lo, hi] = std::minmax(a + 1, b);` のように一時的な値を渡すと、すぐ消える値を参照してしまいます（未定義動作）。

### std::ranges::minmax <span class="ver ver-20">C++20</span> {#ranges-minmax data-toc-label="std::ranges::minmax"}

```cpp
template <input_range R, class Proj = identity, class Comp = ranges::less>
constexpr minmax_result<range_value_t<R>> minmax(R&& r, Comp comp = {}, Proj proj = {});
```

- 戻り値: `.min` と `.max` を持つ構造体。1 回なめるだけで両方取れる

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> heights = {3, 8, 1, 6};
  auto [low, high] = std::ranges::minmax(heights);
  std::println("最低 {} / 最高 {}", low, high);
}
```

```text title="実行結果"
最低 1 / 最高 8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| グラフの縦軸の範囲（最小〜最大） | `auto [lo, hi] = std::ranges::minmax(values)` |
| 当たり判定の AABB（最小点と最大点） | 各軸で `minmax` を使う |

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲で `std::ranges::minmax` | 未定義動作 |

## よくあるミス

??? failure "一時的な値の参照を保存する"
    2 引数版は参照を返すので、`auto [lo, hi] = std::minmax(a + 1, b);` のように一時的な値を渡すと、すぐ消える値を参照してしまいます。値を保存したいなら `std::pair<int, int>` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::min`](min.md) / [`std::max`](max.md) | 片方だけ求める |
| [`std::ranges::minmax_element`](minmax_element.md) | 両方の**位置**を返す |

## コンパイラ対応

`std::minmax` は C++11、`std::ranges::minmax` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `minmax` は最小と最大を一度に返す
    - [x] 構造化束縛で `auto [lo, hi]`
    - [x] 空の範囲は未定義動作

## 関連ページ

- [cpprefjp: std::minmax](https://cpprefjp.github.io/reference/algorithm/minmax.html)
- [cppreference: std::minmax](https://en.cppreference.com/w/cpp/algorithm/minmax)

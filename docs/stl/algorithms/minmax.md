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

配列の最小値と最大値の両方が欲しい。`min` と `max` を別々に呼ぶと、配列を 2 回なめることになります。データが大きいと、無駄が目立ちます。`std::minmax` は、最小と最大を一度に返す関数です。C++20 の `std::ranges::minmax` は、範囲を丸ごと渡せます。

!!! tip "ポイント"
    - 戻り値は `{最小, 最大}` の組。構造化束縛で受けると読みやすい。
    - 範囲を 2 回なめたくないとき（データが大きいとき）に使う。
    - 2 引数版は**参照の組**を返す。一時的な値を渡して保存すると危険。

!!! info "このページを読む前に"
    [`std::min`](min.md) と [`std::max`](max.md) を先に読んでください。`minmax` は、その 2 つをまとめたものです。

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

座標の集まりから、囲む矩形（AABB）を求めるときに使います。x の最小・最大、y の最小・最大をそれぞれ `ranges::minmax` で一度に求められます。

2 つの値を小さい順に並べ直すのにも使います。`auto [lo, hi] = std::minmax(a, b);` で、`lo` が小さいほう、`hi` が大きいほうになります。範囲選択の始点と終点を整えるときに便利です。

2 引数版は参照の組を返すので、一時的な値を渡して保存すると、ぶら下がります。

## 未定義動作・例外

| やったこと | 結果 |
| --- | --- |
| 空の範囲で `std::ranges::minmax` | 未定義動作 |

## よくあるミス

??? failure "一時的な値の参照を保存する"
    2 引数版は参照を返すので、`auto [lo, hi] = std::minmax(a + 1, b);` のように一時的な値を渡すと、すぐ消える値を参照してしまいます。値を保存したいなら `std::pair<int, int>` で受けます。

??? failure "一時的な値を渡して、参照がぶら下がる"
    `auto r = std::minmax(f(), g());` は、`f()` と `g()` が一時的な値なので、`r` が行の終わりで消えた値を指します。値を変数に受けてから渡します。

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

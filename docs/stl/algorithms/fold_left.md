---
title: std::ranges::fold_left
summary: "範囲を左から畳み込んで、1 つの値にする（`accumulate` の範囲版）。"
order: 23
tags:
  - アルゴリズム
---

# std::ranges::fold_left

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <algorithm>`
</div>

`std::ranges::fold_left` は、**範囲の要素を左から順に、関数で畳み込んで 1 つの値にする**アルゴリズムです。[`std::accumulate`](accumulate.md) の C++23 版で、範囲をそのまま渡せ、結果の型が自然に決まります。初期値を使わない `fold_left_first` もあります。

!!! tip "ポイント"
    - `fold_left(v, 0, std::plus{})` で合計。関数を変えれば、積、最大値、連結なども同じ形で書ける。
    - アキュムレーターの型は、**初期値と関数の結果の型**から決まる（`accumulate` の「初期値の型の罠」が減る）。
    - 初期値なしで先頭の要素から畳み込むなら `fold_left_first`（空の範囲では `std::optional` が空になる）。

!!! info "このページを読む前に"
    [ラムダ式](../../basics/lambda.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::ranges::fold_left <span class="ver ver-23">C++23</span> {#fold_left data-toc-label="std::ranges::fold_left"}

```cpp
template <input_range R, class T, class F>
constexpr auto fold_left(R&& r, T init, F f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | まとめる範囲 |
| `init` | `T` | 初期値 |
| `f` | 関数 | `(これまでの結果, 次の要素)` → 新しい結果。**省略できない**（合計なら `std::plus{}`） |

- 戻り値: まとめた結果

```cpp
#include <algorithm>
#include <functional>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<int> scores = {70, 85, 90};
  std::println("{}", std::ranges::fold_left(scores, 0, std::plus{}));

  std::vector<std::string> words = {"Game", "Over"};
  auto joined = std::ranges::fold_left(
      words, std::string(),
      [](std::string acc, const std::string& w) { return acc + w + " "; });
  std::println("[{}]", joined);
}
```

```text title="実行結果"
245
[Game Over ]
```

### std::ranges::fold_left_first <span class="ver ver-23">C++23</span> {#fold_left_first data-toc-label="std::ranges::fold_left_first"}

```cpp
template <input_range R, class F>
constexpr auto fold_left_first(R&& r, F f);
```

- 最初の要素を初期値にして畳み込みます。戻り値は `std::optional`（空なら値なし）

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {4, 9, 2};
  auto best = std::ranges::fold_left_first(v, [](int a, int b) { return a > b ? a : b; });
  std::println("{}", best.value());
}
```

```text title="実行結果"
9
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| HP の合計 | `fold_left(hp, 0, std::plus{})` |
| 最大のダメージ | `fold_left_first(damages, std::ranges::max)` |
| 文字列の連結 | `fold_left(parts, std::string{}, 連結)` |

## よくあるミス

??? failure "古い環境で使えない"
    C++23 の機能です。GCC 13 / MSVC 19.34 以降が必要です。使えないときは `std::accumulate` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::accumulate`](accumulate.md) | 従来の書き方 |
| [`std::ranges::fold_right`](fold_right.md) | 右から畳み込む |
| [`std::reduce`](reduce.md) | 順序を問わない合計 |

## コンパイラ対応

C++23 の機能です。GCC 13 / Clang 19 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 左から畳み込む
    - [x] `fold_left_first` は初期値なし
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::fold_left](https://cpprefjp.github.io/reference/algorithm/ranges_fold_left.html)
- [cppreference: std::ranges::fold_left](https://en.cppreference.com/w/cpp/algorithm/ranges/fold)

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

配列を畳み込んで 1 つの値にする。`std::accumulate` は、初期値の型が結果の型を決めてしまうので、`double` の合計に `0` を渡すと整数のまま足される、という罠があります。C++23 の `std::ranges::fold_left` は、範囲を左から順に関数で畳み込む `accumulate` の後継です。範囲をそのまま渡せ、結果の型が自然に決まります。

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

合計、積、最大値、文字列の連結など、1 つの値にまとめる処理に使います。`std::ranges::fold_left(v, 0.0, std::plus{})` と書くと、`double` の合計になります。

初期値を与えない `fold_left_first` は、最初の要素を初期値にします。空のときは `std::optional` が空で返るので、最大値の計算で「初期値に何を入れるか」に悩まなくて済みます。

`views` と組み合わせて、`enemies | views::transform(&Enemy::hp) | ranges::fold_left(...)` のように、変換した値を合計できます。C++23 に対応していない環境では、`accumulate` を使います。

## よくあるミス

??? failure "古い環境で使えない"
    C++23 の機能です。GCC 13 / MSVC 19.34 以降が必要です。使えないときは `std::accumulate` を使います。

??? failure "空の範囲で初期値が返る"
    範囲が空のとき、`fold_left` は初期値を返します。最大値の計算で初期値に `0` を渡すと、空のときに `0` が答えになります。`fold_left_first` を使うと、空は `nullopt` で区別できます。

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

---
title: std::accumulate / std::ranges::fold_left
tags:
  - アルゴリズム
---

# std::accumulate / std::ranges::fold_left

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-23">C++23</span>
`#include <numeric>` / `#include <algorithm>`
</div>

`std::accumulate` と `std::ranges::fold_left` は、<strong>範囲の要素を順に 1 つの値にまとめる（畳み込む）</strong>関数です。何も指定しなければ合計を計算し、関数を渡せば掛け算や最大値、文字列の連結など好きなまとめ方ができます。`accumulate` は昔からある関数、`fold_left` は C++23 で入った ranges 版です。

!!! tip "ポイント"
    - <strong>合計なら `std::ranges::fold_left(v, 0, std::plus{})` か `std::accumulate(v.begin(), v.end(), 0)`。</strong>
    - 初期値の型が結果の型になる。float の合計に `0` を渡すと int で計算されて小数が消える（**必ず `0.0f`**）。
    - 単純な合計なら、for ループで書いても読みやすさはほぼ同じ。無理に使わなくていい。

## 関数一覧

| 関数 | 重要度 | 何をする | ヘッダ |
| --- | --- | --- | --- |
| [`std::accumulate`](#accumulate) | <span class="rank rank-sometimes">たまに</span> | 初期値から順に足し込む（関数も指定可） | `<numeric>` |
| [`std::ranges::fold_left`](#fold_left) | <span class="rank rank-sometimes">たまに</span> | ranges 版の畳み込み <span class="ver ver-23">C++23</span> | `<algorithm>` |
| [`std::reduce`](#reduce) | <span class="rank rank-rare">知ってるだけ</span> | 順番を問わない畳み込み（並列化できる） <span class="ver ver-17">C++17</span> | `<numeric>` |
| [`std::ranges::fold_left_first`](#fold_left_first) | <span class="rank rank-rare">知ってるだけ</span> | 最初の要素を初期値にする <span class="ver ver-23">C++23</span> | `<algorithm>` |
| [`std::ranges::fold_right`](#fold_right) | <span class="rank rank-rare">知ってるだけ</span> | 右（末尾）から畳み込む <span class="ver ver-23">C++23</span> | `<algorithm>` |

計算量はどれも O(n) です。

## よくある使い方

```cpp
#include <algorithm>
#include <functional>
#include <numeric>
#include <print>
#include <ranges>
#include <vector>

struct Item {
  int price;
  float weight;
};

int main() {
  std::vector<Item> bag = {{100, 1.5f}, {300, 0.5f}, {50, 2.0f}};

  // 合計金額（プロジェクションは無いので transform してから）
  int total = std::accumulate(bag.begin(), bag.end(), 0,
                              [](int sum, const Item& i) { return sum + i.price; });

  // 合計重量（初期値は 0.0f にする）
  float weight = std::ranges::fold_left(
      bag | std::views::transform(&Item::weight), 0.0f, std::plus{});

  std::println("{} G / {} kg", total, weight);
}
```

```text title="実行結果"
450 G / 4 kg
```

## 関数の詳しい説明

### std::accumulate {#accumulate}

```cpp
template <class InputIt, class T>
constexpr T accumulate(InputIt first, InputIt last, T init);
template <class InputIt, class T, class BinaryOp>
constexpr T accumulate(InputIt first, InputIt last, T init, BinaryOp op);
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `first`, `last` | イテレータ | 範囲（ranges 版は無いので `begin` / `end` を渡す） | 省略不可 |
| `init` | `T` | 初期値。**この型が結果の型になる** | 省略不可 |
| `op` | 関数 | `(これまでの結果, 次の要素)` を受け取って新しい結果を返す | `+` |

- 戻り値: まとめた結果
- 先頭から順番に計算する

<div class="anim" data-label="std::accumulate(v.begin(), v.end(), 0)">
1 2 3 4 # 初期値 0
*1 2 3 4 # 0 + 1 = 1
*1 *2 3 4 # 1 + 2 = 3
*1 *2 *3 4 # 3 + 3 = 6
*1 *2 *3 *4 # 6 + 4 = 10。左から順に足していく
</div>

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::println("合計 {}", std::accumulate(v.begin(), v.end(), 0));
  std::println("積 {}", std::accumulate(v.begin(), v.end(), 1,
                                        [](int a, int b) { return a * b; }));
}
```

```text title="実行結果"
合計 10
積 24
```

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

### std::reduce <span class="ver ver-17">C++17</span> {#reduce data-toc-label="std::reduce"}

```cpp
template <class InputIt, class T>
T reduce(InputIt first, InputIt last, T init);
template <class ExecutionPolicy, class ForwardIt, class T>
T reduce(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, T init);
```

- `accumulate` と似ていますが、**計算の順番を問わない**ので、`std::execution::par` を渡すと並列で計算できます
- 足し算のように順番を入れ替えても結果が同じ計算にしか使えません

<div class="anim" data-label="std::reduce(v.begin(), v.end(), 0)">
1 2 3 4 # 初期値 0
*1 *2 3 4 # (1 + 2) と
1 2 *3 *4 # (3 + 4) を別々に計算してもよい
*1 *2 *3 *4 # 最後に合わせて 10。順番は保証されない
</div>

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v(1000, 1);
  std::println("{}", std::reduce(v.begin(), v.end(), 0));
}
```

```text title="実行結果"
1000
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

### std::ranges::fold_right <span class="ver ver-23">C++23</span> {#fold_right data-toc-label="std::ranges::fold_right"}

```cpp
template <bidirectional_range R, class T, class F>
constexpr auto fold_right(R&& r, T init, F f);
```

- 末尾から畳み込みます。`f` は `(要素, これまでの結果)` の順に受け取ります

```cpp
#include <algorithm>
#include <print>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> v = {"a", "b", "c"};
  auto s = std::ranges::fold_right(
      v, std::string(), [](const std::string& x, std::string acc) { return acc + x; });
  std::println("{}", s);
}
```

```text title="実行結果"
cba
```

## フラグ・オプション

`f` / `op` に渡すものです。

| 渡すもの | 重要度 | 意味 |
| --- | --- | --- |
| `std::plus{}` | <span class="rank rank-sometimes">たまに</span> | 足し算（合計） |
| `std::multiplies{}` | <span class="rank rank-rare">知ってるだけ</span> | 掛け算 |
| ラムダ式 | <span class="rank rank-sometimes">たまに</span> | 自由なまとめ方 |

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| 合計 | 所持品の合計重量、パーティの合計戦力 |
| 平均 | フレーム時間の平均（合計 ÷ 個数） |
| 確率の合計 | ドロップテーブルの重みの合計 |

## よくあるミス

??? failure "float の合計に 0 を渡す"
    ```cpp
    std::vector<float> v = {0.5f, 0.5f};
    auto bad = std::accumulate(v.begin(), v.end(), 0);      // int で計算されて 0
    auto good = std::accumulate(v.begin(), v.end(), 0.0f);  // 1
    ```

??? failure "<numeric> を忘れる"
    `std::accumulate` は `<algorithm>` ではなく `<numeric>` にあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::count_if`](count_if.md) | 数える |
| [`std::ranges::max`](min_max.md) | 最大値 |

## コンパイラ対応

| 機能 | MSVC | GCC | Clang (libc++) |
| --- | --- | --- | --- |
| `std::accumulate` | ○ | ○ | ○ |
| `std::ranges::fold_left` など <span class="ver ver-23">C++23</span> | VS 2022 17.5〜 | 13〜 | 18〜 |

## これだけ覚える

!!! abstract "まとめ"
    - [x] 合計は `accumulate(b, e, 0)` か `fold_left(r, 0, std::plus{})`
    - [x] 初期値の型が結果の型。float なら `0.0f`
    - [x] `accumulate` は `<numeric>`

## 関連ページ

- [cpprefjp: std::accumulate](https://cpprefjp.github.io/reference/numeric/accumulate.html)
- [cppreference: std::ranges::fold_left](https://en.cppreference.com/w/cpp/algorithm/ranges/fold_left)

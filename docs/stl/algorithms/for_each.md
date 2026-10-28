---
title: std::ranges::for_each
summary: "全要素に関数を呼ぶ。普段は範囲 for のほうが読みやすい。"
order: 38
tags:
  - アルゴリズム
---

# std::ranges::for_each

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <algorithm>`
</div>

全要素に同じ処理を行うなら、`for (auto& x : v) { ... }` で書けます。`std::ranges::for_each` は、それとほぼ同じことをする関数です。普段は範囲 `for` のほうが読みやすいので、`for_each` を選ぶ理由は多くありません。ただし、関数を変数として渡したい、プロジェクションを使いたい、並列実行したい、といった場面では便利です。

!!! tip "ポイント"
    - <strong>普段は範囲 for でいい。</strong> for_each を使う理由は少ない。
    - 先頭 n 個だけなら `for_each_n`。
    - 並列に処理したいなら、`std::for_each(std::execution::par, ...)`（`<execution>`）。

!!! info "このページを読む前に"
    [ranges とビュー](../../basics/ranges.md)と[ラムダ式](../../basics/lambda.md)が分かると読みやすいです。

## 関数一覧

| 関数 | 重要度 | 何をする | 計算量 |
| --- | --- | --- | --- |
| [`std::ranges::for_each`](#for_each) | <span class="rank rank-sometimes">たまに</span> | 全要素に関数を呼ぶ | O(n) |
| [`std::ranges::for_each_n`](#for_each_n) | <span class="rank rank-rare">知ってるだけ</span> | 先頭 n 個に関数を呼ぶ | O(n) |
| [`std::for_each`（並列版）](#parallel) | <span class="rank rank-rare">知ってるだけ</span> | 複数のスレッドで並列に呼ぶ <span class="ver ver-17">C++17</span> | O(n) |

## よくある使い方

```cpp
#include <algorithm>
#include <print>
#include <vector>

struct Enemy {
  int hp;
};

int main() {
  std::vector<Enemy> enemies = {{30}, {50}, {80}};
  auto poison = [](int& hp) { hp -= 5; };
  std::ranges::for_each(enemies, poison, &Enemy::hp);  // プロジェクションで hp だけ渡す

  for (const auto& e : enemies) {  // 同じことは範囲 for でも書ける
    std::print("{} ", e.hp);
  }
  std::println("");
}
```

```text title="実行結果"
25 45 75 
```

## 関数の詳しい説明

### std::ranges::for_each {#for_each}

```cpp
template <input_range R, class Proj = identity, class Fun>
constexpr for_each_result<borrowed_iterator_t<R>, Fun> for_each(R&& r, Fun f, Proj proj = {});
```

| 引数 | 型 | 意味 | 省略すると |
| --- | --- | --- | --- |
| `r` | 範囲 | 対象 | 省略不可 |
| `f` | 関数 | 各要素（またはプロジェクションの結果）を受け取る関数 | 省略不可 |
| `proj` | プロジェクション | `f` に渡す前の変換 | そのまま |

- 戻り値: `.in`（終わりの位置）と `.fun`（使った関数オブジェクト。状態を持たせていれば結果が取れる）

<div class="anim" data-label="std::ranges::for_each(v, double_it)">
1 2 3 # v
*1 2 3 # 1 つずつ関数に渡す
>2 *2 3 # 1 つ目が書き換わる
>2 >4 *3 # 2 つ目
>2 >4 >6 # 全部に適用される
</div>

### std::ranges::for_each_n {#for_each_n}

```cpp
template <input_iterator I, class Proj = identity, class Fun>
constexpr for_each_n_result<I, Fun> for_each_n(I first, std::iter_difference_t<I> n, Fun f, Proj proj = {});
```

- `first` から n 個だけに関数を呼びます

```cpp
#include <algorithm>
#include <print>
#include <vector>

int main() {
  std::vector<int> ranking = {980, 870, 860, 700};
  std::ranges::for_each_n(ranking.begin(), 3, [](int score) { std::print("{} ", score); });
  std::println("");
}
```

```text title="実行結果"
980 870 860 
```

### std::for_each（並列版） {#parallel}

<span class="ver ver-17">C++17</span>

```cpp
template <class ExecutionPolicy, class ForwardIt, class F>
void for_each(ExecutionPolicy&& policy, ForwardIt first, ForwardIt last, F f);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `policy` | 実行ポリシー | `std::execution::seq`（順番に）/ `par`（並列）/ `par_unseq`（並列 + ベクトル化） |

- `<execution>` が必要です。GCC では TBB ライブラリのリンクが必要なことがあります
- 各要素の処理がお互いに関係しない（同じデータを書き換えない）ときだけ使えます

```cpp
#include <algorithm>
#include <execution>
#include <print>
#include <vector>

int main() {
  std::vector<float> particles(8, 1.0f);
  std::for_each(std::execution::seq, particles.begin(), particles.end(),
                [](float& p) { p *= 2.0f; });  // par にすると並列（環境によってはリンク設定が必要）
  std::println("{}", particles);
}
```

```text title="実行結果"
[2, 2, 2, 2, 2, 2, 2, 2]
```

## フラグ・オプション

実行ポリシー（`<execution>`）です。

| 値 | 意味 |
| --- | --- |
| `std::execution::seq` | 順番に 1 つずつ（並列にしない） |
| `std::execution::par` | 複数のスレッドで並列に |
| `std::execution::par_unseq` | 並列 + SIMD でまとめて処理 |
| `std::execution::unseq` | 1 スレッドで SIMD <span class="ver ver-20">C++20</span> |

`std::sort`、`std::transform`、`std::reduce` など多くのアルゴリズムが最初の引数にこれを受け取れます（ranges 版は非対応）。

## ゲームでの使いどころ

普段は範囲 `for` で十分です。`for_each` が役立つのは、処理を関数オブジェクトとして使い回すときです。たとえば、全オブジェクトに同じ `Update` を適用するコードで、関数を引数に取る汎用の部品を作るときに使えます。

大量の要素を並列で処理するなら、`std::for_each(std::execution::par, ...)` が使えます。数万個のパーティクルを更新する場面で、効果があることがあります。ただし、並列にすると、更新の順序が保証されません。要素どうしが独立していることが前提です。

先頭の n 個だけなら、`for_each_n` です。

## よくあるミス

??? failure "par で共有データを書き換える"
    並列版の関数の中で、同じ変数（合計など）を書き換えるとデータ競争になります。合計なら `std::reduce` を使います。

??? failure "普通の `for` で足りるのに使う"
    `for_each` は、範囲 `for` より読みにくくなることが多いです。`break` や `continue` も使えません。普通の処理は範囲 `for` で書きます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 普段は範囲 `for` で書く。
    - [x] 関数を渡したい、プロジェクションを使いたいときに `for_each`。
    - [x] 並列にするなら `std::for_each(std::execution::par, ...)`。

## 関連ページ

- [範囲 for](../../basics/range-for.md)
- [並行処理の基本](../../basics/concurrency.md)

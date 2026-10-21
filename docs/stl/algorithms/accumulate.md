---
title: std::accumulate
summary: "要素を先頭から順に足し込んで、合計などの 1 つの値を作る。"
order: 22
tags:
  - アルゴリズム
---

# std::accumulate

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <numeric>`
</div>

`std::accumulate` は、**範囲の要素を先頭から順に足し込んで、1 つの値を作る**関数です。合計を求めるのが基本で、足し算の代わりに関数を渡せば、掛け算、文字列の連結、最大値の更新などもできます。ヘッダーは `<algorithm>` ではなく **`<numeric>`** です。

!!! tip "ポイント"
    - **初期値の型**が結果の型になる。`double` の合計を取るのに `0` を渡すと、整数のまま足されて小数が切り捨てられる。`0.0` と書く。
    - C++23 では、より自然な [`std::ranges::fold_left`](fold_left.md) が使える（初期値の型の罠が少ない）。
    - 順番に足すので並列にはならない。並列で足すなら [`std::reduce`](reduce.md)。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

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

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| パーティ全員の HP の合計 | `std::accumulate(hp.begin(), hp.end(), 0)` |
| 平均ダメージ | 合計を個数で割る |
| アイテムの重さの合計 | `accumulate(items, 0.0f, 足し算)` |

## よくあるミス

??? failure "double の合計に 0 を渡す"
    ```cpp
    std::vector<double> v = {0.5, 0.5};
    auto a = std::accumulate(v.begin(), v.end(), 0);    // 0 は int。結果は 0（小数が切り捨てられる）
    auto b = std::accumulate(v.begin(), v.end(), 0.0);  // 1.0
    ```

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::fold_left`](fold_left.md) | C++23 の範囲版。型の罠が少ない |
| [`std::reduce`](reduce.md) | 順序を問わない（並列化できる）合計 |
| [`std::transform_reduce`](transform_reduce.md) | 変換してから合計する |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 先頭から順に足し込む
    - [x] 初期値の型が結果の型
    - [x] ヘッダーは `<numeric>`

## 関連ページ

- [cpprefjp: std::accumulate](https://cpprefjp.github.io/reference/numeric/accumulate.html)
- [cppreference: std::accumulate](https://en.cppreference.com/w/cpp/algorithm/accumulate)

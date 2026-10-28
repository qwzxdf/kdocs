---
title: std::transform_reduce
summary: "要素を変換してから、合計などにまとめる（内積に使える）。"
order: 26
tags:
  - アルゴリズム
---

# std::transform_reduce

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`std::transform_reduce` は、**要素に変換をかけてから、1 つの値にまとめる**関数です。「2 つの配列の内積」「各要素の 2 乗の合計」のような、変換 → 合計の処理を 1 回の走査で行います。[`reduce`](reduce.md) と同じく、順序を問わないので並列化できます。

!!! tip "ポイント"
    - 2 つの範囲を渡すと、**内積**（要素ごとに掛けて合計）になる。
    - 1 つの範囲に変換関数を渡すと、「変換してから合計」になる。
    - 合計の関数と変換の関数を自分で選べる。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。ヘッダーは `<numeric>` です。

## 関数の詳しい説明

### std::transform_reduce {#transform_reduce}

```cpp
// 2 つの範囲の内積
template <class It1, class It2, class T>
T transform_reduce(It1 first1, It1 last1, It2 first2, T init);

// 1 つの範囲を変換して合計
template <class It, class T, class BinaryOp, class UnaryOp>
T transform_reduce(It first, It last, T init, BinaryOp reduce_op, UnaryOp transform_op);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first`, `last` | イテレータ | 対象の範囲 |
| `first2` | イテレータ | 2 つ目の範囲の先頭（内積版） |
| `init` | T | 初期値。結果の型になる |
| `reduce_op` | 関数 | まとめる演算（例: `std::plus{}`） |
| `transform_op` | 関数 | 各要素を変換する関数 |

- 戻り値: 結果（`T`）
- 計算量: O(n)

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> a = {1, 2, 3};
  std::vector<int> b = {4, 5, 6};

  // 内積: 1*4 + 2*5 + 3*6
  std::println("内積 {}", std::transform_reduce(a.begin(), a.end(), b.begin(), 0));

  // 各要素を 2 乗して合計: 1 + 4 + 9
  int sum_sq = std::transform_reduce(a.begin(), a.end(), 0, std::plus{}, [](int x) { return x * x; });
  std::println("2 乗和 {}", sum_sq);
}
```

```text title="実行結果"
内積 32
2 乗和 14
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ベクトルの内積（ライティング、射影） | `transform_reduce(a, b, 0.0f)` |
| 全オブジェクトの重さの合計 | `transform_reduce(items, 0.0f, plus, 重さ)` |

## よくあるミス

??? failure "初期値の型を間違える"
    `accumulate` と同じく、初期値の型が結果の型です。`float` の合計は `0.0f` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::reduce`](reduce.md) | 変換なしで合計 |
| [`std::inner_product`](inner_product.md) | 従来の内積。順序固定 |
| [`std::ranges::transform`](transform.md) | 変換だけ（合計しない） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 変換してから合計する
    - [x] 2 つの範囲なら内積
    - [x] 順序を問わないので並列化できる

## 関連ページ

- [cpprefjp: std::transform_reduce](https://cpprefjp.github.io/reference/numeric/transform_reduce.html)
- [cppreference: std::transform_reduce](https://en.cppreference.com/w/cpp/algorithm/transform_reduce)

---
title: std::transform_inclusive_scan
summary: "各要素を変換してから、先頭からの累積を作る（その位置を含む）。"
order: 900
tags:
  - アルゴリズム
---

# std::transform_inclusive_scan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

累積和を作る前に各要素を何か変換したいことがあります（たとえば 2 乗してから足す）。`inclusive_scan` の前に `transform` を挟むと 2 回走査しますが、`transform_inclusive_scan` なら 1 回で済みます。

!!! tip "ポイント"
    - 変換関数と結合関数の 2 つを渡す。
    - その位置を含む累積は inclusive、含まないのは [`transform_exclusive_scan`](transform_exclusive_scan.md)。
    - 実行ポリシーを付けると並列に動く。

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::transform_inclusive_scan {#transform_inclusive_scan}

```cpp
template <class InputIt, class OutputIt, class BinaryOp, class UnaryOp>
OutputIt transform_inclusive_scan(InputIt first, InputIt last, OutputIt d_first, BinaryOp binary_op, UnaryOp unary_op);

template <class InputIt, class OutputIt, class BinaryOp, class UnaryOp, class T>
OutputIt transform_inclusive_scan(InputIt first, InputIt last, OutputIt d_first, BinaryOp binary_op, UnaryOp unary_op, T init);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `first, last` | イテレータ | 入力の範囲 |
| `d_first` | イテレータ | 出力の先頭 |
| `binary_op` | 関数 | 累積に使う 2 項演算 |
| `unary_op` | 関数 | 各要素に先に適用する変換 |
| `init` | T | 省略可。初期値 |

- 戻り値: 出力の最後の次のイテレータ
- 計算量: 線形


## 実際に動かしてみる

```cpp
#include <functional>
#include <numeric>
#include <print>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3, 4};
  std::vector<int> out(v.size());
  std::transform_inclusive_scan(v.begin(), v.end(), out.begin(), std::plus<>{},
                                [](int x) { return x * x; });
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 5, 14, 30]
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 2 乗和の累積を作る | `std::transform_inclusive_scan(v.begin(), v.end(), out.begin(), std::plus<>{}, [](int x){ return x * x; });` |

## よくあるミス

??? failure "結合関数が結合法則を満たさない"
    並列版は順序が不定です。引き算のような結合法則を満たさない演算は結果が不定になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`inclusive_scan`](inclusive_scan.md) | 変換なしの版 |
| [`transform_exclusive_scan`](transform_exclusive_scan.md) | その位置を含まない版 |
| [`partial_sum`](partial_sum.md) | 順序が固定の古い版 |

## コンパイラ対応

C++17 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 変換しながら累積を作る
    - [x] その位置を含む
    - [x] 結合法則を満たす演算で

## 関連ページ

- [cpprefjp: std::transform_inclusive_scan](https://cpprefjp.github.io/reference/numeric/transform_inclusive_scan.html)
- [cppreference: std::transform_inclusive_scan](https://en.cppreference.com/w/cpp/algorithm/transform_inclusive_scan)

---
title: std::transform_exclusive_scan
summary: "各要素を変換してから、先頭からの累積を作る（その位置を含まない）。"
order: 900
tags:
  - アルゴリズム
---

# std::transform_exclusive_scan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

要素ごとに変換してから、その位置を含めない累計を求めたい。`std::transform_exclusive_scan` は、`transform` と `exclusive_scan` を、中間の配列なしで 1 回の走査にまとめます。

!!! tip "ポイント"
    - 要素を単項演算で変換してから、`exclusive_scan` する
    - 中間の配列を作らない
    - 初期値と、結合の二項演算が必須
    - 実行ポリシーで並列にできる

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::transform_exclusive_scan {#transform_exclusive_scan}

<span class="ver ver-17">C++17</span>

```cpp
template <class InputIt, class OutputIt, class T, class BinaryOp, class UnaryOp>
OutputIt transform_exclusive_scan(InputIt first, InputIt last, OutputIt d_first,
                                  T init, BinaryOp binary_op, UnaryOp unary_op);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `init` | `T` | 先頭の出力になる初期値 |
| `binary_op` | 二項関数 | 累計の演算（結合法則を満たす） |
| `unary_op` | 単項関数 | 各要素の変換 |

`out[0] = init`、`out[i] = binary_op(out[i-1], unary_op(in[i-1]))` です。

たとえば、「要素を 2 倍してから、その位置を含めない累計」は、`unary_op` に `x * 2`、`binary_op` に `plus` を指定します。

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3};
  std::vector<int> out(v.size());

  // 2 倍してから、その位置を含めない累計
  std::transform_exclusive_scan(v.begin(), v.end(), out.begin(), 0, std::plus<>(),
                                [](int x) { return x * 2; });
  std::println("{}", out);
}
```

```text title="実行結果"
[0, 2, 6]
```

## ゲームでの使いどころ

各要素の重みを計算してから、開始位置を求めるような処理に使います。

## よくあるミス

??? failure "変換が副作用を持つ"
    並列実行で、順序が不定になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exclusive_scan`](exclusive_scan.md) | 変換なし |
| [`transform_inclusive_scan`](transform_inclusive_scan.md) | 含める版 |
| [`transform_reduce`](transform_reduce.md) | 最後の合計だけ |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::transform_exclusive_scan](https://cpprefjp.github.io/reference/numeric/transform_exclusive_scan.html)
- [cppreference: std::transform_exclusive_scan](https://en.cppreference.com/w/cpp/algorithm/transform_exclusive_scan)

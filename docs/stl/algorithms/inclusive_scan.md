---
title: std::inclusive_scan
summary: "累積和（各位置までの合計、その位置を含む）を求める。並列化できる。"
order: 30
tags:
  - アルゴリズム
---

# std::inclusive_scan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <numeric>`
</div>

`std::partial_sum` と同じ累計を、並列にも実行できるようにしたのが C++17 の `std::inclusive_scan` です。各位置の結果に、その位置の要素を含めるので、「包含的（inclusive）」な走査と呼びます。

!!! tip "ポイント"
    - `out[i]` は、`in[0]` 〜 `in[i]` の合計（その位置を含む）
    - 演算は結合法則を満たす必要がある（並列実行のため）
    - 実行ポリシーを渡して、並列に実行できる
    - 初期値（`init`）を渡せる

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::inclusive_scan {#inclusive_scan}

<span class="ver ver-17">C++17</span>

```cpp
template <class InputIt, class OutputIt>
OutputIt inclusive_scan(InputIt first, InputIt last, OutputIt d_first);

template <class InputIt, class OutputIt, class BinaryOp, class T>
OutputIt inclusive_scan(InputIt first, InputIt last, OutputIt d_first, BinaryOp op, T init);
```

`init` を渡すと、先頭の要素の前に `init` があるものとして計算します。`out[0] = op(init, in[0])` です。

並列実行では、要素をいくつかのブロックに分け、ブロックごとに累計を求めて、あとで結合します。そのため、演算の順序が `partial_sum` と変わり、浮動小数点数の結果が微妙に異なることがあります。

小さな範囲では、並列化のコストのほうが大きいので、速くなるとは限りません。数十万要素を超えるあたりから、効果が出ます。

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3, 4};

  std::vector<int> out(v.size());
  std::inclusive_scan(v.begin(), v.end(), out.begin());
  std::println("{}", out);

  // 初期値つき
  std::inclusive_scan(v.begin(), v.end(), out.begin(), std::plus<>(), 100);
  std::println("{}", out);
}
```

```text title="実行結果"
[1, 3, 6, 10]
[101, 103, 106, 110]
```

## ゲームでの使いどころ

大量の要素の累計（ヒストグラムの累積分布など）を、並列で求めるときに使います。

## よくあるミス

??? failure "結合法則を満たさない演算を渡す"
    並列実行で結果が変わります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exclusive_scan`](exclusive_scan.md) | その位置を含めない累計 |
| [`partial_sum`](partial_sum.md) | 並列に対応しない版 |
| [`transform_inclusive_scan`](transform_inclusive_scan.md) | 変換してから累計 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::inclusive_scan](https://cpprefjp.github.io/reference/numeric/inclusive_scan.html)
- [cppreference: std::inclusive_scan](https://en.cppreference.com/w/cpp/algorithm/inclusive_scan)

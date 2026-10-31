---
title: std::partial_sum
summary: "先頭からの累積和（途中までの合計）を求める。"
order: 28
tags:
  - アルゴリズム
---

# std::partial_sum

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <numeric>`
</div>

スコアの履歴から累計を、距離の列から累積距離を求めたい。`std::partial_sum` は、先頭から各位置までの合計を並べます。`{1,2,3,4}` から `{1,3,6,10}` を作ります。`adjacent_difference` の逆の働きです。

!!! tip "ポイント"
    - 出力の `i` 番目は、入力の 0 〜 `i` 番目の合計
    - 加算の代わりに、別の演算も指定できる
    - 入力と出力が同じ範囲でもよい
    - C++17 の `inclusive_scan` が、並列に対応した後継

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::partial_sum {#partial_sum}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class InputIt, class OutputIt>
OutputIt partial_sum(InputIt first, InputIt last, OutputIt d_first);

template <class InputIt, class OutputIt, class BinaryOp>
OutputIt partial_sum(InputIt first, InputIt last, OutputIt d_first, BinaryOp op);
```

`out[0] = in[0]`、`out[i] = op(out[i-1], in[i])` で、前の結果に次の要素を足していきます。順序が決まっているので、並列にはできません。

整数がオーバーフローしないかは、呼び出し側の責任です。要素の型が `int` で、合計が大きくなるなら、出力に `long long` を使います。出力先の型が合計の型になります。

並列化できる `std::inclusive_scan` は、演算が結合法則を満たすことが前提です。浮動小数点数の加算は、厳密には結合法則を満たさないので、`inclusive_scan` と `partial_sum` で結果が微妙に違うことがあります。

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  const std::vector<int> v = {1, 2, 3, 4};

  std::vector<int> sums(v.size());
  std::partial_sum(v.begin(), v.end(), sums.begin());
  std::println("{}", sums);

  // 積の累計
  std::vector<int> prods(v.size());
  std::partial_sum(v.begin(), v.end(), prods.begin(), std::multiplies<>());
  std::println("{}", prods);
}
```

```text title="実行結果"
[1, 3, 6, 10]
[1, 2, 6, 24]
```

## ゲームでの使いどころ

重みつき抽選で、重みの累計を作り、乱数がどの区間に入るかを二分探索で探すのが定番です。

## よくあるミス

??? failure "出力の型が小さくて、オーバーフローする"
    `long long` などの大きい型にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`inclusive_scan`](inclusive_scan.md) | 並列版の後継 |
| [`adjacent_difference`](adjacent_difference.md) | 逆の働き |
| [`accumulate`](accumulate.md) | 最後の合計だけを求める |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::partial_sum](https://cpprefjp.github.io/reference/numeric/partial_sum.html)
- [cppreference: std::partial_sum](https://en.cppreference.com/w/cpp/algorithm/partial_sum)

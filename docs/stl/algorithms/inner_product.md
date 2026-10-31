---
title: std::inner_product
summary: "2 つの範囲の内積（要素ごとの積の合計）を求める。"
order: 27
tags:
  - アルゴリズム
---

# std::inner_product

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <numeric>`
</div>

2 つのベクトルの内積を求めたい。`std::inner_product` は、2 つの範囲の対応する要素のかけ算を、全部足します。`{1,2,3}` と `{4,5,6}` なら `1*4 + 2*5 + 3*6 = 32` です。かけ算と足し算を、別の演算に変えることもできます。

!!! tip "ポイント"
    - 対応する要素の積の合計（内積）を求める
    - 初期値を渡す
    - 積と和の演算を、別の関数に変えられる
    - 並列にしたいなら C++17 の `transform_reduce`

!!! info "このページを読む前に"
    [イテレータ](../../basics/iterator.md) が分かると読みやすいです。

## 関数の詳しい説明

### std::inner_product {#inner_product}

<span class="ver ver-11">C++98〜</span>

```cpp
template <class InputIt1, class InputIt2, class T>
T inner_product(InputIt1 first1, InputIt1 last1, InputIt2 first2, T init);

template <class InputIt1, class InputIt2, class T, class BinaryOp1, class BinaryOp2>
T inner_product(InputIt1 first1, InputIt1 last1, InputIt2 first2, T init,
                BinaryOp1 op1, BinaryOp2 op2);
```

結果の型は、`init` の型です。`int` の `init` で `double` の要素を足すと、小数部が失われます。`0.0` と書きます。

2 つ目の範囲は、先頭だけを渡すので、1 つ目と同じ長さがあることを、呼び出し側が保証します。

演算を変えた版は、`op1` が「全体を畳む演算」（既定は `+`）、`op2` が「対応する要素どうしの演算」（既定は `*`）です。「全要素が一致するか」のような、内積以外の使い方もできます。

順序が規定されているので、並列にはなりません。並列には `std::transform_reduce` を使います。

## 実際に動かしてみる

```cpp
#include <numeric>
#include <print>
#include <vector>

int main() {
  const std::vector<int> a = {1, 2, 3};
  const std::vector<int> b = {4, 5, 6};

  std::println("内積: {}", std::inner_product(a.begin(), a.end(), b.begin(), 0));

  // 小数なら初期値も double にする
  const std::vector<double> x = {0.5, 1.5};
  const std::vector<double> y = {2.0, 4.0};
  std::println("{}", std::inner_product(x.begin(), x.end(), y.begin(), 0.0));
}
```

```text title="実行結果"
内積: 32
7
```

## ゲームでの使いどころ

ベクトルの内積は、専用の数学ライブラリが普通です。重みつきの合計を求める処理で使えます。

## よくあるミス

??? failure "init の型が整数で、小数が切り捨てられる"
    `0.0` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`transform_reduce`](transform_reduce.md) | 並列に対応した後継 |
| [`accumulate`](accumulate.md) | 1 つの範囲の合計 |
| [`partial_sum`](partial_sum.md) | 累計 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::inner_product](https://cpprefjp.github.io/reference/numeric/inner_product.html)
- [cppreference: std::inner_product](https://en.cppreference.com/w/cpp/algorithm/inner_product)

---
title: std::gslice
summary: "valarray から、多次元の添字（開始位置・各次元の個数・各次元の間隔）で要素を選ぶ。"
order: 900
tags:
  - コンテナ
---

# std::gslice

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <valarray>`
</div>

`std::slice` は、1 つの間隔で要素を選びますが、`std::gslice`（一般化したスライス）は、複数の次元の「個数」と「間隔」を指定して、行列の部分行列のような、多次元の選び方ができます。

!!! tip "ポイント"
    - `gslice(開始, {各次元の個数}, {各次元の間隔})` で指定する
    - 個数と間隔は、`valarray<size_t>` で渡す
    - 行列の部分ブロックを取り出せる
    - 使う機会は少ない

!!! info "このページを読む前に"
    [`std::valarray`](valarray.md) を先に読んでください。

## 関数の詳しい説明

### std::gslice {#gslice}

```cpp
class gslice {
 public:
  gslice();
  gslice(std::size_t start,
         const std::valarray<std::size_t>& sizes,
         const std::valarray<std::size_t>& strides);
};
```

4×4 の行列を 1 次元に持ったとき、左上の 2×2 のブロックは、`gslice(0, {2, 2}, {4, 1})` です。外側の次元が「2 行、間隔 4」、内側の次元が「2 列、間隔 1」を表します。

選ばれる要素の順序は、最後の次元が最も速く変わる順（行優先）です。

`v[gslice]` は、`gslice_array` を返し、代入で元を更新できます。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <numeric>
#include <print>
#include <valarray>
#include <vector>

int main() {
  // 4x4 の行列を 1 次元で持つ: 0..15
  std::valarray<int> m(16);
  std::iota(std::begin(m), std::end(m), 0);

  // 左上の 2x2 ブロック: 2 行（間隔 4）x 2 列（間隔 1）
  const std::valarray<std::size_t> sizes = {2, 2};
  const std::valarray<std::size_t> strides = {4, 1};
  const std::valarray<int> block(m[std::gslice(0, sizes, strides)]);

  std::println("{}", std::vector<int>(std::begin(block), std::end(block)));
}
```

```text title="実行結果"
[0, 1, 4, 5]
```

## ゲームでの使いどころ

数値計算の行列で、部分ブロックを扱うときに使います。

## よくあるミス

??? failure "個数と間隔の次元数が合わない"
    2 つの `valarray` は、同じ長さにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`slice`](slice.md) | 1 次元の指定 |
| `std::mdspan` | C++23 の多次元の見え方 |
| [`valarray`](valarray.md) | 対象 |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::gslice](https://cpprefjp.github.io/reference/valarray/gslice.html)
- [cppreference: std::gslice](https://en.cppreference.com/w/cpp/numeric/valarray/gslice)

---
title: std::slice
summary: "valarray から、開始位置・個数・間隔で要素を選ぶ。"
order: 900
tags:
  - コンテナ
---

# std::slice

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <valarray>`
</div>

`std::valarray` の一部を、「開始位置、個数、間隔」で指定して取り出したい。行列を 1 次元に並べたとき、1 列分を取るのが典型です。`std::slice(start, size, stride)` は、その指定を表す小さな型で、`v[std::slice(...)]` で一部だけを参照できます。

!!! tip "ポイント"
    - `slice(開始, 個数, 間隔)` で、等間隔の要素を指す
    - `v[slice]` は、元の `valarray` の要素への参照（`slice_array`）
    - 代入すると、元の `valarray` が書き換わる
    - 行列の行や列を取り出すのに向く

!!! info "このページを読む前に"
    [`std::valarray`](valarray.md) を先に読んでください。

## 関数の詳しい説明

### std::slice {#slice}

```cpp
class slice {
 public:
  slice();
  slice(std::size_t start, std::size_t size, std::size_t stride);
  std::size_t start() const;
  std::size_t size() const;
  std::size_t stride() const;
};
```

`slice(1, 3, 2)` は、添字 1、3、5 の 3 要素です（開始 1、間隔 2、個数 3）。

非 const の `valarray` に `[slice]` を使うと `slice_array` が得られ、これに代入すると、元の要素が更新されます。`valarray` に変換して値を取り出すこともできます。

```cpp
std::valarray<int> col(v[std::slice(1, 3, 4)]);   // 4 列の行列の 1 列目
```

範囲が `valarray` の大きさを超えると、未定義動作です。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <valarray>
#include <vector>

int main() {
  std::valarray<int> v = {0, 1, 2, 3, 4, 5, 6, 7, 8, 9};

  // 添字 1 から、間隔 2 で 3 個: 1, 3, 5
  const std::valarray<int> s(v[std::slice(1, 3, 2)]);
  std::println("{}", std::vector<int>(std::begin(s), std::end(s)));

  // 代入すると、元の valarray が書き換わる
  v[std::slice(0, 3, 3)] = 100;  // 添字 0, 3, 6
  std::println("{}", std::vector<int>(std::begin(v), std::end(v)));
}
```

```text title="実行結果"
[1, 3, 5]
[100, 1, 2, 100, 4, 5, 100, 7, 8, 9]
```

## ゲームでの使いどころ

行列を 1 次元に持つ数値計算で、行や列を取り出すときに使います。ゲームの行列は、専用の数学ライブラリです。

## よくあるミス

??? failure "範囲が配列を超える"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`gslice`](gslice.md) | 多次元の指定 |
| [`mask_array`](mask_array.md) | 条件で選ぶ |
| [`indirect_array`](indirect_array.md) | 添字の列で選ぶ |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::slice](https://cpprefjp.github.io/reference/valarray/slice.html)
- [cppreference: std::slice](https://en.cppreference.com/w/cpp/numeric/valarray/slice)

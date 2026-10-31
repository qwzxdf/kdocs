---
title: std::strided_slice
summary: "submdspan で「開始位置・長さ・間隔」を指定する範囲。"
order: 900
tags:
  - コンテナ
---

# std::strided_slice

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <mdspan>`
</div>

`std::submdspan` で、範囲を「1 つおき」「3 つおき」のように、間隔つきで取りたい。`std::strided_slice{offset, extent, stride}` は、その指定を表します。ミップマップのように、画像を間引いて見るときに使います。

!!! tip "ポイント"
    - `strided_slice{開始, 個数の範囲, 間隔}` で指定する
    - `extent` は、範囲の長さ（個数ではない）
    - 結果は `layout_stride` になる
    - C++26

!!! info "このページを読む前に"
    [`submdspan`](submdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::strided_slice {#strided_slice}

<span class="ver ver-26">C++26</span>

```cpp
template <class OffsetType, class ExtentType, class StrideType>
struct strided_slice {
  OffsetType offset;
  ExtentType extent;
  StrideType stride;
};
```

`strided_slice{1, 5, 2}` は、位置 1 から長さ 5 の範囲を、間隔 2 で取ります。取られる位置は 1、3、5 です（範囲 `[1, 6)` の中の 3 つ）。

個数は `ceil(extent / stride)` で決まります。範囲の長さと間隔から決まるので、個数を直接指定するわけではありません。

整数に見える引数は、コンパイル時の定数（`std::integral_constant`）にすると、結果の `extents` が静的になり、最適化されます。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
std::mdspan<float, std::dextents<std::size_t, 2>> img(pixels, 8, 8);

// 縦横ともに 1 つおきに見る（4 x 4）
auto half = std::submdspan(img,
                           std::strided_slice{0, 8, 2},
                           std::strided_slice{0, 8, 2});
```

## ゲームでの使いどころ

画像の縮小（間引き）や、ミップマップの下位レベルを、コピーなしで作るときに使います。

## よくあるミス

??? failure "extent を個数だと思う"
    範囲の長さです。個数は `extent / stride` で決まります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`submdspan`](submdspan.md) | 使う関数 |
| [`full_extent`](full_extent.md) | 全部 |
| [`layout_stride`](layout_stride.md) | 結果のレイアウト |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::strided_slice](https://cpprefjp.github.io/reference/mdspan/strided_slice.html)
- [cppreference: std::strided_slice](https://en.cppreference.com/w/cpp/container/mdspan/strided_slice)

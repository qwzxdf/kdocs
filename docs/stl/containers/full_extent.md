---
title: std::full_extent
summary: "submdspan で「この次元は全部」を表す目印。"
order: 900
tags:
  - コンテナ
---

# std::full_extent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <mdspan>`
</div>

`std::submdspan` で、ある次元を「全部」取りたいときに、その次元の指定として渡す印が `std::full_extent` です。行列から「2 行目の全部の列」を取るのに、`submdspan(m, 2, std::full_extent)` と書きます。

!!! tip "ポイント"
    - `submdspan` の次元の指定で、その次元の全部を表す
    - `full_extent_t` 型の定数
    - 範囲 `(0, size)` を書くより簡潔
    - C++26

!!! info "このページを読む前に"
    [`submdspan`](submdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::full_extent {#full_extent}

<span class="ver ver-26">C++26</span>

```cpp
struct full_extent_t { explicit full_extent_t() = default; };
inline constexpr std::full_extent_t full_extent{};
```

`submdspan` の各次元の指定には、次の 3 種類が書けます。

| 指定 | 意味 |
| --- | --- |
| 整数 | その位置だけ。次元が 1 つ減る |
| `std::pair{開始, 終了}` | 範囲 |
| `std::full_extent` | 全部 |

`full_extent` は、範囲 `[0, extent)` と同じ意味ですが、大きさを書かずに済み、動的な次元でも使えます。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
std::mdspan<int, std::dextents<std::size_t, 2>> m(data, 3, 4);

auto row2 = std::submdspan(m, 2, std::full_extent);                    // 3 行目の全部の列
auto col1 = std::submdspan(m, std::full_extent, 1);                    // 2 列目の全部の行
auto block = std::submdspan(m, std::pair{0, 2}, std::full_extent);     // 上の 2 行
```

## ゲームでの使いどころ

画像の 1 行や 1 列を切り出して、1 次元の `mdspan` として扱うときに使います。

## よくあるミス

??? failure "整数と範囲の違いを取り違える"
    整数は次元が減ります。範囲は次元が残ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`submdspan`](submdspan.md) | 使う関数 |
| [`strided_slice`](strided_slice.md) | 間隔つきの範囲 |
| [`mdspan`](mdspan.md) | 対象 |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::full_extent](https://cpprefjp.github.io/reference/mdspan/full_extent_t.html)
- [cppreference: std::full_extent](https://en.cppreference.com/w/cpp/container/mdspan/full_extent_t)

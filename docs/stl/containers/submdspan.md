---
title: std::submdspan
summary: "mdspan の一部（行・列・範囲）を取り出して、新しい mdspan にする。"
order: 900
tags:
  - コンテナ
---

# std::submdspan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <mdspan>`
</div>

`std::mdspan` で見ている 2 次元の画像から、一部分（矩形、1 行、1 列）だけを、コピーなしで取り出したい。`std::submdspan(m, 指定...)` は、次元ごとの指定（位置、範囲、全部、間隔つきの範囲）を受け取って、元のデータの部分的な見え方を返します。

!!! tip "ポイント"
    - 次元ごとに、整数・範囲・`full_extent`・`strided_slice` を指定する
    - 整数を指定した次元は消える（次元数が減る）
    - 元のデータを共有する。コピーしない
    - C++26

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::submdspan {#submdspan}

<span class="ver ver-26">C++26</span>

```cpp
template <class T, class E, class L, class A, class... SliceSpecifiers>
constexpr auto submdspan(const std::mdspan<T, E, L, A>& src, SliceSpecifiers... slices);
```

結果の `mdspan` のレイアウトは、指定によって自動で選ばれます。行を取り出すだけなら `layout_right` のまま、列を取り出すと `layout_stride` になります。

指定の種類は次のとおりです。

- 整数: その位置だけ（次元が消える）
- `std::pair{a, b}`: `[a, b)` の範囲
- `std::full_extent`: 全部
- `std::strided_slice{offset, extent, stride}`: 間隔つきの範囲

結果は元のデータを指すので、元が破棄されるとぶら下がります。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
std::array<int, 12> data = {};
std::mdspan<int, std::dextents<std::size_t, 2>> m(data.data(), 3, 4);   // 3 行 4 列

auto row = std::submdspan(m, 1, std::full_extent);                       // 2 行目: 長さ 4
auto rect = std::submdspan(m, std::pair{0, 2}, std::pair{1, 3});         // 2 x 2 の矩形
rect[0, 0] = 99;                                                         // 元のデータが変わる
```

## ゲームでの使いどころ

画像処理で、タイルや一部の領域だけを、コピーせずに処理するときに使います。

## よくあるミス

??? failure "元のデータより長く保持する"
    ぶら下がります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`full_extent`](full_extent.md) | 全部を表す |
| [`strided_slice`](strided_slice.md) | 間隔つきの範囲 |
| [`layout_stride`](layout_stride.md) | 結果のレイアウトに使われる |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::submdspan](https://cpprefjp.github.io/reference/mdspan/submdspan.html)
- [cppreference: std::submdspan](https://en.cppreference.com/w/cpp/container/mdspan/submdspan)

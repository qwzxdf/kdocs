---
title: std::layout_stride
summary: "次元ごとの「歩幅」を自分で決める配置規則。"
order: 33
tags:
  - コンテナ
---

# std::layout_stride

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <mdspan>`
</div>

`layout_left` と `layout_right` は、並び方が決まっていますが、「3 行目ごとに取る」「列を 1 つ飛ばしに見る」のように、任意の間隔（ストライド）で見たいことがあります。`std::layout_stride` は、次元ごとの間隔を、実行時に指定できるレイアウトです。

!!! tip "ポイント"
    - 次元ごとのストライド（要素の間隔）を指定する
    - 部分的な見え方（行列の列だけ、1 つ飛ばし）を作れる
    - `mapping(extents, strides)` で構築する
    - `submdspan` の結果などで使われる

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::layout_stride {#layout_stride}

<span class="ver ver-23">C++23</span>

```cpp
struct layout_stride {
  template <class Extents> class mapping;
};
```

`mapping` は、`extents` と、各次元のストライドの配列から作ります。`m[i, j]` の位置は、`i * stride(0) + j * stride(1)` です。

行優先の 2×3 は、ストライドが `{3, 1}`、列優先は `{1, 2}` です。

```cpp
layout_stride::mapping<extents<size_t, 2, 2>> map(extents<size_t, 2, 2>{}, std::array{3, 2});
```

これにより、3 列の行列から、1 列飛ばしで 2 列を取り出す（ストライド 2）といった見方ができます。ストライドが、実際のデータの範囲を超えないようにするのは、利用者の責任です。

## 実際に動かしてみる

```cpp
#include <array>
#include <mdspan>
#include <print>

int main() {
  // 2 行 4 列の行列 (行優先)
  std::array<int, 8> data = {0, 1, 2, 3, 4, 5, 6, 7};

  // 列を 1 つ飛ばしに見る: 2 行 x 2 列、ストライドは {4, 2}
  using E = std::extents<std::size_t, 2, 2>;
  std::layout_stride::mapping<E> map(E{}, std::array<std::size_t, 2>{4, 2});
  std::mdspan<int, E, std::layout_stride> m(data.data(), map);

  std::println("{} {}", m[0, 0], m[0, 1]);  // 0 と 2
  std::println("{} {}", m[1, 0], m[1, 1]);  // 4 と 6
}
```

```text title="実行結果"
0 2
4 6
```

## ゲームでの使いどころ

画像の一部分や、行列の間引き（ミップマップのような）を、コピーなしで見るときに使います。

## よくあるミス

??? failure "ストライドが範囲を超える"
    配列の外を読みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`layout_left`](layout_left.md) | 列優先 |
| [`submdspan`](submdspan.md) | 部分的な見え方を作る |
| [`mdspan`](mdspan.md) | 使う側 |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::layout_stride](https://cpprefjp.github.io/reference/mdspan/layout_stride.html)
- [cppreference: std::layout_stride](https://en.cppreference.com/w/cpp/container/layout_stride)

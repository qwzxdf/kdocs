---
title: std::layout_left
summary: "多次元の添字を、1 次元の位置に変える規則（列優先）。"
order: 32
tags:
  - コンテナ
---

# std::layout_left

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <mdspan>`
</div>

2 次元の配列を 1 次元のメモリに並べるとき、行ごとに並べる方法（行優先）と、列ごとに並べる方法（列優先）があります。C++ の配列は行優先ですが、Fortran や OpenGL の行列は列優先です。`std::layout_left` は、`mdspan` で列優先を指定するレイアウトで、最初の添字が最も速く変わります。

!!! tip "ポイント"
    - `layout_left`: 最初の添字が連続する（列優先）
    - `layout_right`: 最後の添字が連続する（行優先）。`mdspan` の既定
    - `m[i, j]` の位置は、`i + j * 行数`
    - 列優先のライブラリのデータを、コピーせずに扱える

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::layout_left {#layout_left}

<span class="ver ver-23">C++23</span>

```cpp
struct layout_left {
  template <class Extents> class mapping;
};
```

`extents<size_t, 2, 3>` なら、`m[i, j]` の 1 次元の位置は `i + j * 2` です。`i` が 1 増えると位置が 1 増え、`j` が 1 増えると、行数ぶん増えます。

`layout_right`（既定）では、`m[i, j]` は `i * 3 + j` で、`j` が 1 増えると位置が 1 増えます。

どちらを選ぶかで、メモリの並びが変わります。同じ `data` を、`layout_left` と `layout_right` で見ると、行列の転置を、コピーなしで見ているのと同じ結果になります。

ループは、連続する添字が最も内側になるように書くと、キャッシュに有利です。`layout_left` では、最初の添字（`i`）を内側にします。

## 実際に動かしてみる

```cpp
#include <array>
#include <mdspan>
#include <print>

int main() {
  std::array<int, 6> data = {0, 1, 2, 3, 4, 5};
  using E = std::extents<std::size_t, 2, 3>;

  std::mdspan<int, E, std::layout_right> r(data.data());  // 行優先（既定）
  std::mdspan<int, E, std::layout_left> l(data.data());   // 列優先

  std::println("right: [0,1] = {} [1,0] = {}", r[0, 1], r[1, 0]);
  std::println("left:  [0,1] = {} [1,0] = {}", l[0, 1], l[1, 0]);
}
```

```text title="実行結果"
right: [0,1] = 1 [1,0] = 3
left:  [0,1] = 2 [1,0] = 1
```

## ゲームでの使いどころ

OpenGL / Direct3D の列優先の行列データを、そのまま `mdspan` で見るときに使います。

## よくあるミス

??? failure "ループの順序がレイアウトに合っていない"
    連続しない順で回ると、キャッシュに不利で遅くなります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`layout_stride`](layout_stride.md) | 任意の間隔 |
| [`default_accessor`](default_accessor.md) | 要素の取り出し |
| [`mdspan`](mdspan.md) | 使う側 |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::layout_left](https://cpprefjp.github.io/reference/mdspan/layout_left.html)
- [cppreference: std::layout_left](https://en.cppreference.com/w/cpp/container/layout_left)

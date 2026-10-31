---
title: std::dextents
summary: "すべての次元が実行時に決まる extents の別名。"
order: 900
tags:
  - コンテナ
---

# std::dextents

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <mdspan>`
</div>

`std::mdspan` で、行と列の大きさを、実行時に決めたい。`std::extents<size_t, std::dynamic_extent, std::dynamic_extent>` と書くのは長いので、「`N` 次元がすべて動的」を表す別名が `std::dextents<IndexType, N>` です。

!!! tip "ポイント"
    - `dextents<size_t, 2>` は、2 次元ともに実行時に決まる `extents`
    - `extents<size_t, dynamic_extent, dynamic_extent>` の短い書き方
    - 次元数だけを指定する
    - `mdspan` の既定の次元指定として、最もよく使う

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::dextents {#dextents}

<span class="ver ver-23">C++23</span>

```cpp
template <class IndexType, std::size_t Rank>
using dextents = /* Rank 個の dynamic_extent を持つ extents */;
```

`IndexType` は添字の型で、`std::size_t` や `int` を指定します。小さい型にすると、`mdspan` オブジェクトが小さくなります。

```cpp
std::mdspan<float, std::dextents<std::size_t, 2>> m(data, rows, cols);
```

大きさは、`mdspan` を作るときの引数で渡します。次元の一部だけを固定したいなら、`extents` に直接 `dynamic_extent` と数値を並べます。

## 実際に動かしてみる

```cpp
#include <array>
#include <mdspan>
#include <print>

int main() {
  std::array<int, 6> data = {1, 2, 3, 4, 5, 6};

  // 2 x 3 の行列として見る（大きさは実行時に渡す）
  std::mdspan<int, std::dextents<std::size_t, 2>> m(data.data(), 2, 3);

  std::println("{} x {}", m.extent(0), m.extent(1));
  std::println("m[1, 2] = {}", m[1, 2]);
}
```

```text title="実行結果"
2 x 3
m[1, 2] = 6
```

## ゲームでの使いどころ

画像やグリッドのデータを、`vector` の上に、2 次元の見え方で重ねるときに使います。

## よくあるミス

??? failure "大きさを渡し忘れる"
    動的な次元の大きさは、構築のときに必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`extents`](extents.md) | 元の型 |
| [`dynamic_extent`](dynamic_extent.md) | 動的を表す値 |
| [`mdspan`](mdspan.md) | 使う側 |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::dextents](https://cpprefjp.github.io/reference/mdspan/dextents.html)
- [cppreference: std::dextents](https://en.cppreference.com/w/cpp/container/mdspan/extents)

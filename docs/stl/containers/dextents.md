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

2 次元の画像のように、縦横の大きさが実行時に決まる `mdspan` を作りたいとき、`extents<size_t, dynamic_extent, dynamic_extent>` と書くのは長いです。`dextents<size_t, 2>` と書けば、同じ型になります。

!!! tip "ポイント"
    - `dextents<IndexType, Rank>` = `extents<IndexType, dynamic_extent, ...>`（Rank 個）。
    - 次元の数だけを指定する。
    - `mdspan` のテンプレート引数に使う。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::dextents {#dextents}

```cpp
template <class IndexType, std::size_t Rank>
using dextents = /* Rank 個の dynamic_extent を持つ extents */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `IndexType` | 型 | 添字の型 |
| `Rank` | size_t | 次元の数 |

- 戻り値: `extents` の型
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <cstddef>
#include <mdspan>
#include <print>

int main() {
  std::dextents<std::size_t, 2> e(3, 4);
  std::println("{} {}", e.extent(0), e.extent(1));
}
```

```text title="実行結果"
3 4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 実行時にサイズが決まる 2 次元配列 | `std::mdspan<float, std::dextents<std::size_t, 2>>` |

## よくあるミス

??? failure "一部の次元だけ固定したい"
    `dextents` はすべて動的です。一部を固定するなら `extents` を直接書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`extents`](extents.md) | 次元ごとに固定・動的を選ぶ |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] すべて動的な extents の別名
    - [x] 次元の数を指定する
    - [x] mdspan で使う

## 関連ページ

- [cpprefjp: std::dextents](https://cpprefjp.github.io/reference/mdspan/dextents.html)
- [cppreference: std::dextents](https://en.cppreference.com/w/cpp/container/mdspan/extents)

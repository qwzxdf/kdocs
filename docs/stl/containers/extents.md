---
title: std::extents
summary: "mdspan の「各次元の大きさ」を表す型。コンパイル時に決める次元と、実行時に決める次元を混ぜられる。"
order: 30
tags:
  - コンテナ
---

# std::extents

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <mdspan>`
</div>

`std::extents` は、**[`mdspan`](mdspan.md) の各次元の大きさ**を表す型です。次元ごとに「コンパイル時に決まる大きさ」か「実行時に決まる大きさ（`std::dynamic_extent`）」を選べます。固定の次元はメモリにも載らず、コンパイラが最適化できます。全部が実行時の次元なら、`std::dextents<IndexType, 次元数>` と短く書けます。

!!! tip "ポイント"
    - `extents<int, 4, dynamic_extent>` は「1 次元目は 4 固定、2 次元目は実行時」。
    - 全部が実行時なら `std::dextents<int, 2>`（2 次元）。
    - mdspan を作るとき、型として渡す。普段は `mdspan(data, 幅, 高さ)` のように書けば自動で決まる。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 宣言

```cpp
template <class IndexType, std::size_t... Extents>
class extents;

template <class IndexType, std::size_t Rank>
using dextents = /* 全部が dynamic_extent の extents */;
```

## 関数の詳しい説明

### extent {#extent}

```cpp
constexpr index_type extent(rank_type r) const noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | `rank_type` | 次元の番号（0 始まり） |

- 戻り値: その次元の大きさ
- 計算量: O(1)

```cpp
#include <mdspan>
#include <print>

int main() {
  // 1 次元目は 4 で固定、2 次元目は実行時に決める（ここでは 5）
  std::extents<int, 4, std::dynamic_extent> e(5);

  std::println("{} x {} / 次元数 {} / 実行時に決まる次元 {}",
               e.extent(0), e.extent(1), e.rank(), e.rank_dynamic());
}
```

```text title="実行結果"
4 x 5 / 次元数 2 / 実行時に決まる次元 1
```

### rank, rank_dynamic {#rank}

```cpp
static constexpr rank_type rank() noexcept;
static constexpr rank_type rank_dynamic() noexcept;
```

- 戻り値: 全部の次元数 / 実行時に決まる次元の数
- 計算量: O(1)

### static_extent {#static_extent}

```cpp
static constexpr size_t static_extent(rank_type r) noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | `rank_type` | 次元の番号 |

- 戻り値: コンパイル時に決まる大きさ。実行時なら `std::dynamic_extent`
- 計算量: O(1)

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定幅 16 のタイルマップ（高さだけ可変） | `extents<int, 16, dynamic_extent>` |
| 画像（幅・高さとも実行時） | `dextents<int, 2>` |

## よくあるミス

??? failure "次元の順番を取り違える"
    `extents<int, W, H>` の並びは、`mdspan` の添字 `m[i, j]` の並びと同じです。幅と高さのどちらが先かは、自分で決めて統一します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::mdspan`](mdspan.md) | extents と layout を組み合わせて、配列を多次元として見る |
| [`layout_right`](layout_right.md) | 行優先（既定） |
| [`layout_left`](layout_left.md) | 列優先 |

## コンパイラ対応

C++23 の機能です。GCC 14 / Clang 18 / MSVC 19.39（VS 2022 17.9）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] mdspan の各次元の大きさ
    - [x] コンパイル時と実行時を次元ごとに選べる
    - [x] 全部実行時なら `dextents`

## 関連ページ

- [cpprefjp: std::extents](https://cpprefjp.github.io/reference/mdspan/extents.html)
- [cppreference: std::extents](https://en.cppreference.com/w/cpp/container/extents)

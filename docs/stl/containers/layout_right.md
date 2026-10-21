---
title: std::layout_right
summary: "多次元の添字を、1 次元の位置に変える規則（行優先）。mdspan の既定。"
order: 31
tags:
  - コンテナ
---

# std::layout_right

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <mdspan>`
</div>

`std::layout_right` は、**多次元の添字 `(i, j)` を、メモリ上の 1 次元の位置に変える規則**のうち、**行優先（row-major）**のものです。`mdspan` の既定の規則で、C / C++ の配列 `a[i][j]` と同じ並びです。**最後の添字が 1 つずつ隣り合って**並びます。

!!! tip "ポイント"
    - `m(i, j)` の位置は `i * 列数 + j`。同じ行の要素が隣り合う。
    - `mdspan` の既定。何も指定しなければこれ。
    - DirectX（HLSL の行列）を `float[4][4]` で持つ場合も、この並び。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 宣言

```cpp
struct std::layout_right {
  template <class Extents>
  class mapping;
};
```

## 関数の詳しい説明

### mapping::operator() {#operator}

```cpp
constexpr index_type operator()(Indices... idx) const noexcept;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `idx...` | 整数 | 各次元の添字 |

- 戻り値: メモリ上の位置（先頭からの要素数）
- 計算量: O(1)

```cpp
#include <mdspan>
#include <print>

int main() {
  using Ext = std::extents<int, 2, 3>;  // 2 行 3 列
  std::layout_right::mapping<Ext> m;

  // (1, 0) は 2 行目の先頭。(0, 1) は 1 行目の 2 つ目
  std::println("(1,0) → {} / (0,1) → {} / 全体 {}", m(1, 0), m(0, 1), m.required_span_size());
}
```

```text title="実行結果"
(1,0) → 3 / (0,1) → 1 / 全体 6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| タイルマップ `tiles[y][x]`（行ごとに連続） | `mdspan<Tile, dextents<int, 2>, layout_right>` |
| 画像の 1 ピクセル行を連続して処理する | 同じ行の要素が隣り合うので、キャッシュに優しい |

## よくあるミス

??? failure "列方向にばかり回す"
    行優先で列方向（`i` を内側のループ）に回すと、要素が離れていてキャッシュに乗りにくくなります。内側のループは最後の添字にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::layout_left`](layout_left.md) | 列優先（先頭の添字が隣り合う） |
| [`std::layout_stride`](layout_stride.md) | 次元ごとの歩幅を自分で指定 |
| [`std::mdspan`](mdspan.md) | 配列を多次元として見る |

## コンパイラ対応

C++23 の機能です。GCC 14 / Clang 18 / MSVC 19.39 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 行優先（最後の添字が隣り合う）
    - [x] `mdspan` の既定
    - [x] 内側のループは最後の添字

## 関連ページ

- [cpprefjp: std::layout_right](https://cpprefjp.github.io/reference/mdspan/layout_right.html)
- [cppreference: std::layout_right](https://en.cppreference.com/w/cpp/container/layout_right)

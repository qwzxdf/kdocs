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

`std::layout_left` は、**多次元の添字 `(i, j)` をメモリ上の 1 次元の位置に変える規則<strong>のうち、</strong>列優先（column-major）<strong>のものです。</strong>最初の添字が 1 つずつ隣り合って**並びます。Fortran や、一部の数学ライブラリ（行列を列ごとに持つもの）と同じ並びです。

!!! tip "ポイント"
    - `m(i, j)` の位置は `i + 行数 * j`。同じ列の要素が隣り合う。
    - 既定の [`layout_right`](layout_right.md) の反対。
    - 外部のライブラリが列優先のメモリを要求するときに使う。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 宣言

```cpp
struct std::layout_left {
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
  std::layout_left::mapping<Ext> m;

  // 列優先: (1, 0) は 1 つ隣、(0, 1) は 1 列ぶん（2 つ）先
  std::println("(1,0) → {} / (0,1) → {} / 全体 {}", m(1, 0), m(0, 1), m.required_span_size());
}
```

```text title="実行結果"
(1,0) → 1 / (0,1) → 2 / 全体 6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 列優先の行列を要求する外部ライブラリとのやり取り | `mdspan<float, ext, layout_left>` |

## よくあるミス

??? failure "layout_right のつもりで渡す"
    列優先のデータを行優先として読むと、転置された結果になります。ライブラリの仕様（行優先か列優先か）を確認します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::layout_right`](layout_right.md) | 行優先（既定） |
| [`std::layout_stride`](layout_stride.md) | 次元ごとの歩幅を指定 |

## コンパイラ対応

C++23 の機能です。GCC 14 / Clang 18 / MSVC 19.39 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 列優先（最初の添字が隣り合う）
    - [x] `layout_right` の反対
    - [x] 外部ライブラリとの連携で使う

## 関連ページ

- [cpprefjp: std::layout_left](https://cpprefjp.github.io/reference/mdspan/layout_left.html)
- [cppreference: std::layout_left](https://en.cppreference.com/w/cpp/container/layout_left)

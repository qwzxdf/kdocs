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

`std::layout_stride` は、**次元ごとの「歩幅（次の要素まで何個とぶか）」を自分で指定する**配置の規則です。行や列を飛ばして見たり、大きな画像の一部分を切り出して見たりするときに使います。`layout_right` / `layout_left` では表せない並びを `mdspan` で扱えます。

!!! tip "ポイント"
    - `m(i, j)` の位置は `i * stride0 + j * stride1`。
    - 歩幅は、`mapping` のコンストラクタに渡す。
    - 大きな 2 次元配列から、一部分を切り出す（`submdspan`）と、この規則になる。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 宣言

```cpp
struct std::layout_stride {
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

- 戻り値: メモリ上の位置（`Σ idx × stride`）
- 計算量: O(1)

```cpp
#include <array>
#include <mdspan>
#include <print>

int main() {
  using Ext = std::dextents<int, 2>;
  // 2 行 3 列。行の歩幅は 6、列の歩幅は 2（要素を 1 つおきに見る）
  std::layout_stride::mapping<Ext> m(Ext(2, 3), std::array<int, 2>{6, 2});

  std::println("(1,2) → {} / 必要な長さ {}", m(1, 2), m.required_span_size());
}
```

```text title="実行結果"
(1,2) → 10 / 必要な長さ 11
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 大きな画像から、一部（タイル）だけを切り出して見る | 歩幅は元の幅のまま、`extents` だけを小さくする |
| RGBA の画像から R チャンネルだけを見る | 歩幅を 4 にする |

## よくあるミス

??? failure "required_span_size を無視する"
    元になる配列の長さは、`required_span_size()` 以上にします。足りないと範囲外アクセスです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::layout_right`](layout_right.md) | 隙間のない行優先 |
| [`std::layout_left`](layout_left.md) | 隙間のない列優先 |
| [`std::views::stride`](../algorithms/views/stride.md) | 1 次元で n 個おきに見る |

## コンパイラ対応

C++23 の機能です。GCC 14 / Clang 18 / MSVC 19.39 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 次元ごとの歩幅を自分で決める
    - [x] 切り出しや間引きに向く
    - [x] `required_span_size()` を確認

## 関連ページ

- [cpprefjp: std::layout_stride](https://cpprefjp.github.io/reference/mdspan/layout_stride.html)
- [cppreference: std::layout_stride](https://en.cppreference.com/w/cpp/container/layout_stride)

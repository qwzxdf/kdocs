---
title: std::aligned_accessor
summary: "要素が指定した境界に並ぶことを保証する mdspan のアクセサ。"
order: 900
tags:
  - コンテナ
---

# std::aligned_accessor

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <mdspan>`
</div>

SIMD で処理するデータは、32 や 64 バイトの境界に並んでいてほしい。`std::aligned_accessor<T, N>` は、`mdspan` のアクセサーで、「このデータは `N` バイトの境界にある」と約束します。内部で `assume_aligned` を使って、コンパイラの最適化を助けます。

!!! tip "ポイント"
    - `mdspan` の 4 番目のテンプレート引数に指定する
    - `aligned_accessor<float, 32>` で、32 バイト境界を約束する
    - 約束を破ると未定義動作
    - C++26

!!! info "このページを読む前に"
    [`default_accessor`](default_accessor.md) を先に読んでください。

## 関数の詳しい説明

### std::aligned_accessor {#aligned_accessor}

<span class="ver ver-26">C++26</span>

```cpp
template <class ElementType, std::size_t ByteAlignment>
struct aligned_accessor {
  using offset_policy = std::default_accessor<ElementType>;
  using element_type = ElementType;
  using reference = ElementType&;
  using data_handle_type = ElementType*;
  constexpr reference access(data_handle_type p, std::size_t i) const noexcept;
};
```

`access` が、内部で `std::assume_aligned<ByteAlignment>(p)` を通した参照を返します。

`ByteAlignment` は、2 のべき乗で、`ElementType` のアライメント以上でなければなりません。

データを実際にその境界に置くのは、確保する側の責任です。`alignas` の配列や、アライメントつきで確保したメモリを使います。

## 使い方の形

手元の MSVC では使えないので、動かさずに、形だけを示します。

```cpp
alignas(32) float data[16] = {};
using Acc = std::aligned_accessor<float, 32>;
std::mdspan<float, std::extents<std::size_t, 4, 4>, std::layout_right, Acc> m(data);
```

## ゲームでの使いどころ

行列やベクトルの SIMD 処理で、アライメントを型で約束して、コンパイラに速い命令を選ばせます。

## よくあるミス

??? failure "境界に置いていないデータに使う"
    未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`default_accessor`](default_accessor.md) | 標準のアクセサー |
| `std::assume_aligned` | 内部で使う |
| [`mdspan`](mdspan.md) | 使う側 |

## コンパイラ対応

C++26 の機能です。手元の MSVC（Visual Studio 2026）では未対応のため、サンプルは動かしていません。

## 関連ページ

- [cpprefjp: std::aligned_accessor](https://cpprefjp.github.io/reference/mdspan/aligned_accessor.html)
- [cppreference: std::aligned_accessor](https://en.cppreference.com/w/cpp/container/mdspan/aligned_accessor)

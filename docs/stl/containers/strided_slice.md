---
title: std::strided_slice
summary: "submdspan で「開始位置・長さ・間隔」を指定する範囲。"
order: 900
tags:
  - コンテナ
---

# std::strided_slice

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <mdspan>`
</div>

`mdspan` の一部を、1 つおきに取り出したいことがあります（偶数番目の列だけ、など）。`strided_slice{offset, extent, stride}` は、開始位置・長さ・間隔を指定する範囲で、`submdspan` に渡します。

!!! tip "ポイント"
    - `offset`・`extent`・`stride` の 3 つのメンバ。
    - `stride` が 2 なら 1 つおき。
    - C++26 の機能。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::strided_slice {#strided_slice}

```cpp
template <class OffsetType, class ExtentType, class StrideType>
struct strided_slice {
  OffsetType offset;
  ExtentType extent;
  StrideType stride;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `offset` | 整数 | 開始位置 |
| `extent` | 整数 | 範囲の長さ |
| `stride` | 整数 | 間隔 |

- 戻り値: なし（範囲の指定）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <mdspan>
#include <print>

int main() {
  std::strided_slice s{.offset = 0, .extent = 6, .stride = 2};
  std::println("{} {} {}", s.offset, s.extent, s.stride);
}
```

```text title="実行結果"
0 6 2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 画像の列を 1 つおきに取り出す | `std::strided_slice{.offset = 0, .extent = 6, .stride = 2}` |

## よくあるミス

??? failure "`extent` を終端位置と思う"
    `extent` は取り出す範囲の「長さ」です。終端の位置ではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`submdspan`](submdspan.md) | 一部を取り出す |
| [`full_extent`](full_extent.md) | 全部 |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 開始・長さ・間隔の範囲
    - [x] submdspan の引数
    - [x] C++26

## 関連ページ

- [cpprefjp: std::strided_slice](https://cpprefjp.github.io/reference/mdspan/strided_slice.html)
- [cppreference: std::strided_slice](https://en.cppreference.com/w/cpp/container/mdspan/strided_slice)

---
title: std::submdspan
summary: "mdspan の一部（行・列・範囲）を取り出して、新しい mdspan にする。"
order: 900
tags:
  - コンテナ
---

# std::submdspan

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <mdspan>`
</div>

画像の 1 行だけ、2 次元配列の一部の矩形だけを処理したいとき、元のデータをコピーせずに、その部分を指す `mdspan` を作れるのが `submdspan` です。行や列を 1 つ指定したり、範囲を指定したり、`full_extent` で全部を指定したりします。

!!! tip "ポイント"
    - 次元の数と同じだけのスライスを渡す。
    - 1 つの添字を渡すと、その次元は消える（次元が 1 つ減る）。
    - コピーはしない（元の配列を指す）。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::submdspan {#submdspan}

```cpp
template <class T, class Extents, class Layout, class Accessor, class... Slices>
constexpr auto submdspan(const mdspan<T, Extents, Layout, Accessor>& src, Slices... slices);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `src` | mdspan | 元の mdspan |
| `slices...` | スライス | 各次元の指定（整数・範囲・`full_extent`） |

- 戻り値: 一部を指す新しい `mdspan`
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <mdspan>
#include <print>

int main() {
  int data[] = {1, 2, 3, 4, 5, 6};
  std::mdspan m(data, 2, 3);
  auto row = std::submdspan(m, 1, std::full_extent);
  std::println("{} {} {}", row[0], row[1], row[2]);
}
```

```text title="実行結果"
4 5 6
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 画像の 1 行を取り出して処理 | `auto row = std::submdspan(img, y, std::full_extent);` |

## よくあるミス

??? failure "元の配列が先に消える"
    `submdspan` は元のデータを指すだけです。元のデータが生きている間だけ使えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`full_extent`](full_extent.md) | 全部を表す |
| [`strided_slice`](strided_slice.md) | 間隔つきの範囲 |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] mdspan の一部を取り出す
    - [x] コピーしない
    - [x] C++26

## 関連ページ

- [cpprefjp: std::submdspan](https://cpprefjp.github.io/reference/mdspan/submdspan.html)
- [cppreference: std::submdspan](https://en.cppreference.com/w/cpp/container/mdspan/submdspan)

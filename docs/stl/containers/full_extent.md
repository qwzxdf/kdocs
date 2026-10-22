---
title: std::full_extent
summary: "submdspan で「この次元は全部」を表す目印。"
order: 900
tags:
  - コンテナ
---

# std::full_extent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <mdspan>`
</div>

`mdspan` の一部だけを取り出す `submdspan(m, 行, 列)` で、「この次元は全部ほしい」を表したいことがあります。それが `std::full_extent` です。行を 1 つ指定して、列は全部、のような使い方をします。

!!! tip "ポイント"
    - `submdspan` の引数として使う。
    - スライスの「全部」を表す。
    - 数値（1 つの添字）や範囲（`pair`）と同じ位置に書く。

!!! info "このページを読む前に"
    [`std::mdspan`](mdspan.md) を先に読んでください。

## 関数の詳しい説明

### std::full_extent {#full_extent}

```cpp
struct full_extent_t { explicit full_extent_t() = default; };
inline constexpr full_extent_t full_extent{};
```

- 戻り値: なし（目印）
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <mdspan>
#include <print>
#include <type_traits>

int main() {
  std::println("{}", std::is_same_v<std::remove_const_t<decltype(std::full_extent)>, std::full_extent_t>);
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 画像の 1 行だけを取り出す | `std::submdspan(img, 3, std::full_extent)` |

## よくあるミス

??? failure "次元の数を間違える"
    `submdspan` に渡すスライスは、次元の数と同じだけ必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`submdspan`](submdspan.md) | 一部を取り出す |
| [`strided_slice`](strided_slice.md) | 間隔つきの範囲 |

## コンパイラ対応

C++26 の機能です。対応は新しい標準ライブラリに限られます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 「全部」を表す目印
    - [x] submdspan の引数
    - [x] C++26

## 関連ページ

- [cpprefjp: std::full_extent](https://cpprefjp.github.io/reference/mdspan/full_extent_t.html)
- [cppreference: std::full_extent](https://en.cppreference.com/w/cpp/container/mdspan/full_extent_t)

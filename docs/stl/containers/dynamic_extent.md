---
title: std::dynamic_extent
summary: "span や mdspan で「要素数が実行時に決まる」ことを表す定数。"
order: 900
tags:
  - コンテナ
---

# std::dynamic_extent

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <span>`
</div>

`std::span<int, 3>` は要素数 3 に固定され、`std::span<int>` は実行時に決まります。この「実行時に決まる」ことを表す特別な値が `std::dynamic_extent` です。`std::mdspan` の `extents` でも、次元が実行時に決まることを示すのに使います。

!!! tip "ポイント"
    - `std::span<T>` の `extent` が、これと等しい
    - 値は `size_t` の最大値（`-1`）
    - `extents<size_t, 3, dynamic_extent>` のように、次元ごとに指定できる
    - `<span>` で定義される

!!! info "このページを読む前に"
    [`std::span`](span.md) を先に読んでください。

## 関数の詳しい説明

### std::dynamic_extent {#dynamic_extent}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr std::size_t dynamic_extent = std::numeric_limits<std::size_t>::max();
```

`span<T>` と書くと、`span<T, dynamic_extent>` の意味です。`extent` が `dynamic_extent` でない `span` は、要素数が型に入っているので、`size()` は定数で、サイズを持つ領域がありません。

`mdspan` の `extents<IndexType, 3, dynamic_extent>` は、1 次元目が 3 に固定、2 次元目が実行時に決まる、を表します。`dextents<IndexType, N>` は、`N` 個の次元がすべて動的な `extents` の別名です。

値が `size_t` の最大値なので、「配列の大きさが実際にその値」という意味と衝突しませんが、比較のとき、符号つきの整数と混ぜないように注意します。

## 実際に動かしてみる

```cpp
#include <array>
#include <mdspan>
#include <print>
#include <span>

int main() {
  std::println("動的: {}", std::span<int>::extent == std::dynamic_extent);
  std::println("固定: {}", std::span<int, 3>::extent);

  // mdspan の extents で、動的な次元を表す
  using E = std::extents<std::size_t, 3, std::dynamic_extent>;
  E e(4);  // 動的な次元だけを渡す
  std::println("{} x {}", e.extent(0), e.extent(1));
  std::println("静的な次元: {}", E::static_extent(0));
}
```

```text title="実行結果"
動的: true
固定: 3
3 x 4
静的な次元: 3
```

## ゲームでの使いどころ

`span` や `mdspan` の型を書くときに出てきます。値を直接使う場面は、あまりありません。

## よくあるミス

??? failure "符号つき整数と比べる"
    `-1` と比べるような書き方は避けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`span`](span.md) | 使われる場所 |
| [`extents`](extents.md) | 次元の大きさの型 |
| [`dextents`](dextents.md) | すべて動的な `extents` |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::dynamic_extent](https://cpprefjp.github.io/reference/span/dynamic_extent.html)
- [cppreference: std::dynamic_extent](https://en.cppreference.com/w/cpp/container/span/dynamic_extent)

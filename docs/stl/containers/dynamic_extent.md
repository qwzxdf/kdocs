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

`std::span<int, 3>` は要素数を型で固定し、`std::span<int>` は実行時に決まる要素数を持ちます。後者の「実行時に決まる」ことを表す特別な値が `std::dynamic_extent` です。`span<int>::extent` は、この値と等しくなります。

!!! tip "ポイント"
    - `span<T>` の `extent` が、これと等しい。
    - 値は `size_t` の最大値（`-1`）。
    - `mdspan` の `extents` でも、動的な次元を表すのに使う。

!!! info "このページを読む前に"
    [`std::span`](span.md) を先に読んでください。

## 関数の詳しい説明

### std::dynamic_extent {#dynamic_extent}

```cpp
inline constexpr std::size_t dynamic_extent = std::numeric_limits<std::size_t>::max();
```

- 戻り値: 定数
- 計算量: なし


## 実際に動かしてみる

```cpp
#include <print>
#include <span>

int main() {
  std::println("{}", std::span<int>::extent == std::dynamic_extent);
  std::println("{}", std::span<int, 3>::extent);
}
```

```text title="実行結果"
true
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定長か動的かをコンパイル時に分岐する | `if constexpr (S::extent == std::dynamic_extent)` |

## よくあるミス

??? failure "実際の要素数と思う"
    `dynamic_extent` は「不定」を表す目印で、要素数そのものではありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`span`](span.md) | 要素数を持つ view |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素数が実行時に決まることを表す
    - [x] size_t の最大値
    - [x] span / mdspan で使う

## 関連ページ

- [cpprefjp: std::dynamic_extent](https://cpprefjp.github.io/reference/span/dynamic_extent.html)
- [cppreference: std::dynamic_extent](https://en.cppreference.com/w/cpp/container/span/dynamic_extent)

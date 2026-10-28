---
title: std::ranges::ssize
summary: "範囲の要素数を、符号付きの整数で返す。"
order: 900
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::ssize

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

範囲（ranges）のアルゴリズムは、配列、コンテナ、自作の範囲、ビューのどれでも受け取れます。それぞれの範囲から符号つきの要素数を取り出す書き方を、1 つにそろえたのが `std::ranges::ssize` です。メンバー関数 `v.ssize()` と、非メンバー関数 `ssize(v)` のどちらがあっても、同じ書き方で呼べます。

!!! tip "ポイント"
    - `std::ranges::ssize(r)` は範囲 `r` の符号つきの要素数
    - メンバー関数と非メンバー関数のどちらでも自動で選ばれる
    - 配列や、独自の範囲型にも使える
    - カスタマイズ ポイント オブジェクトなので、名前空間の探索の影響を受けない

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::ssize {#ssize}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* カスタマイズ ポイント オブジェクト */ ssize;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 対象の範囲 |

`std::ranges::ssize(r)` は、`r` の型に合わせて、適した方法で符号つきの要素数を取り出します。メンバー関数があればそれを、なければ ADL で見つかる非メンバー関数を呼びます。配列には専用の実装が使われます。

カスタマイズ ポイント オブジェクトは、関数ではなく関数オブジェクトです。そのため、名前空間の探索（ADL）によって、意図しない関数が選ばれる事故を避けられます。アルゴリズムの内部は、この方法で範囲を扱います。

条件を満たさない型（要素にアクセスできない型）に呼ぶと、コンパイルエラーです。

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  const std::vector<int> v = {10, 20, 30};
  std::println("符号つきの要素数 = {}", std::ranges::ssize(v) - 4);
}
```

```text title="実行結果"
符号つきの要素数 = -1
```

## ゲームでの使いどころ

範囲を受け取る自作のテンプレートで、先頭や要素数を取り出すときに使います。

```cpp
template <std::ranges::range R>
void Dump(R&& r) {
  for (auto it = std::ranges::begin(r); it != std::ranges::end(r); ++it) Print(*it);
}
```

## よくあるミス

??? failure "範囲でない型に呼んでコンパイルエラーになる"
    `std::ranges::range` で先に確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`begin`](../iterator/begin.md) | 従来の `std::begin` |
| [`range`](range.md) | 範囲のコンセプト |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::ranges::ssize(r)` は範囲の符号つきの要素数
    - [x] メンバーでも非メンバーでも使える
    - [x] 配列や自作の範囲にも使える

## 関連ページ

- [cpprefjp: std::ranges::ssize](https://cpprefjp.github.io/reference/ranges/ssize.html)
- [cppreference: std::ranges::ssize](https://en.cppreference.com/w/cpp/ranges/ssize)

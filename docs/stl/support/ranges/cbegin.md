---
title: std::ranges::cbegin
summary: "範囲の先頭を指す、const のイテレータを返す。"
order: 900
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::cbegin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

範囲（ranges）のアルゴリズムは、配列、コンテナ、自作の範囲、ビューのどれでも受け取れます。それぞれの範囲から先頭を指す読み取り専用のイテレーターを取り出す書き方を、1 つにそろえたのが `std::ranges::cbegin` です。メンバー関数 `v.cbegin()` と、非メンバー関数 `cbegin(v)` のどちらがあっても、同じ書き方で呼べます。

!!! tip "ポイント"
    - `std::ranges::cbegin(r)` は範囲 `r` の範囲の先頭（const）
    - メンバー関数と非メンバー関数のどちらでも自動で選ばれる
    - 配列や、独自の範囲型にも使える
    - カスタマイズ ポイント オブジェクトなので、名前空間の探索の影響を受けない

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::cbegin {#cbegin}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* カスタマイズ ポイント オブジェクト */ cbegin;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 対象の範囲 |

`std::ranges::cbegin(r)` は、`r` の型に合わせて、適した方法で先頭を指す読み取り専用のイテレーターを取り出します。メンバー関数があればそれを、なければ ADL で見つかる非メンバー関数を呼びます。配列には専用の実装が使われます。

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
  std::println("範囲の先頭（const） = {}", std::is_same_v<decltype(*std::ranges::cbegin(v)), const int&>);
}
```

```text title="実行結果"
範囲の先頭（const） = true
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
    - [x] `std::ranges::cbegin(r)` は範囲の範囲の先頭（const）
    - [x] メンバーでも非メンバーでも使える
    - [x] 配列や自作の範囲にも使える

## 関連ページ

- [cpprefjp: std::ranges::cbegin](https://cpprefjp.github.io/reference/ranges/cbegin.html)
- [cppreference: std::ranges::cbegin](https://en.cppreference.com/w/cpp/ranges/cbegin)

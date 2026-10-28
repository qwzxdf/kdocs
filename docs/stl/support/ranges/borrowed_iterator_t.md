---
title: std::ranges::borrowed_iterator_t
summary: "範囲のイテレータの型（借りられない範囲なら dangling）を取り出す型の別名。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::borrowed_iterator_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

イテレーターを返すアルゴリズムの戻り値の型は、渡された範囲が借用できるかで変わります。借用できれば普通のイテレーター、できなければ `dangling` です。その型を計算するのが `std::ranges::borrowed_iterator_t<R>` です。

!!! tip "ポイント"
    - `borrowed_iterator_t<R>`: 借用できる範囲なら `iterator_t<R>`、できなければ `dangling`
    - アルゴリズムの戻り値の型の定義に使われる
    - 自作のアルゴリズムでも、同じ作法で書ける
    - 直接書く機会は少ない

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::borrowed_iterator_t {#borrowed_iterator_t}

<span class="ver ver-20">C++20</span>

```cpp
template <ranges::range R>
using borrowed_iterator_t =
    std::conditional_t<borrowed_range<R>, iterator_t<R>, dangling>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 範囲 | 対象の範囲の型 |

`std::vector<int>&`（左辺値）なら `std::vector<int>::iterator`、一時的な `std::vector<int>` なら `std::ranges::dangling` になります。

自作の検索関数も、この型を戻り値にしておくと、標準のアルゴリズムと同じ安全性を得られます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  using Lvalue = std::ranges::borrowed_iterator_t<std::vector<int>&>;
  using Rvalue = std::ranges::borrowed_iterator_t<std::vector<int>>;
  std::println("左辺値は iterator : {}", std::is_same_v<Lvalue, std::vector<int>::iterator>);
  std::println("一時は dangling   : {}", std::is_same_v<Rvalue, std::ranges::dangling>);
}
```

```text title="実行結果"
左辺値は iterator : true
一時は dangling   : true
```

## ゲームでの使いどころ

自作の検索アルゴリズムの戻り値に使います。

```cpp
template <std::ranges::input_range R, class T>
std::ranges::borrowed_iterator_t<R> FindFirst(R&& r, const T& value);
```

## よくあるミス

??? failure "通常の `iterator_t` を返して、一時オブジェクトの危険に気づけない"
    `borrowed_iterator_t` を返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`dangling`](dangling.md) | 印の型 |
| [`borrowed_range`](borrowed_range.md) | 借用できる範囲 |
| [`iterator_t`](iterator_t.md) | 範囲のイテレーターの型 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `borrowed_iterator_t<R>` は借用できればイテレーター、できなければ `dangling`
    - [x] アルゴリズムの戻り値の型に使われる
    - [x] 自作のアルゴリズムでも同じ作法

## 関連ページ

- [cpprefjp: std::ranges::borrowed_iterator_t](https://cpprefjp.github.io/reference/ranges/borrowed_iterator_t.html)
- [cppreference: std::ranges::borrowed_iterator_t](https://en.cppreference.com/w/cpp/ranges/borrowed_iterator_t)

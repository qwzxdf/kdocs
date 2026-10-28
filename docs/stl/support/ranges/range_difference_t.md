---
title: std::ranges::range_difference_t
summary: "範囲のイテレータの差の型を取り出す型の別名。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::range_difference_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

範囲を受け取る自作のテンプレートで、「この範囲の要素の型は何か」を知りたい場面があります。コンテナなら `T::value_type` と書けますが、配列やビューにはありません。`std::ranges::range_difference_t<R>` は、<strong>任意の範囲 `R` のイテレーターの差の型</strong>を取り出します。

!!! tip "ポイント"
    - `std::ranges::range_difference_t<R>` は範囲 `R` のイテレーターの差の型
    - 配列、コンテナ、ビューのどれにも使える
    - メンバー型（`value_type` など）がなくてもよい
    - 戻り値は型。実行時のコストはない

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::range_difference_t {#range_difference_t}

<span class="ver ver-20">C++20</span>

```cpp
template <ranges::range R>
using range_difference_t = /* イテレーターの差の型 */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 範囲 | 対象の範囲の型 |

`R` の `begin` と `end` から計算した型を返します。`value_type` のようなメンバー型を持たない配列やビューにも、同じ書き方で使えます。

範囲でない型を渡すと、型が存在せず、コンパイルエラーになります。

## 実際に動かしてみる

```cpp
#include <cstddef>
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  std::println("vector<int> のイテレーターの差 は std::ptrdiff_t : {}", std::is_same_v<std::ranges::range_difference_t<std::vector<int>>, std::ptrdiff_t>);
}
```

```text title="実行結果"
vector<int> のイテレーターの差 は std::ptrdiff_t : true
```

## ゲームでの使いどころ

範囲を受け取る自作のテンプレートで、戻り値や一時変数の型に使います。

```cpp
template <std::ranges::input_range R>
std::vector<std::ranges::range_value_t<R>> ToVector(R&& r);
```

## よくあるミス

??? failure "`std::decay_t` と取り違える"
    この別名は範囲から型を計算します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`range`](range.md) | 範囲のコンセプト |
| [`iterator_t`](iterator_t.md) | イテレーターの型 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ranges::range_difference_t<R>` は範囲のイテレーターの差の型
    - [x] 配列やビューにも使える
    - [x] 自作のテンプレートの型の計算に使う

## 関連ページ

- [cpprefjp: std::ranges::range_difference_t](https://cpprefjp.github.io/reference/ranges/range_difference_t.html)
- [cppreference: std::ranges::range_difference_t](https://en.cppreference.com/w/cpp/ranges/range_difference_t)

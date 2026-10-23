---
title: std::common_comparison_category
summary: "複数の順序型から、全部を含む共通の順序型を求める。"
order: 900
group: 比較（<compare>）
tags:
  - 型・言語サポート
---

# std::common_comparison_category

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <compare>`
</div>

複数のメンバーを持つ構造体の `<=>` は、メンバーごとの比較結果を合成して作ります。メンバーの型によって、比較の結果が `strong_ordering` だったり、`partial_ordering` だったりします。合成した結果は、その中で一番弱い型になります。`std::common_comparison_category` は、<strong>複数の順序型の共通の型（一番弱い型）</strong>を返します。

!!! tip "ポイント"
    - `std::common_comparison_category_t<A, B>` は一番弱い順序型
    - `strong` と `partial` の共通は `partial`
    - `= default` の `operator<=>` の戻り値の決定に使われる
    - `<compare>` で宣言される

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::common_comparison_category_t {#common_comparison_category}

<span class="ver ver-20">C++20</span>

```cpp
template <class... Ts>
using common_comparison_category_t = typename common_comparison_category<Ts...>::type;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `Ts...` | 順序型の並び | 共通の型を求めたい順序型 |

`strong_ordering` と `weak_ordering` なら `weak_ordering`、`strong_ordering` と `partial_ordering` なら `partial_ordering` になります。順序型でない型が混ざると、`void` を返します。

`auto operator<=>(const T&) const = default;` が、メンバーの比較結果を合成して戻り値の型を決めるとき、同じ規則が働いています。

## 実際に動かしてみる

```cpp
#include <compare>
#include <print>
#include <type_traits>

int main() {
  using R1 = std::common_comparison_category_t<std::strong_ordering, std::partial_ordering>;
  using R2 = std::common_comparison_category_t<std::strong_ordering, std::weak_ordering>;
  std::println("strong と partial -> partial: {}", std::is_same_v<R1, std::partial_ordering>);
  std::println("strong と weak    -> weak   : {}", std::is_same_v<R2, std::weak_ordering>);
}
```

```text title="実行結果"
strong と partial -> partial: true
strong と weak    -> weak   : true
```

## ゲームでの使いどころ

`= default` の `<=>` を使えば、この規則は自動で働きます。直接使うのは、比較を自作するテンプレートの内部です。

## よくあるミス

??? failure "順序型でない型を混ぜる"
    `void` が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`compare_three_way_result`](compare_three_way_result.md) | `<=>` の結果の型 |
| [`strong_ordering`](strong_ordering.md) | 全順序 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.x 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `common_comparison_category_t` は順序型の中で一番弱い型
    - [x] `strong` と `partial` なら `partial`
    - [x] `= default` の `<=>` の戻り値の決定に使われる

## 関連ページ

- [cpprefjp: std::common_comparison_category](https://cpprefjp.github.io/reference/compare/common_comparison_category.html)
- [cppreference: std::common_comparison_category](https://en.cppreference.com/w/cpp/utility/common_comparison_category)

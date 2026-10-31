---
title: std::views::all
summary: "範囲を、軽いビューとして扱えるようにする。"
order: 21
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::all

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::all` は、どんな範囲でも、「ビュー」に変換する窓口です。コンテナの左辺値を渡すと、参照だけを持つ軽い `ref_view`、右辺値を渡すと、中身を所有する `owning_view`、すでにビューなら、そのまま返します。他のビュー アダプターが、内部で最初に呼びます。

!!! tip "ポイント"
    - 範囲をビューに変換する
    - コンテナの左辺値 → `ref_view`（参照だけ）
    - コンテナの右辺値 → `owning_view`（所有する）
    - ビューならそのまま。コピーされるだけ

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::views::all {#all}

<span class="ver ver-20">C++20</span>

```cpp
inline constexpr /* 未規定 */ all = /* 未規定 */;
template <class R> using all_t = decltype(views::all(std::declval<R>()));
```

| 渡すもの | 結果 |
| --- | --- |
| ビュー | そのコピー |
| コンテナの左辺値 | `ref_view<コンテナ>` |
| コンテナの右辺値 | `owning_view<コンテナ>`（C++20 の欠陥報告で追加） |

`v | std::views::filter(...)` のようなパイプラインでは、`filter` が内部で `views::all(v)` を呼んでいます。そのため、普通は意識しません。

型を書く必要があるとき（クラスのメンバーに、ビューを持つなど）は、`std::views::all_t<R>` が結果の型を教えてくれます。

左辺値のコンテナは参照しか持たないので、元のコンテナより長く生かしてはいけません。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  std::vector<int> v = {1, 2, 3};

  // 左辺値 → ref_view
  static_assert(std::is_same_v<decltype(std::views::all(v)), std::ranges::ref_view<std::vector<int>>>);

  // 右辺値 → owning_view
  auto owned = std::views::all(std::vector<int>{4, 5, 6});
  std::println("所有している要素数: {}", owned.size());

  // ビューはそのまま
  auto again = std::views::all(std::views::all(v));
  std::println("{}", again.size());
}
```

```text title="実行結果"
所有している要素数: 3
3
```

## ゲームでの使いどころ

自作のビュー アダプターを書くときに、受け取った範囲を、まず `views::all` でビューにします。

## よくあるミス

??? failure "ビューを元のコンテナより長く保持する"
    `ref_view` は参照だけです。ぶら下がります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ref_view`](ref_view.md) | 参照だけを持つ |
| [`owning_view`](owning_view.md) | 所有する |
| [`subrange`](subrange.md) | イテレータの組 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::all_t](https://cpprefjp.github.io/reference/ranges/all_t.html)
- [cppreference: std::ranges::all_t](https://en.cppreference.com/w/cpp/ranges/all_t)

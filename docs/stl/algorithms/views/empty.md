---
title: std::views::empty
summary: "要素が 1 つもない範囲を作る。"
order: 18
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::empty

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

要素が 0 個のビューが欲しい。条件分岐で、ある場合は範囲、ない場合は空の範囲を返したいときに、型をそろえる必要があります。`std::views::empty<T>` は、型 `T` の要素を 0 個持つ、空のビューです。

!!! tip "ポイント"
    - 要素が 0 個のビュー
    - `std::views::empty<int>` のように、要素の型を指定する
    - `size()` が 0、`begin() == end()`
    - コンパイル時に決まる、軽いビュー

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::views::empty {#empty}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
  requires std::is_object_v<T>
inline constexpr std::ranges::empty_view<T> empty{};
```

`empty_view<T>` は、状態を持たず、`begin()` と `end()` は `nullptr` を返します。`data()` も `nullptr` です。

使いどころは、分岐の戻り値の型をそろえることです。

```cpp
auto items = has_items ? some_view : std::views::empty<int>;   // 型が違うので、そのままでは書けない
```

型が違うビューを三項演算子で選ぶのは、できません。`std::ranges::to<std::vector>()` で具体化するか、共通の型にする工夫が要ります。

`empty_view` は、ビューを組み立てる部品として、`views::join` の中間などで使われます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>

int main() {
  auto e = std::views::empty<int>;
  std::println("要素数: {}", e.size());
  std::println("空: {}", e.empty());
  std::println("begin == end: {}", e.begin() == e.end());

  int count = 0;
  for (int x : e) {
    (void)x;
    ++count;
  }
  std::println("ループの回数: {}", count);
}
```

```text title="実行結果"
要素数: 0
空: true
begin == end: true
ループの回数: 0
```

## ゲームでの使いどころ

ビューを返す関数で、「何もない」場合の戻り値として使います。

## よくあるミス

??? failure "型の違うビューを三項演算子で選ぶ"
    コンパイルできません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`single`](single.md) | 要素が 1 個のビュー |
| [`iota`](iota.md) | 連続する値のビュー |
| [`all`](all.md) | 範囲全体のビュー |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::empty_view](https://cpprefjp.github.io/reference/ranges/empty_view.html)
- [cppreference: std::ranges::empty_view](https://en.cppreference.com/w/cpp/ranges/empty_view)

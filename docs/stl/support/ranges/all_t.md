---
title: std::views::all_t
summary: "views::all が返す view の型。"
order: 900
tags:
  - 型・言語サポート
---

# std::views::all_t

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

範囲アダプター（`views::transform` など）は、コンテナを直接受け取らず、いったん「ビュー」に変換します。コンテナの参照を持つ軽いビューにするのが `views::all` で、その結果の型が `std::views::all_t<R>` です。

!!! tip "ポイント"
    - `std::views::all_t<R>` は `views::all(r)` の結果の型
    - 左辺値のコンテナは `ref_view` になる
    - ビューはそのまま、一時のコンテナは `owning_view` になる
    - 範囲アダプターの内部で使われる

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::views::all_t {#all_t}

<span class="ver ver-20">C++20</span>

```cpp
template <ranges::viewable_range R>
using all_t = decltype(views::all(std::declval<R>()));
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `R` | 範囲 | 対象の範囲の型 |

範囲をビューに変換する `views::all` の戻り値の型です。コンテナの左辺値は、コンテナを参照する `ranges::ref_view`、一時的なコンテナは、所有権を引き取る `ranges::owning_view`、すでにビューなら、そのままの型です。

ビューは、コピーが軽いことが前提の型なので、コンテナをそのまま渡さず、この変換を通します。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <type_traits>
#include <vector>

int main() {
  using Lvalue = std::views::all_t<std::vector<int>&>;
  std::println("左辺値は ref_view: {}", std::is_same_v<Lvalue, std::ranges::ref_view<std::vector<int>>>);
}
```

```text title="実行結果"
左辺値は ref_view: true
```

## ゲームでの使いどころ

範囲アダプターを自作するときに、入力の型の計算に使います。

## よくあるミス

??? failure "コンテナがコピーされると思う"
    コンテナは参照されるだけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`viewable_range`](viewable_range.md) | ビューにできる範囲 |
| [`range`](range.md) | 基本の範囲 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `views::all_t<R>` は `views::all` の結果の型
    - [x] 左辺値は `ref_view`、一時は `owning_view`
    - [x] 範囲アダプターの内部で使われる

## 関連ページ

- [cpprefjp: std::views::all_t](https://cpprefjp.github.io/reference/ranges/all_t.html)
- [cppreference: std::views::all_t](https://en.cppreference.com/w/cpp/ranges/all_view)

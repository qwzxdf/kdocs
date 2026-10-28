---
title: std::ranges::viewable_range
summary: "view に変換できる範囲を要求するコンセプト。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::viewable_range

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

範囲アダプターのパイプ（`range | views::filter(...)`）に渡せる範囲と、渡せない範囲があります。`std::ranges::viewable_range<R>` は、<strong>R を `views::all` でビューに変換できること</strong>を要求するコンセプトです。

!!! tip "ポイント"
    - `std::ranges::viewable_range<R>`: ビューに変換できる範囲か
    - 左辺値のコンテナ、ビュー、一時のコンテナ（C++20 の後の修正で可）が満たす
    - 範囲でない型は満たさない
    - 範囲アダプターの引数の制約として使われる

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::viewable_range {#viewable_range}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
concept viewable_range = range<T> && /* 変換できる */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる範囲の型 |

範囲のうち、`views::all` でビューにできるものが満たします。通常のコンテナの左辺値と、ビュー、一時のコンテナ（所有権を引き取る）は満たします。範囲でない型は満たしません。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::println("vector<int>& : {}", std::ranges::viewable_range<std::vector<int>&>);
  std::println("int         : {}", std::ranges::viewable_range<int>);
}
```

```text title="実行結果"
vector<int>& : true
int         : false
```

## ゲームでの使いどころ

自作の範囲アダプターの引数の制約に使います。

```cpp
template <std::ranges::viewable_range R>
auto operator()(R&& r) const;
```

## よくあるミス

??? failure "範囲でない型を渡す"
    範囲を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`all_t`](all_t.md) | 変換後の型 |
| [`range`](range.md) | 基本の範囲 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `viewable_range<R>` は R をビューにできるか
    - [x] 範囲アダプターの引数の制約
    - [x] 範囲でない型は満たさない

## 関連ページ

- [cpprefjp: std::ranges::viewable_range](https://cpprefjp.github.io/reference/ranges/viewable_range.html)
- [cppreference: std::ranges::viewable_range](https://en.cppreference.com/w/cpp/ranges/viewable_range)

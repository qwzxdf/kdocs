---
title: std::ranges::enable_view
summary: "自分の型を view として扱ってよいと宣言する変数テンプレート。"
order: 900
tags:
  - 型・言語サポート
---

# std::ranges::enable_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

範囲は、コンテナ（要素を所有する）とビュー（要素を借りて、軽くコピーできる）に分かれます。自作の型が「ビューです」と宣言するための目印が `std::ranges::enable_view` です。

!!! tip "ポイント"
    - `std::ranges::enable_view<T>` は、型 `T` がビューとして扱われるか
    - `view_base` を継承するか、特殊化で `true` にして宣言する
    - `std::string_view` や `std::span` は `true`
    - コンテナは `false`

!!! info "このページを読む前に"
    [範囲（ranges）の基礎](../../../basics/ranges.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ranges::enable_view {#enable_view}

<span class="ver ver-20">C++20</span>

```cpp
template <class T>
inline constexpr bool enable_view = /* ... */;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 調べる型 |

自作の範囲型をビューとして扱ってほしいときは、`std::ranges::view_base` を継承するか、`enable_view<MyView>` を `true` に特殊化します。

ビューは、コピーとムーブが定数時間で、要素を所有しないという約束を持つ型です。この約束を守らない型をビューと宣言すると、範囲アダプターが誤動作します。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <string_view>
#include <vector>

int main() {
  std::println("string_view  : {}", std::ranges::enable_view<std::string_view>);
  std::println("vector<int>  : {}", std::ranges::enable_view<std::vector<int>>);
}
```

```text title="実行結果"
string_view  : true
vector<int>  : false
```

## ゲームでの使いどころ

自作のビューに目印を付けます。

```cpp
struct MyView : std::ranges::view_base {
  // begin() / end() を持つ軽い型
};
```

## よくあるミス

??? failure "コンテナをビューと宣言する"
    ビューは要素を所有しない型だけです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`viewable_range`](viewable_range.md) | ビューにできる範囲 |
| [`all_t`](all_t.md) | 変換後の型 |

## コンパイラ対応

C++20 から使えます。GCC 10 以降、Clang 13 以降、Visual Studio 2019 16.10 以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `enable_view<T>` は T がビューとして扱われるか
    - [x] `view_base` を継承して宣言する
    - [x] コンテナは `false`

## 関連ページ

- [cpprefjp: std::ranges::enable_view](https://cpprefjp.github.io/reference/ranges/enable_view.html)
- [cppreference: std::ranges::enable_view](https://en.cppreference.com/w/cpp/ranges/view)

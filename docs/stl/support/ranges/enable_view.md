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

view は「コピー・ムーブが軽い範囲」です。ただし C++ はそれを型から自動で判断できません。自作の view には、`view_base` を継承するか、`enable_view<T>` を `true` に特殊化して「これは view です」と宣言します。

!!! tip "ポイント"
    - `view_base` か `view_interface` を継承していれば、自動で `true`。
    - 標準の view は最初から `true`。
    - `vector` のような持ち主のコンテナは `false`。

!!! info "このページを読む前に"
    [`std::ranges::range`](range.md) を先に読んでください。

## 関数の詳しい説明

### std::ranges::enable_view {#enable_view}

```cpp
template <class T>
inline constexpr bool enable_view = derived_from<T, view_base>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 宣言する型 |

- 戻り値: view なら `true`
- 計算量: コンパイル時のみ


## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <string_view>
#include <vector>

int main() {
  std::println("{}", std::ranges::enable_view<std::string_view>);
  std::println("{}", std::ranges::enable_view<std::vector<int>>);
}
```

```text title="実行結果"
true
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作の view を、標準のパイプで使えるようにする |

## よくあるミス

??? failure "コンテナに `true` を指定する"
    view はコピーが軽いことを前提にしています。コンテナに指定すると、不要なコピーが起きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`view_interface`](view_interface.md) | view の土台 |
| [`range`](range.md) | 範囲 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 自分の型を view として扱ってよいと宣言する変数テンプレート
    - [x] `view_base` か `view_interface` を継承していれば、自動で `true`
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ranges::enable_view](https://cpprefjp.github.io/reference/ranges/enable_view.html)
- [cppreference: std::ranges::enable_view](https://en.cppreference.com/w/cpp/ranges/view)

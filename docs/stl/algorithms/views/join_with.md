---
title: std::views::join_with
summary: "入れ子の範囲を、区切りを挟んで 1 本につなげて見る。"
order: 9
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::join_with

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <ranges>`
</div>

`std::views::join_with` は、[`join`](join.md) と同じく入れ子の範囲を 1 本につなげますが、**つなぎ目に区切り（デリミタ）を挟みます**。文字列の一覧を「,」でつなぐ、のような使い方ができます。

!!! tip "ポイント"
    - 区切りは、1 つの値（`
    - `）でも、範囲（`" - "`）でもよい。
    - 文字列にしたいなら最後に `| std::ranges::to<std::string>()`。
    - `std::string` の連結を、ビューで書ける。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::join_with {#join_with}

```cpp
nested | std::views::join_with(delimiter)
std::views::join_with(nested, delimiter)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `delimiter` | 値または範囲 | 要素の間に挟む区切り |

- 戻り値: 区切りを挟んで連結したビュー
- 計算量: 全体で O(要素数)

```cpp
#include <print>
#include <ranges>
#include <string>
#include <vector>

int main() {
  std::vector<std::string> words = {"hp", "mp", "atk"};

  auto csv = words | std::views::join_with(',') | std::ranges::to<std::string>();
  std::println("{}", csv);
}
```

```text title="実行結果"
hp,mp,atk
```

### std::ranges::join_with_view <span class="ver ver-23">C++23</span> {#join_with_view data-toc-label="std::ranges::join_with_view"}

```cpp
template <input_range V, forward_range Pattern>
class join_with_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

範囲の範囲を、区切りをはさんでつなぐ view。`views::join_with(sep)` が作ります。

ふつうは `views::join_with` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::join_with_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ステータス名をカンマ区切りの 1 行にする | `words | join_with(',')` |
| パスの要素を「/」でつなぐ | `parts | join_with('/')` |

## よくあるミス

??? failure "最後に区切りが付くと思う"
    区切りは要素と要素の**間**にだけ入ります。最後には付きません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::join`](join.md) | 区切りなしでつなぐ |
| [`std::views::split`](split.md) | 逆に、区切りで分ける |
| [`std::format`](../../utilities/format.md) | 書式つきの文字列を作る |

## コンパイラ対応

C++23 の機能です。GCC 13 / MSVC 19.34（VS 2022 17.4）以降で使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 区切りを挟んで連結する
    - [x] 区切りは要素の間だけ
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ranges::join_with_view](https://cpprefjp.github.io/reference/ranges/join_with_view.html)
- [cppreference: std::ranges::join_with_view](https://en.cppreference.com/w/cpp/ranges/join_with_view)

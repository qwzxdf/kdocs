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

`std::views::empty<T>` は、**要素が 1 つもない範囲**（空の範囲）です。型 `T` の要素を持つ範囲として扱われますが、中身はありません。ほかの範囲を返す関数が、「何も無い」を返したいときに使います。

!!! tip "ポイント"
    - `views::empty<T>` と、テンプレート引数で型を指定する（関数ではなく変数テンプレート）。
    - サイズは常に 0。
    - `std::ranges::empty` は別物（範囲が空かを調べる関数）。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::empty {#empty}

```cpp
std::views::empty<T>
```

- 戻り値: 常に空のビュー
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>

int main() {
  auto e = std::views::empty<int>;
  std::println("空？ {} / 個数 {}", std::ranges::empty(e), std::ranges::size(e));
}
```

```text title="実行結果"
空？ true / 個数 0
```

### std::ranges::empty_view <span class="ver ver-20">C++20</span> {#empty_view data-toc-label="std::ranges::empty_view"}

```cpp
template <class T>
class empty_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

要素が 0 個の view。`views::empty<T>` で作ります。

ふつうは `views::empty` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::empty_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「該当なし」を、空の範囲で返す | `return std::views::empty<Enemy>;` |

## よくあるミス

??? failure "empty と ranges::empty を混同する"
    `std::views::empty<T>` は「空の範囲」そのもの。`std::ranges::empty(r)` は「範囲 r が空か」を調べる関数です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::single`](single.md) | 要素が 1 つの範囲 |
| `std::vector<T>{}` | 空の `vector`（実体がある） |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 空の範囲
    - [x] `views::empty<T>` と書く
    - [x] `ranges::empty` とは別物

## 関連ページ

- [cpprefjp: std::ranges::empty_view](https://cpprefjp.github.io/reference/ranges/empty_view.html)
- [cppreference: std::ranges::empty_view](https://en.cppreference.com/w/cpp/ranges/empty_view)

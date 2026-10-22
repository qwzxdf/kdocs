---
title: std::views::join
summary: "入れ子の範囲（範囲の範囲）を、1 本につなげて見る。"
order: 8
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::join

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::join` は、**範囲の範囲（`vector<vector<int>>` など）を、1 本の範囲につなげて見る**ビューです。「各チームのメンバー一覧を、全員 1 本の一覧にする」ときなどに使います。

!!! tip "ポイント"
    - 内側の範囲を、外側の順に連結する。区切りを挟むなら [`join_with`](join_with.md)（C++23）。
    - 内側の要素の型が、連結した範囲の要素の型になる。
    - 内側が空の範囲でも、そのまま飛ばされる。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::join {#join}

```cpp
nested | std::views::join
std::views::join(nested)
```

- 戻り値: 連結したビュー
- 計算量: 全体で O(要素数)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::vector<std::vector<int>> teams = {{1, 2}, {3}, {4, 5}};

  auto all = teams | std::views::join | std::ranges::to<std::vector>();
  std::println("{}", all);
}
```

```text title="実行結果"
[1, 2, 3, 4, 5]
```

### std::ranges::join_view <span class="ver ver-20">C++20</span> {#join_view data-toc-label="std::ranges::join_view"}

```cpp
template <input_range V>
class join_view;
```

- 戻り値: `begin()` / `end()` をもつ view の型
- 計算量: begin / end は定数。要素の取り出しは元の範囲と同じ

範囲の範囲を、1 本につなげて見せる view。`views::join` が作ります。

ふつうは `views::join` を使って書くので、この型の名前を自分で書くことは少なく、`auto` で受けます。型名が必要なとき（関数の戻り値の型を明示したいときなど）や、CTAD（クラステンプレートの引数推論）で `std::ranges::join_view v(r, ...)` と直接作るときにだけ登場します。

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 全チームのメンバー ID を 1 本に並べる | `teams | join` |
| マップの各行（`vector<vector<Tile>>`）を 1 本にして走査する | `rows | join` |

## よくあるミス

??? failure "内側が右辺値（一時的な範囲）のまま join する"
    内側の範囲が一時オブジェクトのとき、イテレータが壊れることがあります。内側も実体を持つコンテナにしておきます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::join_with`](join_with.md) | 区切りを挟んでつなげる |
| [`std::views::chunk`](chunk.md) | 逆に、n 個ずつに分ける |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 入れ子の範囲を 1 本につなげる
    - [x] 区切りなしの連結
    - [x] `chunk` の逆

## 関連ページ

- [cpprefjp: std::ranges::join_view](https://cpprefjp.github.io/reference/ranges/join_view.html)
- [cppreference: std::ranges::join_view](https://en.cppreference.com/w/cpp/ranges/join_view)

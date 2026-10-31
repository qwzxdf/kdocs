---
title: std::views::elements
summary: "tuple（や pair）の範囲から、N 番目の要素だけを取り出して見る。"
order: 12
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::elements

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`pair` や `tuple` の範囲から、N 番目の要素だけを取り出したビューが欲しい。`std::views::elements<N>` は、各要素に `std::get<N>` を適用したビューを作ります。`std::map` の範囲から、値だけを取り出す `values` も、これの特殊な形です。

!!! tip "ポイント"
    - 各要素から N 番目のメンバーを取り出す
    - `elements<0>` はキー、`elements<1>` は値を取り出す（`keys` / `values` と同じ）
    - `pair`、`tuple`、`array` など、`get<N>` できる型に使える
    - 元の要素への参照を返すので、書き換えもできる

!!! info "このページを読む前に"
    [ビュー](../views.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::views::elements {#elements}

<span class="ver ver-20">C++20</span>

```cpp
template <std::size_t N>
inline constexpr /* 未規定 */ elements = /* 未規定 */;
// v | std::views::elements<N>
```

`std::views::keys` は `elements<0>`、`std::views::values` は `elements<1>` の別名です。

要素の型が `std::pair<std::string, int>` なら、`elements<1>` が `int` のビューになります。元の要素への参照なので、`for (int& x : v | views::elements<1>)` で、元の `pair` の `second` を書き換えられます。

`tuple` のように、3 個以上のメンバーを持つ型では、`elements<2>` のように、任意の位置を取り出せます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ranges>
#include <string>
#include <utility>
#include <vector>

int main() {
  std::vector<std::pair<std::string, int>> items = {{"potion", 3}, {"ether", 5}, {"elixir", 1}};

  const auto names = items | std::views::elements<0> | std::ranges::to<std::vector>();
  const auto counts = items | std::views::elements<1> | std::ranges::to<std::vector>();
  std::println("{}", names);
  std::println("{}", counts);

  // 元の pair の second を書き換える
  for (int& n : items | std::views::elements<1>) n *= 10;
  std::println("{}", items[0].second);
}
```

```text title="実行結果"
["potion", "ether", "elixir"]
[3, 5, 1]
30
```

## ゲームでの使いどころ

`std::map` や、`pair` の `vector` から、キーだけ、値だけを取り出して処理するときに使います。

## よくあるミス

??? failure "範囲外の N を指定する"
    コンパイル エラーです。

## 類似

| 名前 | 違い |
| --- | --- |
| `views::keys` | `elements<0>` |
| `views::values` | `elements<1>` |
| [`zip`](zip.md) | 複数の範囲を組にする |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::ranges::elements_view](https://cpprefjp.github.io/reference/ranges/elements_view.html)
- [cppreference: std::ranges::elements_view](https://en.cppreference.com/w/cpp/ranges/elements_view)

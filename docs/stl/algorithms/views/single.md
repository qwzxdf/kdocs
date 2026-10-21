---
title: std::views::single
summary: "1 つの値だけを持つ範囲を作る。"
order: 17
group: ビュー（std::views）
tags:
  - アルゴリズム
---

# std::views::single

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::views::single` は、**値を 1 つだけ持つ範囲**を作るビューです。ほかの範囲とつなげたいとき（[`join`](join.md) など）に、1 つの値を「範囲として」扱うのに使います。

!!! tip "ポイント"
    - 要素数は常に 1。
    - 値は**コピー（またはムーブ）されて保持**される。
    - 単独では使い道が少なく、ほかのビューと組み合わせて使う。

!!! info "このページを読む前に"
    [ranges とビュー](../../../basics/ranges.md)、[ラムダ式](../../../basics/lambda.md) を先に読むと分かりやすいです。

## 関数の詳しい説明

### views::single {#single}

```cpp
std::views::single(value)
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `value` | T | 範囲に入れる値 |

- 戻り値: 要素が 1 つだけのビュー
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  auto one = std::views::single(42) | std::ranges::to<std::vector>();
  std::println("{}", one);
  std::println("{}", std::ranges::size(std::views::single(42)));
}
```

```text title="実行結果"
[42]
1
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「先頭に 1 つ足した範囲」を join で作る | `views::join` の中で `single` を並べる |

## よくあるミス

??? failure "範囲として使えず、値のままだと思う"
    `single(42)` は、`42` ではなく「要素が 42 だけの範囲」です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::views::empty`](empty.md) | 要素が 0 個の範囲 |
| [`std::views::repeat`](repeat.md) | 同じ値を繰り返す |
| [`std::optional`](../../utilities/optional.md) | 0 個か 1 個の値 |

## コンパイラ対応

C++20 の機能です。主要なコンパイラすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 要素 1 つの範囲
    - [x] ほかのビューと組み合わせる
    - [x] `optional` に似た範囲

## 関連ページ

- [cpprefjp: std::ranges::single_view](https://cpprefjp.github.io/reference/ranges/single_view.html)
- [cppreference: std::ranges::single_view](https://en.cppreference.com/w/cpp/ranges/single_view)

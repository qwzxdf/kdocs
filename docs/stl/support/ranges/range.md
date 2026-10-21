---
title: std::ranges::range
summary: "「範囲」であること（begin と end がある）を要求するコンセプト。"
order: 1
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::range

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::range<T>` は、**T が範囲である（`begin()` と `end()` が使える）こと**を要求するコンセプトです。`vector`、配列、ビューなど、`for` で回せるものは範囲です。ranges のアルゴリズムの引数は、このコンセプトで制約されています。

!!! tip "ポイント"
    - `std::ranges::range<std::vector<int>>` は `true`、`int` は `false`。
    - 細かい種類に `input_range`、`forward_range`、`random_access_range`、`contiguous_range` がある。
    - 自作のアルゴリズムに「範囲を受け取る」制約を付けるときに使う。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::ranges::range {#range}

```cpp
template <class T>
concept range = requires(T& t) { ranges::begin(t); ranges::end(t); };
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | テンプレート引数 | 調べる型 |

- 戻り値: 範囲なら `true`
- 計算量: コンパイル時

```cpp
#include <print>
#include <ranges>
#include <vector>

int main() {
  std::println("{} {}", std::ranges::range<std::vector<int>>, std::ranges::range<int>);
}
```

```text title="実行結果"
true false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 「範囲を受け取る」自作関数 | `template <std::ranges::range R> void Draw(R&& items)` |

## よくあるミス

??? failure "テンプレートで begin / end を手書きする"
    ranges のコンセプトを使えば、制約が簡潔になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ranges::subrange`](../../algorithms/views/subrange.md) | イテレータから範囲を作る |
| [`ranges::begin`](begin.md) | 先頭を取る |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲であること
    - [x] `for` で回せるもの
    - [x] 種類別のコンセプトもある

## 関連ページ

- [cpprefjp: std::ranges::range](https://cpprefjp.github.io/reference/ranges/range.html)
- [cppreference: std::ranges::range](https://en.cppreference.com/w/cpp/ranges/range)

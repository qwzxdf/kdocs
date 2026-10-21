---
title: std::ranges::begin
summary: "範囲の先頭のイテレータを取る（配列・コンテナ・独自の範囲に対応）。"
order: 2
group: ranges の基本部品
tags:
  - 型・言語サポート
---

# std::ranges::begin

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <ranges>`
</div>

`std::ranges::begin(r)` は、**範囲の先頭のイテレータを取る**関数オブジェクトです。コンテナの `begin()` メンバ関数、配列、`begin(r)` の自由関数のどれにも対応します。`ranges::end`、`ranges::size`、`ranges::empty` も同じ仲間です。

!!! tip "ポイント"
    - `std::begin` より厳密で、間違った使い方はコンパイルエラーになる。
    - 右辺値の範囲（一時オブジェクト）には使えない（ぶら下がり防止）。
    - 自作の範囲にも対応しやすい。

!!! info "このページを読む前に"
    [テンプレートとコンセプト](../../../basics/template.md) の基本が前提です。

## 関数の詳しい説明

### std::ranges::begin {#begin}

```cpp
inline constexpr /*unspecified*/ ranges::begin;
inline constexpr /*unspecified*/ ranges::end;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `r` | 範囲 | 先頭・終端を取りたい範囲 |

- 戻り値: 先頭（終端）のイテレータ
- 計算量: O(1)

```cpp
#include <print>
#include <ranges>

int main() {
  int a[] = {10, 20, 30};
  std::println("{} {}", *std::ranges::begin(a), std::ranges::end(a) - std::ranges::begin(a));
}
```

```text title="実行結果"
10 3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 自作の ranges 風アルゴリズムで先頭を取る | `auto first = std::ranges::begin(r);` |

## よくあるミス

??? failure "一時的な範囲に使う"
    `std::ranges::begin(GetVector())` はコンパイルエラーです（ぶら下がりを防ぐため）。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::begin`](../iterator/begin.md) | 従来の関数 |
| [`ranges::size`](size.md) | 要素数 |

## コンパイラ対応

C++20 の機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ranges 版の begin / end
    - [x] 右辺値には使えない
    - [x] 配列にも対応

## 関連ページ

- [cpprefjp: std::ranges::begin](https://cpprefjp.github.io/reference/ranges/begin.html)
- [cppreference: std::ranges::begin](https://en.cppreference.com/w/cpp/ranges/begin)

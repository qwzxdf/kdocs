---
title: std::range_format
summary: "範囲の書式化の種類を表す列挙型。"
order: 900
tags:
  - ユーティリティ
---

# std::range_format

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

`std::range_format` は、範囲の書式化の種類を表す列挙型です。`std::format_kind<R>` の値の型で、`disabled`、`map`、`set`、`sequence`、`string`、`debug_string` の 6 つがあります。

!!! tip "ポイント"
    - `disabled`: 書式化の対象外
    - `map`: キーと値の組の範囲。`{k: v, ...}`
    - `set`: 集合。`{a, b, ...}`
    - `sequence`: 並び。`[a, b, ...]`

!!! info "このページを読む前に"
    [`std::format_kind`](format_kind.md) を先に読んでください。

## 関数の詳しい説明

### std::range_format {#range_format}

<span class="ver ver-23">C++23</span>

```cpp
enum class range_format {
  disabled,
  map,
  set,
  sequence,
  string,
  debug_string
};
```

| 値 | 意味 | 表示の形 |
| --- | --- | --- |
| `disabled` | 書式化しない | （使えない） |
| `map` | キーと値の範囲 | `{1: 10, 2: 20}` |
| `set` | 集合 | `{1, 2, 3}` |
| `sequence` | 並び | `[1, 2, 3]` |
| `string` | 文字の範囲を文字列として | `abc` |
| `debug_string` | 文字の範囲を、引用符つきの文字列として | `"abc"` |

`string` と `debug_string` は、文字の範囲を文字列として表示するときのためのものです。`std::string` は、専用の `formatter` があるので、この値は使いません。自作の文字のコンテナを、文字列として表示するときに指定します。

`format_kind<R>` が `disabled` だと、`std::formatter<R>` が使えないので、`std::format("{}", r)` はコンパイル エラーです。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <vector>

int main() {
  std::println("sequence: {}", std::format_kind<std::vector<int>> == std::range_format::sequence);
  std::println("disabled ではない: {}", std::format_kind<std::vector<int>> != std::range_format::disabled);

  // 列挙子の比較で、範囲の種類で処理を分けられる
  constexpr auto kind = std::format_kind<std::vector<int>>;
  if constexpr (kind == std::range_format::sequence) {
    std::println("並びとして書式化される");
  }
}
```

```text title="実行結果"
sequence: true
disabled ではない: true
並びとして書式化される
```

## ゲームでの使いどころ

自作のコンテナの `format_kind` を、特殊化するときに値を指定します。

## よくあるミス

??? failure "disabled のままの範囲を表示しようとする"
    コンパイル エラーになります。`format_kind` を特殊化します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_kind`](format_kind.md) | この型の値を持つ変数 |
| [`range_formatter`](range_formatter.md) | 範囲の書式化の部品 |
| [`formattable`](formattable.md) | 書式化できるかのコンセプト |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::range_format](https://cpprefjp.github.io/reference/format/range_format.html)
- [cppreference: std::range_format](https://en.cppreference.com/w/cpp/utility/format/range_format)

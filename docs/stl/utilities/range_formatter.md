---
title: std::range_formatter
summary: "範囲（vector など）を書式化する formatter の部品。"
order: 900
tags:
  - ユーティリティ
---

# std::range_formatter

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

自作のコンテナ `Bag<T>` を `std::println("{}", bag)` で表示したい。要素を 1 つずつ書式化して、区切りや括弧を付ける処理を、一から書くのは大変です。`std::range_formatter<T>` は、範囲を `[1, 2, 3]` の形に書式化する処理をまとめた部品で、自作の `formatter` の中で、委譲先として使います。

!!! tip "ポイント"
    - 自作の `formatter` の中に、メンバーとして持ち、`parse` と `format` を委譲する
    - 区切りは `set_separator`、括弧は `set_brackets` で変えられる
    - 要素の書式の指定（`{:02}` など）も、そのまま使える
    - 標準の範囲の `formatter` は、内部でこれを使っている

!!! info "このページを読む前に"
    [`std::formatter`](formatter.md) と [`std::format_kind`](format_kind.md) を先に読んでください。

## 関数の詳しい説明

### std::range_formatter {#range_formatter}

<span class="ver ver-23">C++23</span>

```cpp
template <class T, class CharT = char>
class range_formatter {
 public:
  constexpr void set_separator(std::basic_string_view<CharT> sep) noexcept;
  constexpr void set_brackets(std::basic_string_view<CharT> opening,
                              std::basic_string_view<CharT> closing) noexcept;
  constexpr auto& underlying() noexcept;
  template <class ParseContext> constexpr auto parse(ParseContext& ctx);
  template <class R, class FormatContext> auto format(R&& r, FormatContext& ctx) const;
};
```

`parse` が、書式の指定を解析し、`format` が、範囲の各要素を書式化して出力します。`underlying()` は、要素の書式化を担当する `formatter<T>` を返します。

既定の区切りは `", "`、括弧は `[` と `]` です。`set_separator(" | ")` と `set_brackets("<", ">")` で変えられます。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <vector>

// 自作のコンテナ
template <class T>
struct Bag {
  std::vector<T> items;
};

// range_formatter に委譲する
template <class T>
struct std::formatter<Bag<T>> {
  std::range_formatter<T> inner;

  constexpr auto parse(std::format_parse_context& ctx) { return inner.parse(ctx); }

  auto format(const Bag<T>& b, std::format_context& ctx) const {
    return inner.format(b.items, ctx);
  }
};

int main() {
  const Bag<int> bag{{1, 2, 3}};
  std::println("{}", bag);

  // 要素の書式指定も使える
  std::println("{::03}", bag);
}
```

```text title="実行結果"
[1, 2, 3]
[001, 002, 003]
```

`{::03}` の 2 つ目のコロン以降が、要素に適用される書式です。

## ゲームでの使いどころ

自作のコンテナ（リングバッファ、固定長配列など）を、デバッグ表示できるようにするときに使います。

## よくあるミス

??? failure "parse で inner の戻り値を返さない"
    `parse` は、書式の解析が終わった位置を返す決まりです。`inner.parse(ctx)` の戻り値を、そのまま返します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`formatter`](formatter.md) | 書式化の実装の基本 |
| [`format_kind`](format_kind.md) | 範囲の種類を決める |
| [`range_format`](range_format.md) | 種類を表す列挙型 |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::range_formatter](https://cpprefjp.github.io/reference/format/range_formatter.html)
- [cppreference: std::range_formatter](https://en.cppreference.com/w/cpp/utility/format/range_formatter)

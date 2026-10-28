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

自作のコンテナを `std::format("{}", c)` で `[1, 2, 3]` のように出力できるようにしたいとき、`formatter<自作コンテナ>` の中で `range_formatter` を使うと、区切りや括弧の指定（`{:n}` など）を含めて処理できます。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::range_formatter {#range_formatter}

```cpp
template <class T, class CharT = char>
struct range_formatter {
  constexpr void set_separator(basic_string_view<CharT> sep);
  constexpr void set_brackets(basic_string_view<CharT> opening, basic_string_view<CharT> closing);
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `T` | 型 | 要素の型 |

- 戻り値: 範囲を書式化する formatter
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  // 例: 自作のコンテナ用の formatter の中で使う
  // std::range_formatter<int> f;
  // f.set_separator(", ");
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 自作のコンテナを `format` に対応させる |

## よくあるミス

??? failure "`vector` に対して自作する"
    標準のコンテナには、最初から formatter があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`formatter`](formatter.md) | formatter の基本 |
| [`format_kind`](format_kind.md) | 範囲の種類 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 範囲（vector など）を書式化する formatter の部品
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::range_formatter](https://cpprefjp.github.io/reference/format/range_formatter.html)
- [cppreference: std::range_formatter](https://en.cppreference.com/w/cpp/utility/format/range_formatter)

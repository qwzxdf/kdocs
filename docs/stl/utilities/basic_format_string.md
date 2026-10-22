---
title: std::basic_format_string
summary: "書式文字列を、コンパイル時に検査して保持する型。"
order: 900
tags:
  - ユーティリティ
---

# std::basic_format_string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::format("{}", x)` の書式文字列は、コンパイル時に検査されます。その検査を担当するのが、`basic_format_string` です。書式文字列の誤り（引数の数が合わない）が、コンパイルエラーになります。

!!! tip "ポイント"
    - `<format>` の部品。
    - ふつうは `std::format` / `std::println` を使えば足りる。
    - 自作の型に対応させるときに登場する。

!!! info "このページを読む前に"
    [`std::format`](format.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_format_string {#basic_format_string}

```cpp
template <class CharT, class... Args>
struct basic_format_string {
  template <class T> consteval basic_format_string(const T& s);
  constexpr basic_string_view<CharT> get() const noexcept;
};
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | 文字列リテラル | 書式文字列（コンパイル時に検査される） |

- 戻り値: 書式文字列の `string_view`（`get()`）
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  std::basic_format_string<char, int> fs("{}");
  std::println("{}", std::format(fs, 3));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 書式文字列を引数に受ける自作のログ関数 |

## よくあるミス

??? failure "実行時の文字列を渡す"
    コンパイル時の定数でないと渡せません。実行時なら `std::runtime_format`（C++26）か `vformat` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_string`](format_string.md) | char 版の別名 |
| [`wformat_string`](wformat_string.md) | wchar_t 版 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式文字列を、コンパイル時に検査して保持する型
    - [x] `<format>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::basic_format_string](https://cpprefjp.github.io/reference/format/basic_format_string.html)
- [cppreference: std::basic_format_string](https://en.cppreference.com/w/cpp/utility/format/basic_format_string)

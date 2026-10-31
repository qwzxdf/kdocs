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

`std::format_string` と `std::wformat_string` の元になるクラス テンプレートが `std::basic_format_string<CharT, Args...>` です。書式文字列を保持し、コンストラクターでコンパイル時に検査します。普段は別名の `format_string` を使い、このテンプレートを直接書くことはありません。

!!! tip "ポイント"
    - `format_string` と `wformat_string` の元のテンプレート
    - コンストラクターは `consteval`。書式の誤りがコンパイル エラーになる
    - `get()` で元の書式を `basic_string_view` として取り出す
    - 実行時の書式は、`std::runtime_format`（C++26）か `vformat`

!!! info "このページを読む前に"
    [`std::format_string`](format_string.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_format_string {#basic_format_string}

<span class="ver ver-20">C++20</span>

```cpp
template <class CharT, class... Args>
struct basic_format_string {
  template <class T> consteval basic_format_string(const T& s);
  constexpr std::basic_string_view<CharT> get() const noexcept;
};
```

`s` は、`basic_string_view<CharT>` に変換できる型です。文字列リテラルがその典型です。`consteval` なので、`s` が定数式でないと、コンパイル エラーになります。

コンストラクターの中で、書式を `formatter<Args>` で解析して、各 `{}` の指定が、対応する引数の型で有効かを確かめます。ここで失敗すると、`std::format_error` を投げようとして、定数式でなくなり、コンパイル エラーになります。

`Args...` は、実際の型ではなく、検査のための型の並びです。`basic_format_string<char, int, std::string>` は、`int` と `std::string` の 2 つの引数を取る書式を検査できます。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <type_traits>

int main() {
  // format_string は basic_format_string<char, ...> の別名
  static_assert(std::is_same_v<std::format_string<int>,
                               std::basic_format_string<char, int>>);
  static_assert(std::is_same_v<std::wformat_string<int>,
                               std::basic_format_string<wchar_t, int>>);

  constexpr std::basic_format_string<char, int, int> f{"{} + {}"};
  std::println("{}", f.get());
  std::println("{}", std::format(f, 1, 2));
}
```

```text title="実行結果"
{} + {}
1 + 2
```

## ゲームでの使いどころ

直接書くことはありません。`format_string` の仕組みを知るための土台です。

## よくあるミス

??? failure "実行時の文字列を渡す"
    `consteval` なので、定数式でないとコンパイルできません。実行時の書式は `vformat` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`format_string`](format_string.md) | `char` 版の別名 |
| [`wformat_string`](wformat_string.md) | `wchar_t` 版の別名 |
| [`std::vformat`](vformat.md) | 実行時の書式 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::basic_format_string](https://cpprefjp.github.io/reference/format/basic_format_string.html)
- [cppreference: std::basic_format_string](https://en.cppreference.com/w/cpp/utility/format/basic_format_string)

---
title: std::basic_string_view
summary: "string_view / wstring_view などの元になる、文字の型を選べるテンプレート。"
order: 900
tags:
  - ユーティリティ
---

# std::basic_string_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <string_view>`
</div>

`std::string_view` は文字列の先頭のポインタと長さだけを持つ軽い「のぞき窓」です。実体は文字の型をテンプレート引数にした `std::basic_string_view<CharT>` で、`string_view` は `basic_string_view<char>` の別名です。`wchar_t` 用の `wstring_view`、UTF-8 / 16 / 32 用の `u8string_view`、`u16string_view`、`u32string_view` も同じテンプレートの別名です。

普段は別名を使うので `basic_string_view` と書く場面は、文字の型に依存しないテンプレートを書くときくらいです。

!!! tip "ポイント"
    - `string_view` は `basic_string_view<char>` の別名。他の文字の型にも別名がある
    - 文字列を所有しない。元の文字列より長く生きるとぶら下がる
    - コピーはポインタと長さのコピーだけで軽い
    - 関数の引数に使うと `std::string`、文字列リテラル、`char*` をまとめて受けられる

!!! info "このページを読む前に"
    [`std::string_view`](string_view.md) を先に読んでください。使い方はそちらにあります。

## 関数の詳しい説明

### std::basic_string_view {#basic_string_view}

<span class="ver ver-17">C++17</span>

```cpp
template <class CharT, class Traits = std::char_traits<CharT>>
class basic_string_view;
```

| 別名 | 元の型 | 文字の型 |
| --- | --- | --- |
| `std::string_view` | `basic_string_view<char>` | `char` |
| `std::wstring_view` | `basic_string_view<wchar_t>` | `wchar_t` |
| `std::u8string_view` | `basic_string_view<char8_t>` | `char8_t`（UTF-8） |
| `std::u16string_view` | `basic_string_view<char16_t>` | `char16_t`（UTF-16） |
| `std::u32string_view` | `basic_string_view<char32_t>` | `char32_t`（UTF-32） |

どの別名も機能は同じです。`size()`、`substr()`、`find()`、`remove_prefix()`、`starts_with()` などが使えます。違うのは 1 要素の大きさと解釈だけです。

`size()` は文字の数ではなく要素（`CharT`）の数です。UTF-8 の `string_view` で日本語の「あ」を数えると、3 要素です。UTF-32 の `u32string_view` なら 1 要素です。

リテラルの接尾辞は `sv` で `"abc"sv`、`L"abc"sv`、`u"abc"sv`、`U"abc"sv`、`u8"abc"sv` と書けます。`using namespace std::string_view_literals;` が要ります。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <string_view>
#include <type_traits>

int main() {
  using namespace std::string_view_literals;

  static_assert(std::is_same_v<std::string_view, std::basic_string_view<char>>);
  static_assert(std::is_same_v<std::wstring_view, std::basic_string_view<wchar_t>>);
  static_assert(std::is_same_v<std::u16string_view, std::basic_string_view<char16_t>>);

  // 文字列リテラルや std::string を、そのまま見る
  std::string s = "Hero";
  std::string_view a = s;
  std::string_view b = "Mage"sv;
  std::println("{} {} {}", a, b.size(), a.substr(1, 2));

  // size() は文字数ではなく要素数
  std::println("UTF-8 の「あ」: {} 要素", std::string_view("あ").size());
  std::println("UTF-32 の「あ」: {} 要素", std::u32string_view(U"あ").size());
}
```

```text title="実行結果"
Hero 4 er
UTF-8 の「あ」: 3 要素
UTF-32 の「あ」: 1 要素
```

## ゲームでの使いどころ

関数の引数を `const std::string&` ではなく `std::string_view` にすると、文字列リテラルを渡すときに一時的な `std::string` が作られません。

## よくあるミス

??? failure "元の文字列より長く生かす"
    `string_view` は所有しないので、元の文字列が消えるとぶら下がります。関数の戻り値には `std::string` を返します。

??? failure "終端の \0 があると思う"
    `string_view` は終端文字を保証しません。C の API に渡すときは `std::string` に変換して `c_str()` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::string_view`](string_view.md) | `char` 版。普段はこちら |
| [`std::basic_string`](../containers/string.md) | 所有する文字列 |
| `std::span` | 文字列以外の連続領域を見る |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::basic_string_view](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)
- [cppreference: std::basic_string_view](https://en.cppreference.com/w/cpp/string/basic_string_view)

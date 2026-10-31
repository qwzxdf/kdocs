---
title: std::runtime_format
summary: "実行時の文字列を、書式文字列として `format` に渡す。"
order: 900
tags:
  - ユーティリティ
---

# std::runtime_format

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-26">C++26</span>
`#include <format>`
</div>

`std::format` や `std::println` の書式文字列は、コンパイル時に検査されるので、実行時に決まる書式（設定ファイルから読んだもの）は、そのままでは渡せません。C++26 の `std::runtime_format(s)` は、実行時の文字列に、「検査を省略します」という印を付けて、`format` の第 1 引数に渡せるようにする関数です。C++23 までは、`std::vformat` を使います。

!!! tip "ポイント"
    - `std::format(std::runtime_format(s), 引数...)` で、実行時の書式が使える
    - 書式の誤りは、実行時に `std::format_error` になる
    - C++26 の機能。C++23 までは `std::vformat`
    - 手元の MSVC（Visual Studio 2026）では、まだ使えない

!!! info "このページを読む前に"
    [`std::format_string`](format_string.md) と [`std::vformat`](vformat.md) を先に読んでください。

## 関数の詳しい説明

### std::runtime_format {#runtime_format}

<span class="ver ver-26">C++26</span>

```cpp
/* 実装定義 */ runtime_format(std::string_view fmt) noexcept;
/* 実装定義 */ runtime_format(std::wstring_view fmt) noexcept;
```

戻り値は、`std::format_string` に暗黙に変換できる、実装定義の型です。コンパイル時の検査をせず、`fmt` を書式としてそのまま保持します。

```cpp
std::string fmt = LoadFormat();                          // 実行時に決まる
std::string s = std::format(std::runtime_format(fmt), hp, mp);
```

書式が引数と合わなければ、`std::vformat` と同じく、`std::format_error` を投げます。

`std::vformat(fmt, std::make_format_args(hp, mp))` と同じ結果が、より短い書き方で得られます。`println` にも使えます。

```cpp
std::println(std::runtime_format(fmt), hp);
```

## 実際に動かしてみる

C++26 の `runtime_format` は、手元の MSVC では使えないので、同じ働きの `vformat` で動かします。

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  // 実行時に決まる書式
  const std::string fmt = "HP {} / MP {}";
  int hp = 30;
  int mp = 12;

  // C++26: std::format(std::runtime_format(fmt), hp, mp)
  // C++23 まで: vformat
  std::println("{}", std::vformat(fmt, std::make_format_args(hp, mp)));
}
```

```text title="実行結果"
HP 30 / MP 12
```

## ゲームでの使いどころ

翻訳された書式を、辞書から取り出して整形するときに使います。

## よくあるミス

??? failure "C++23 でそのまま書く"
    `std::runtime_format` は C++26 です。`vformat` に置き換えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vformat`](vformat.md) | C++23 までの、実行時の書式 |
| [`format_string`](format_string.md) | コンパイル時に検査される書式 |
| [`std::format`](format.md) | 渡す先 |

## コンパイラ対応

C++26 の機能です。手元の MSVC では未対応のため、`vformat` で確かめました。GCC 15 以降、Clang の新しい版で使えます。

## 関連ページ

- [cpprefjp: std::runtime_format](https://cpprefjp.github.io/reference/format/runtime_format.html)
- [cppreference: std::runtime_format](https://en.cppreference.com/w/cpp/utility/format/runtime_format)

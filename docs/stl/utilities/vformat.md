---
title: std::vformat
summary: "書式の文字列を、実行時に決める。"
order: 51
tags:
  - ユーティリティ
---

# std::vformat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <format>`
</div>

`std::format` の書式文字列は、コンパイル時に検査されるので、実行時に決まる書式（設定ファイルから読んだ書式、翻訳された文字列）は渡せません。`std::vformat` は、書式の検査をコンパイル時には行わず、実行時に整形する関数です。引数は `std::make_format_args` で包んで渡します。

!!! tip "ポイント"
    - `std::vformat(fmt, std::make_format_args(a, b))` の形で呼ぶ
    - 書式の誤りは、実行時に `std::format_error` になる
    - `make_format_args` の引数は、左辺値の変数
    - ローカライズされた書式など、実行時に決まる書式に使う

!!! info "このページを読む前に"
    [`std::format`](format.md) と [`std::make_format_args`](make_format_args.md) を先に読んでください。

## 関数の詳しい説明

### std::vformat {#vformat}

<span class="ver ver-20">C++20</span>

```cpp
std::string vformat(std::string_view fmt, std::format_args args);
std::wstring vformat(std::wstring_view fmt, std::wformat_args args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `fmt` | `std::string_view` | 書式文字列。実行時に決まっていてよい |
| `args` | `std::format_args` | `make_format_args` が作った引数 |

書式の中の `{}` の個数と、引数の個数が合わない、型に合わない指定がある、といった誤りは、`std::format_error` として投げられます。

`std::make_format_args` が返すのは、引数への参照を持つオブジェクトです。左辺値を渡す必要があります。一時オブジェクトを渡すと、C++23 以降はコンパイル エラーです。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>
#include <string>

int main() {
  // 実行時に決まる書式（たとえば翻訳された文字列）
  const std::string fmt = "HP {} / MP {}";
  int hp = 30;
  int mp = 12;
  std::println("{}", std::vformat(fmt, std::make_format_args(hp, mp)));

  // 書式の誤りは、実行時に例外
  const std::string bad = "{} {}";
  try {
    std::vformat(bad, std::make_format_args(hp));
  } catch (const std::format_error&) {
    std::println("引数が足りない: format_error");
  }
}
```

```text title="実行結果"
HP 30 / MP 12
引数が足りない: format_error
```

## ゲームでの使いどころ

言語ごとに翻訳された書式（`"HP {} / MP {}"` を日本語に訳したもの）を、辞書から取り出して整形するときに使います。

## よくあるミス

??? failure "make_format_args に一時オブジェクトを渡す"
    参照を保持するので、一時オブジェクトでは、ぶら下がります。変数に入れてから渡します。

??? failure "書式の誤りを検査しない"
    実行時の例外になります。外から来る書式は、`try` で囲みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::format`](format.md) | 書式をコンパイル時に検査する |
| [`vformat_to`](vformat_to.md) | 出力先を指定する |
| [`make_format_args`](make_format_args.md) | 引数を包む |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::vformat](https://cpprefjp.github.io/reference/format/vformat.html)
- [cppreference: std::vformat](https://en.cppreference.com/w/cpp/utility/format/vformat)

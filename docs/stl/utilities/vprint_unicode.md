---
title: std::vprint_unicode
summary: "実行時の書式文字列で、Unicode 対応の出力をする。"
order: 900
tags:
  - ユーティリティ
---

# std::vprint_unicode

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

`std::println` は、内部で `std::vprint_unicode` を呼んでいます。書式を実行時に決めて、標準出力や `FILE*` に、Unicode 対応で出したいときは、これを直接使います。Windows のコンソールでは、UTF-8 を正しく表示できるように、文字コードを考慮して出力します。

!!! tip "ポイント"
    - 書式は `std::string_view`、引数は `make_format_args` で包む
    - 出力先は `FILE*`（標準出力なら `stdout`）。C++23 では、出力先の省略はできない
    - 端末が Unicode に対応していれば、UTF-8 のまま出す。そうでなければ変換する
    - 普段は `std::print` / `std::println`

!!! info "このページを読む前に"
    [`std::vformat`](vformat.md) と [`std::println`](println.md) を先に読んでください。

## 関数の詳しい説明

### std::vprint_unicode {#vprint_unicode}

<span class="ver ver-23">C++23</span>

```cpp
void vprint_unicode(std::FILE* stream, std::string_view fmt, std::format_args args);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `std::FILE*` | 出力先。標準出力なら `stdout` |
| `fmt` | `std::string_view` | 書式（実行時に決まっていてよい） |
| `args` | `std::format_args` | `make_format_args` の結果 |

出力先が端末（Windows のコンソールなど）なら、UTF-8 の文字列を、端末の Unicode の出力 API（Windows では `WriteConsoleW`）に書きます。そうでない（ファイルへのリダイレクトなど）なら、UTF-8 のバイト列をそのまま書きます。

`std::vprint_nonunicode` は、この変換をしない版です。ローカルのコード ページのまま書きます。

改行は自動で付きません。`std::println` の実体は、書式に `\n` を足して、これを呼んでいる形です。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  int hp = 30;
  std::vprint_unicode(stdout, "HP = {}\n", std::make_format_args(hp));
}
```

```text title="実行結果"
HP = 30
```

## ゲームでの使いどころ

自作のログ関数が、実行時の書式を受け取って、標準出力に出すときに使います。`std::print` / `println` を包む関数は、書式を `std::format_string` で受けるほうが、コンパイル時に検査されます。

## よくあるミス

??? failure "改行を足し忘れる"
    `println` と違い、`\n` を書式に含めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vprint_nonunicode`](vprint_nonunicode.md) | Unicode の変換をしない |
| [`std::print`](print.md) | コンパイル時に書式を検査する |
| [`vformat`](vformat.md) | 出力せず、文字列を作る |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::vprint_unicode](https://cpprefjp.github.io/reference/format/vprint_unicode.html)
- [cppreference: std::vprint_unicode](https://en.cppreference.com/w/cpp/utility/format/vprint_unicode)

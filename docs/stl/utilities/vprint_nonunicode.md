---
title: std::vprint_nonunicode
summary: "実行時の書式文字列で、Unicode 変換なしで出力する。"
order: 900
tags:
  - ユーティリティ
---

# std::vprint_nonunicode

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <format>`
</div>

`std::vprint_nonunicode` は、`std::vprint_unicode` の、Unicode の変換をしない版です。書式を整形した結果を、そのままのバイト列で、`FILE*`（標準出力なら `stdout`）に書きます。端末の文字コードが何であれ、UTF-8 から変換せず、バイトの並びを出力します。

!!! tip "ポイント"
    - 変換をしない。整形した結果のバイト列を、そのまま書く
    - Windows のコンソールでは、コード ページが UTF-8 でないと、日本語が文字化けする
    - 普段は `vprint_unicode`、または `std::print`
    - ファイルへの書き込みでは、`vprint_unicode` と同じ結果

!!! info "このページを読む前に"
    [`std::vprint_unicode`](vprint_unicode.md) を先に読んでください。

## 関数の詳しい説明

### std::vprint_nonunicode {#vprint_nonunicode}

<span class="ver ver-23">C++23</span>

```cpp
void vprint_nonunicode(std::string_view fmt, std::format_args args);
void vprint_nonunicode(std::FILE* stream, std::string_view fmt, std::format_args args);
```

端末への出力でも、特別な API を使わず、通常の書き込み（`fwrite` 相当）を行います。バイト列がそのまま端末に届くので、端末が UTF-8 を解釈できなければ、表示が崩れます。

`std::print` は、実行環境が Unicode 対応（MSVC で `/utf-8` を指定したときなど）のとき、`vprint_unicode` を、そうでないとき `vprint_nonunicode` を呼びます。どちらを使うかは、コンパイラが決めます。

自分で `vprint_nonunicode` を選ぶのは、端末を介さない出力（バイナリに近い出力、既に端末の文字コードで書式を用意している）のときです。

## 実際に動かしてみる

```cpp
#include <format>
#include <print>

int main() {
  int hp = 30;
  // ASCII だけなら、どちらを使っても同じ
  std::vprint_nonunicode(stdout, "HP = {}\n", std::make_format_args(hp));
}
```

```text title="実行結果"
HP = 30
```

## ゲームでの使いどころ

ほとんどありません。`println` を使います。

## よくあるミス

??? failure "日本語をコンソールに出して文字化けする"
    コンソールのコード ページが UTF-8 でないと、崩れます。`vprint_unicode` か `println` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`vprint_unicode`](vprint_unicode.md) | 端末では Unicode の出力をする |
| [`std::print`](print.md) | コンパイラが適切な方を選ぶ |
| [`std::println`](println.md) | 改行つき |

## コンパイラ対応

C++23 から使えます。

## 関連ページ

- [cpprefjp: std::vprint_nonunicode](https://cpprefjp.github.io/reference/format/vprint_nonunicode.html)
- [cppreference: std::vprint_nonunicode](https://en.cppreference.com/w/cpp/utility/format/vprint_nonunicode)

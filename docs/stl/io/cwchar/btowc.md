---
title: std::btowc
summary: "1 バイトの文字を、ワイド文字に変換する。"
order: 900
tags:
  - 入出力・文字列
---

# std::btowc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`char` の 1 文字を、`wchar_t` に直したい。ASCII の英数字なら、値がそのまま対応するので簡単ですが、日本語のように 1 文字が複数バイトの文字は、1 バイトだけでは変換できません。`btowc` は「1 バイトで完結する文字」だけを、現在のロケールに従ってワイド文字に変換します。

!!! tip "ポイント"
    - 引数は `int`。`unsigned char` の値か `EOF`
    - 変換できないとき（複数バイト文字の一部など）は `WEOF` を返す
    - `EOF` を渡すと `WEOF` を返す
    - 1 バイトで完結しない文字には使えない。`mbrtowc` を使う

!!! info "このページを読む前に"
    [`std::wint_t`](wint_t.md) と [`WEOF`](weof.md) を先に読んでください。

## 関数の詳しい説明

### std::btowc {#btowc}

```cpp
std::wint_t btowc(int c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `int` | 変換する 1 バイト。`unsigned char` の範囲の値か `EOF` |

`c` を現在のロケールのマルチバイト文字の 1 文字として解釈し、対応するワイド文字を返します。ASCII の範囲（0〜127）は、ほとんどのロケールで同じ値のワイド文字になります。

日本語のロケール（Shift_JIS など）で、全角文字の 1 バイト目だけを渡すと、1 バイトでは文字が完成しないので、`WEOF` が返ります。UTF-8 のロケールでも、128 以上のバイトは、1 バイトの文字ではないので `WEOF` です。

`c` に `char` をそのまま渡すと、`char` が符号つきの環境で、128 以上のバイトが負の値になります。`unsigned char` にキャストして渡します。

戻り値は `wint_t` です。`wchar_t` で受けずに、`WEOF` と比べてから使います。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::println("'A' → L'A': {}", std::btowc('A') == L'A');
  std::println("'7' → L'7': {}", std::btowc('7') == L'7');
  std::println("EOF → WEOF: {}", std::btowc(EOF) == WEOF);
}
```

```text title="実行結果"
'A' → L'A': true
'7' → L'7': true
EOF → WEOF: true
```

## ゲームでの使いどころ

ほとんどありません。ASCII の文字を `wchar_t` に直すだけなら、`static_cast<wchar_t>(c)` で済みます。複数バイトの文字を含む文字列の変換は、`mbsrtowcs` や、Windows の `MultiByteToWideChar` を使います。

## よくあるミス

??? failure "char を符号つきのまま渡す"
    128 以上のバイトが負の値になり、`EOF`（-1）と区別できなくなることがあります。`static_cast<unsigned char>(c)` を渡します。

??? failure "日本語の 1 バイトずつを変換しようとする"
    UTF-8 の日本語は 3 バイトで 1 文字です。1 バイトずつ `btowc` に渡すと、すべて `WEOF` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wctob`](wctob.md) | 逆方向の変換 |
| [`mbrtowc`](mbrtowc.md) | 複数バイトの文字も変換できる |
| [`mbsrtowcs`](mbsrtowcs.md) | 文字列をまとめて変換する |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `btowc` は、1 バイトで完結する文字を、ワイド文字に変換する
    - [x] 変換できなければ `WEOF`。戻り値は `wint_t` で受ける
    - [x] 複数バイトの文字は `mbrtowc`

## 関連ページ

- [cpprefjp: btowc](https://cpprefjp.github.io/reference/cwchar/btowc.html)
- [cppreference: btowc](https://en.cppreference.com/w/cpp/string/multibyte/btowc)

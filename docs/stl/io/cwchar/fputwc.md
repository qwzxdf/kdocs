---
title: std::fputwc
summary: "ファイルにワイド文字を 1 文字書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::fputwc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

ファイルへの出力を 1 文字ずつ行いたい。`fputwc` は、`wchar_t` を 1 つ、`FILE*` に書き込みます。`fputc` のワイド文字版です。書き込むときに、文字をファイルの文字コードに変換するので、日本語を書けるかはロケールとモードしだいです。

!!! tip "ポイント"
    - 戻り値は書いた文字（`wint_t`）。失敗すると `WEOF`
    - ワイド文字を、ファイルの `char` のバイト列に変換して書く。変換方法はロケールとモードで決まる
    - 変換できない文字では `WEOF` が返り、`errno` が `EILSEQ` になる
    - 文字列をまとめて書くなら `fputws`

!!! info "このページを読む前に"
    [`std::fgetwc`](fgetwc.md) を先に読んでください。

## 関数の詳しい説明

### std::fputwc {#fputwc}

```cpp
std::wint_t fputwc(wchar_t ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | `wchar_t` | 書く文字 |
| `stream` | `std::FILE*` | 書き込み先 |

`ch` を、`stream` に設定されている文字コードに変換して書き込みます。成功すれば `ch` を `wint_t` にした値を返し、失敗すれば `WEOF` を返します。

書き込みの失敗には、ディスクがいっぱいなどの入出力エラーのほかに、変換できない文字があります。標準の `fopen` で開いたファイルは、現在のロケールで変換するので、"C" ロケールのまま日本語の文字を書くと、変換に失敗します。MSVC なら `fopen("f.txt", "w, ccs=UTF-8")` で UTF-8 になり、日本語も書けます。

`fputwc` は 1 文字ごとに関数を呼ぶので、大量の文字を書くには向きません。まとめて書くなら `fputws` を使います。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  std::FILE* file = std::fopen("fputwc_sample.txt", "w");
  const wchar_t text[] = L"HP30";
  for (const wchar_t ch : text) {
    if (ch == L'\0') break;
    std::fputwc(ch, file);
  }
  std::fclose(file);

  // 書いた内容を読み直して確かめる
  std::FILE* in = std::fopen("fputwc_sample.txt", "r");
  char buffer[16] = {};
  std::fgets(buffer, sizeof(buffer), in);
  std::fclose(in);
  std::remove("fputwc_sample.txt");

  std::println("{}", buffer);
}
```

```text title="実行結果"
HP30
```

ASCII の範囲なので、ワイド文字 1 つが、`char` の 1 バイトに変換されて書かれています。

## ゲームでの使いどころ

低水準の出力を自作するときくらいです。ログの出力は、UTF-8 の `std::string` に整形してから、`fwrite` か `std::ofstream` で書くのが一般的です。

## よくあるミス

??? failure "戻り値を確かめない"
    失敗すると `WEOF` が返りますが、ループの中で気づかずに続けると、ファイルが途中までしか書かれません。戻り値を検査するか、最後に `ferror` を調べます。

??? failure "ロケールを設定せずに日本語を書く"
    変換に失敗して、`WEOF` が返ります。モードの `ccs=UTF-8`（MSVC）か、ロケールを設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputws`](fputws.md) | 文字列をまとめて書く |
| [`fgetwc`](fgetwc.md) | 1 文字読む |
| `fputc` | `char` 版 |
| `std::wofstream` | C++ のワイド文字のファイル出力 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fputwc` は、ワイド文字を 1 文字、ファイルに書く
    - [x] 失敗すると `WEOF`。変換できない文字も失敗になる
    - [x] まとめて書くなら `fputws`

## 関連ページ

- [cpprefjp: fputwc](https://cpprefjp.github.io/reference/cwchar/fputwc.html)
- [cppreference: fputwc](https://en.cppreference.com/w/cpp/io/c/fputwc)

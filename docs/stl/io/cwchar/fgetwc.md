---
title: std::fgetwc
summary: "ファイルからワイド文字を 1 文字読む。"
order: 900
tags:
  - 入出力・文字列
---

# std::fgetwc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

ファイルの中身を、1 文字ずつ処理したい。`fgetwc` は、`FILE*` から `wchar_t` を 1 つ読んで返します。`fgetc` のワイド文字版です。ファイルの終わりかエラーのときは `WEOF` を返すので、戻り値を `wint_t` で受けるのが決まりです。

!!! tip "ポイント"
    - 戻り値は `wint_t`。`wchar_t` で受けない
    - 終わりかエラーのときは `WEOF`。どちらかは `feof` と `ferror` で調べる
    - ファイルのバイト列を `wchar_t` に変換する方法は、ロケールとモードで決まる
    - 1 行をまとめて読むなら `fgetws`、C++ なら `std::wifstream`

!!! info "このページを読む前に"
    [`std::wint_t`](wint_t.md) と [`WEOF`](weof.md) を先に読んでください。

## 関数の詳しい説明

### std::fgetwc {#fgetwc}

```cpp
std::wint_t fgetwc(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `std::FILE*` | 読み込み元 |

`stream` から、次のマルチバイト文字を読み、`wchar_t` に変換して返します。ファイルのバイト列を、どの文字コードとして読むかは、ストリームの設定で決まります。標準の `fopen` では、現在のロケールに従います。MSVC の `fopen("f.txt", "r, ccs=UTF-8")` のように指定すると、UTF-8 として読めます。

ファイルの終わりに達したときと、読み込みでエラーが起きたとき、`WEOF` を返します。区別するには、`feof(stream)` と `ferror(stream)` を呼びます。変換できないバイト列に当たったときも `WEOF` になり、`errno` が `EILSEQ` になります。

標準のループは、次のとおりです。

```cpp
std::wint_t ch;
while ((ch = std::fgetwc(file)) != WEOF) {
  const wchar_t wc = static_cast<wchar_t>(ch);
  // wc を処理する
}
```

`ch` を `wint_t` にしているのが大切です。`wchar_t` で受けると、`WEOF` が通常の文字の値と区別できなくなる環境があります。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  // 読み込み用のファイルを作る（ASCII）
  std::FILE* out = std::fopen("fgetwc_sample.txt", "w");
  std::fputs("ABC", out);
  std::fclose(out);

  std::FILE* in = std::fopen("fgetwc_sample.txt", "r");
  int count = 0;
  std::wint_t ch;
  while ((ch = std::fgetwc(in)) != WEOF) {
    ++count;
  }
  const bool at_end = std::feof(in) != 0;
  std::fclose(in);
  std::remove("fgetwc_sample.txt");

  std::println("読んだ文字数: {}", count);
  std::println("終わりで止まった: {}", at_end);
}
```

```text title="実行結果"
読んだ文字数: 3
終わりで止まった: true
```

`WEOF` が返ったあと、`feof` が真になるので、エラーではなく終わりに達したことが分かります。

## ゲームでの使いどころ

テキスト ファイルを 1 文字ずつ解析する、古い C のパーサーで見かけます。新しく書くなら、ファイル全体を `std::string`（UTF-8）として読み込んで、自分で解析します。

## よくあるミス

??? failure "戻り値を wchar_t で受ける"
    `WEOF` と通常の文字が区別できず、ループが終わらなかったり、途中で終わったりします。`wint_t` で受けます。

??? failure "文字コードを指定せずに日本語を読む"
    "C" ロケールでは、日本語のバイト列を変換できずに `WEOF` が返ります。ロケールかモードを設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetws`](fgetws.md) | 1 行まとめて読む |
| [`fputwc`](fputwc.md) | 1 文字書く |
| `fgetc` | `char` 版 |
| `std::wifstream` | C++ のワイド文字のファイル入力 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fgetwc` は、ファイルからワイド文字を 1 文字読む
    - [x] 戻り値は `wint_t` で受け、`WEOF` を検査する
    - [x] 終わりかエラーかは `feof` と `ferror`

## 関連ページ

- [cpprefjp: fgetwc](https://cpprefjp.github.io/reference/cwchar/fgetwc.html)
- [cppreference: fgetwc](https://en.cppreference.com/w/cpp/io/c/fgetwc)

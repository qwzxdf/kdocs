---
title: std::fputws
summary: "ファイルにワイド文字列を書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::fputws

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

ワイド文字列を、ファイルに 1 回の呼び出しで書き出したい。`fputws` は、終端の `L'\0'` の手前までを、`FILE*` に書き込みます。`fputs` のワイド文字版で、改行は自動では付きません。

!!! tip "ポイント"
    - 終端は書かない。改行も付かない。`L"...\n"` と自分で書く
    - 戻り値は、成功すると負でない値、失敗すると `EOF`（`WEOF` ではない）
    - ワイド文字を、ファイルの文字コードに変換して書く。変換できない文字は失敗になる
    - 書式つきなら `fwprintf`

!!! info "このページを読む前に"
    [`std::fputwc`](fputwc.md) を先に読んでください。

## 関数の詳しい説明

### std::fputws {#fputws}

```cpp
int fputws(const wchar_t* str, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const wchar_t*` | 書く文字列。終端があること |
| `stream` | `std::FILE*` | 書き込み先 |

`str` の先頭から、終端の手前までを、`stream` に書き込みます。`puts` と違い、改行を自動で足しません。1 行ごとに改行を入れたいなら、`L"Hero\n"` のように、文字列の中に含めます。

戻り値は、成功すると 0 または正の値です。失敗すると `EOF` を返します。`fputwc` が `WEOF` を返すのと違うので、比べる相手を間違えないようにします。

文字の変換は `fputwc` と同じで、ロケールとモードで決まります。変換できない文字があると、そこまでが書かれて、失敗になります。

書式つきで整形してから書きたいときは、`fwprintf` が便利です。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  std::FILE* out = std::fopen("fputws_sample.txt", "w");
  const int r1 = std::fputws(L"first\n", out);
  const int r2 = std::fputws(L"second\n", out);
  std::fclose(out);

  // 書いた内容を読み直す
  std::FILE* in = std::fopen("fputws_sample.txt", "r");
  char buffer[32] = {};
  const std::size_t n = std::fread(buffer, 1, sizeof(buffer) - 1, in);
  std::fclose(in);
  std::remove("fputws_sample.txt");

  std::println("成功: {}", r1 >= 0 && r2 >= 0);
  std::println("バイト数: {}", n);
}
```

```text title="実行結果"
成功: true
バイト数: 13
```

`first\nsecond\n` の 13 文字が、13 バイトで読み出せました。テキスト モードでは、Windows が `\n` を `\r\n` で書き、読むときに `\n` へ戻すので、読み直した結果は同じです。ファイルの実際の大きさは、Windows では 2 バイト大きくなります。

## ゲームでの使いどころ

ワイド文字のログを書く古いコードで見かけます。新しく書くなら、UTF-8 の `std::string` を `std::ofstream` に書きます。

## よくあるミス

??? failure "改行が付くと思う"
    `puts` と違い、`fputws` は改行を足しません。文字列に `\n` を含めます。

??? failure "WEOF と比べる"
    戻り値は `int` で、失敗は `EOF` です。`WEOF` と比べると、判定が外れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputwc`](fputwc.md) | 1 文字書く |
| [`fgetws`](fgetws.md) | 1 行読む |
| [`fwprintf`](fwprintf.md) | 書式つきで書く |
| `fputs` | `char` 版 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fputws` は、ワイド文字列をファイルに書く。改行は付かない
    - [x] 失敗は `EOF`
    - [x] 書式つきなら `fwprintf`

## 関連ページ

- [cpprefjp: fputws](https://cpprefjp.github.io/reference/cwchar/fputws.html)
- [cppreference: fputws](https://en.cppreference.com/w/cpp/io/c/fputws)

---
title: std::fwprintf
summary: "書式を指定して、ワイド文字でファイルに出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::fwprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`wprintf` は標準出力に決まっています。ログ ファイルや標準エラー出力に、同じ書式で書きたいときは、出力先を指定できる `fwprintf` を使います。`fprintf` のワイド文字版で、出力先以外の使い方は `wprintf` と同じです。

!!! tip "ポイント"
    - 第 1 引数が出力先の `FILE*`。`stdout` / `stderr` / `fopen` で開いたファイル
    - ワイド文字列は `%ls`、`char` の文字列は `%hs`
    - ファイルに書かれる形（UTF-8 か UTF-16 か）は、`fopen` のモード（`ccs=`）やロケールで決まる
    - 戻り値は書いた文字数。エラーなら負の値

!!! info "このページを読む前に"
    [`std::wprintf`](wprintf.md) を先に読んでください。

## 関数の詳しい説明

### std::fwprintf {#fwprintf}

```cpp
int fwprintf(std::FILE* stream, const wchar_t* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `std::FILE*` | 出力先 |
| `format` | `const wchar_t*` | 書式文字列 |
| `...` | 可変引数 | 書式に対応する値 |

`stream` に、`format` に従って整形したワイド文字を書き込みます。`stream` に `stdout` を渡せば `wprintf` と同じになります。

ワイド文字を、ファイルにどう書くかは、ストリームの設定しだいです。標準の `fopen` で開いただけのファイルでは、ワイド文字が、ロケールに従った `char` のバイト列に変換されて書かれます。"C" ロケールのままでは、ASCII 以外の文字が変換できずに、書き込みが失敗することがあります。

MSVC には、`fopen("log.txt", "w, ccs=UTF-8")` のように、文字コードを指定できる拡張があります。これを使うと、`wchar_t` の文字列が UTF-8 で書かれ、日本語も扱えます。標準ではないので、移植性はありません。

出力の向きの決まりは、`wprintf` と同じです。同じ `FILE*` に `fprintf` と `fwprintf` を混ぜてはいけません。

戻り値は、書き込んだ文字数です。ディスクがいっぱいなどで失敗すると、負の値を返します。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  std::FILE* file = std::fopen("fwprintf_sample.txt", "w");
  if (!file) return 1;

  const int written = std::fwprintf(file, L"HP=%d name=%ls\n", 30, L"Hero");
  std::fclose(file);
  std::remove("fwprintf_sample.txt");

  std::println("書いた文字数: {}", written);
}
```

```text title="実行結果"
書いた文字数: 16
```

`HP=30 name=Hero` と改行で 16 文字です。サンプルのファイルは、確認したあとに消しています。

## ゲームでの使いどころ

Windows のゲームで、`wchar_t` のメッセージをログ ファイルに書く古いコードに出会います。新しく書くなら、UTF-8 の `std::string` と `std::ofstream`、あるいは `std::format` で整形して書き出します。

## よくあるミス

??? failure "文字コードを指定せずに日本語を書く"
    "C" ロケールのままでは、変換できずに失敗するか、`?` になります。MSVC の `ccs=UTF-8` か、UTF-8 の `char` の文字列に直してから書きます。

??? failure "fclose を忘れて、内容が残らない"
    バッファに溜まった分は、`fclose` か `fflush` で書き出されます。異常終了すると、最後の行が消えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wprintf`](wprintf.md) | 標準出力に出す |
| [`swprintf`](swprintf.md) | 文字の配列に書き込む |
| [`fprintf`](../cstdio/fprintf.md) | `char` 版 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fwprintf` は、出力先を指定できる `wprintf`
    - [x] ファイルに書かれる形は、モードとロケールで決まる
    - [x] 同じ `FILE*` に `char` の関数と混ぜない

## 関連ページ

- [cpprefjp: fwprintf](https://cpprefjp.github.io/reference/cwchar/fwprintf.html)
- [cppreference: fwprintf](https://en.cppreference.com/w/cpp/io/c/fwprintf)

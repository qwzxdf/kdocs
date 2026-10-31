---
title: std::fgetws
summary: "ファイルからワイド文字列を 1 行読む。"
order: 900
tags:
  - 入出力・文字列
---

# std::fgetws

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

テキスト ファイルを 1 行ずつ読んで処理したい。`fgetws` は、改行までを（または指定した文字数までを）`wchar_t` の配列に読み込みます。`fgets` のワイド文字版です。1 文字ずつ `fgetwc` を呼ぶより簡単で、バッファの大きさも渡せるので安全です。

!!! tip "ポイント"
    - 改行までを読み、改行も配列に含む。最後に終端が付く
    - 第 2 引数は、配列の要素数（終端を含む）。それを超えて読まない
    - 戻り値は、成功なら `str`、ファイルの終わりかエラーなら `nullptr`
    - 行が `count - 1` 文字より長いと、途中で切れる。続きは次の呼び出しで読まれる

!!! info "このページを読む前に"
    [`std::fgetwc`](fgetwc.md) を先に読んでください。

## 関数の詳しい説明

### std::fgetws {#fgetws}

```cpp
wchar_t* fgetws(wchar_t* str, int count, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `wchar_t*` | 読み込み先 |
| `count` | `int` | 読む最大の要素数（終端を含む） |
| `stream` | `std::FILE*` | 読み込み元 |

`stream` から、改行を読み込むか、`count - 1` 要素に達するか、ファイルの終わりに達するまで読み、`str` に書き込んで、終端の `L'\0'` を付けます。

改行は、`str` の末尾に残ります。1 行の中身だけが欲しいときは、末尾の `L'\n'` を取り除きます。

```cpp
wchar_t line[256];
while (std::fgetws(line, 256, file)) {
  const std::size_t len = std::wcslen(line);
  if (len > 0 && line[len - 1] == L'\n') line[len - 1] = L'\0';
  // line を処理する
}
```

1 行が `count - 1` 要素より長いと、そこで切れます。残りは次の `fgetws` で読まれます。長い行を扱うなら、配列を大きくするか、切れたかを（末尾が改行かで）調べて、続けて読みます。

戻り値は、成功すると `str` で、ファイルの終わりで 1 要素も読めなかった場合と、エラーの場合は `nullptr` です。エラーのとき、`str` の中身は不定です。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  std::FILE* out = std::fopen("fgetws_sample.txt", "w");
  std::fputs("first\nsecond\n", out);
  std::fclose(out);

  std::FILE* in = std::fopen("fgetws_sample.txt", "r");
  wchar_t line[32];
  int lines = 0;
  while (std::fgetws(line, 32, in)) {
    ++lines;
  }
  std::fclose(in);
  std::remove("fgetws_sample.txt");

  std::println("行数: {}", lines);
}
```

```text title="実行結果"
行数: 2
```

## ゲームでの使いどころ

設定ファイルを 1 行ずつ読む古いコードに出てきます。新しく書くなら、`std::ifstream` と `std::getline` で UTF-8 の行を読むほうが、行の長さの制限もなく、簡単です。

## よくあるミス

??? failure "末尾の改行を取り除かない"
    比較や表示のときに、改行が残っていると不一致になります。長さを調べて、末尾が改行なら外します。

??? failure "count に配列の要素数ではなくバイト数を渡す"
    `sizeof(line)` はバイト数です。要素数は `sizeof(line) / sizeof(line[0])` です。バイト数を渡すと、あふれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetwc`](fgetwc.md) | 1 文字だけ読む |
| [`fputws`](fputws.md) | 文字列を書く |
| `fgets` | `char` 版 |
| `std::getline` | C++ の 1 行読み込み。長さの制限がない |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fgetws` は、ファイルから 1 行を、ワイド文字列として読む
    - [x] `count` は要素数。末尾の改行は残る
    - [x] 新しいコードは `std::getline`

## 関連ページ

- [cpprefjp: fgetws](https://cpprefjp.github.io/reference/cwchar/fgetws.html)
- [cppreference: fgetws](https://en.cppreference.com/w/cpp/io/c/fgetws)

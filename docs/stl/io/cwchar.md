---
title: <cwchar>
summary: "ワイド文字（`wchar_t`）の C 由来の関数群。"
order: 100
tags:
  - 入出力・文字列
---

# &lt;cwchar&gt;

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <cwchar>`
</div>

Windows の API は、文字列を `wchar_t`（UTF-16）で受け取ります。ファイルのパス、ウィンドウのタイトル、エラーメッセージ。この `wchar_t` の文字列を、C の標準ライブラリで扱うための関数群が `<cwchar>` です。`strlen` に当たる `wcslen`、`printf` に当たる `wprintf` のように、多くの関数が、`str` が `wcs` に、`printf` が `wprintf` に変わった名前で用意されています。

これらは C の流儀の関数で、文字数の管理もバッファの大きさも自分で見る必要があります。新しいコードでは `std::wstring` や `std::format` を使い、この関数群は、Windows API との橋渡しや、古いコードを読むために知っておく、くらいの位置づけです。

!!! tip "ポイント"
    - `str…` の関数に対して、`wcs…`（文字列）、`wmem…`（メモリ）、`w…printf`（書式）という名前の対がある
    - Windows の `wchar_t` は 16 ビットで UTF-16。Linux や macOS では 32 ビットで UTF-32
    - バイト列（`char`）との変換は `mbrtowc` / `wcrtomb` などの組。ロケールの設定に左右される
    - 新しいコードは `std::wstring`。UTF-8 と UTF-16 の変換は、文字コードの章を見る

!!! info "このページを読む前に"
    [文字コード](../../encoding/index.md)の章で、UTF-8 と UTF-16 の違いと、Windows API の A / W の関係を先に読むと、この関数群が必要になる理由が分かります。

## 関数の詳しい説明

### 関数の一覧 {#list}

| 分類 | 関数 | 役割 |
| --- | --- | --- |
| 型と定数 | [`wint_t`](cwchar/wint_t.md)、[`WEOF`](cwchar/weof.md)、[`mbstate_t`](cwchar/mbstate_t.md) | 文字の型、終端の値、変換の途中状態 |
| 文字列の操作 | [`wcscpy`](cwchar/wcscpy.md)、[`wcscmp`](cwchar/wcscmp.md)、[`wmemcpy`](cwchar/wmemcpy.md) | コピー、比較 |
| 数値への変換 | [`wcstol`](cwchar/wcstol.md) | 文字列を `long` に変換する |
| 書式つき入出力 | [`wprintf`](cwchar/wprintf.md)、[`fwprintf`](cwchar/fwprintf.md)、[`swprintf`](cwchar/swprintf.md)、[`wscanf`](cwchar/wscanf.md) | `printf` のワイド版 |
| 文字の入出力 | [`fgetwc`](cwchar/fgetwc.md)、[`fputwc`](cwchar/fputwc.md)、[`fgetws`](cwchar/fgetws.md)、[`fputws`](cwchar/fputws.md) | ファイルへの読み書き |
| `char` との変換 | [`btowc`](cwchar/btowc.md)、[`wctob`](cwchar/wctob.md)、[`mbrlen`](cwchar/mbrlen.md)、[`mbrtowc`](cwchar/mbrtowc.md)、[`wcrtomb`](cwchar/wcrtomb.md)、[`mbsrtowcs`](cwchar/mbsrtowcs.md)、[`wcsrtombs`](cwchar/wcsrtombs.md) | マルチバイト文字との変換 |

この表は引くためのもので、1 つずつの説明は各ページに書いています。

### wcslen {#wcslen}

```cpp
std::size_t wcslen(const wchar_t* s);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `const wchar_t*` | 終端が `L'\0'` のワイド文字列 |

終端を除いた、`wchar_t` の個数を返します。バイト数ではなく、要素の個数です。Windows の UTF-16 では、基本多言語面の文字は 1 要素ですが、絵文字などの一部の文字は 2 要素（サロゲート ペア）になります。そのため、`wcslen` が返す数と、見た目の文字数は一致しないことがあります。

終端を探して先頭から調べるので、計算量は文字列の長さに比例します。ループの条件に毎回書くと、遅くなります。長さは先に変数に取り出します。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::println("長さ: {}", std::wcslen(L"HP 30"));
  std::println("wchar_t の大きさ: {} バイト", sizeof(wchar_t));
}
```

```text title="実行結果"
長さ: 5
wchar_t の大きさ: 2 バイト
```

大きさの 2 バイトは、Windows の結果です。Linux では 4 バイトになります。

## ゲームでの使いどころ

Windows のゲームで、パスやウィンドウ タイトルを Windows API に渡すときに、`wchar_t` の文字列が出てきます。内部の文字列は UTF-8 の `std::string` にそろえ、API を呼ぶ直前に UTF-16 へ変換する、という作りが推奨です。

## よくあるミス

??? failure "wchar_t を UTF-32 と考える"
    Windows の `wchar_t` は UTF-16 で、1 要素が 16 ビットです。絵文字などは、2 要素のサロゲート ペアになります。`wcslen` の結果は、文字数とは限りません。

??? failure "%s と %ls を混同する"
    `wprintf` の `%s` は、MSVC ではワイド文字列、標準では `char` の文字列を意味します。移植性のために、ワイド文字列は `%ls` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::wstring`](../containers/string.md) | C++ のワイド文字列。普段はこちら |
| [`<cstring>`](../memory/cstring.md) | `char` 版の C 由来の関数群 |
| [文字コード](../../encoding/index.md) | UTF-8 と Windows API |

## コンパイラ対応

C++98 から使えます。`wchar_t` の大きさが環境で違う（Windows は 16 ビット、Linux は 32 ビット）ことに注意します。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `<cwchar>` は、`wchar_t` を扱う C 由来の関数群
    - [x] Windows の `wchar_t` は UTF-16。文字数と要素数は一致しないことがある
    - [x] 新しいコードは `std::wstring`。内部は UTF-8 にして、API の直前で変換する

## 関連ページ

- [cpprefjp: cwchar](https://cpprefjp.github.io/reference/cwchar.html)
- [cppreference: Null-terminated wide strings](https://en.cppreference.com/w/cpp/string/wide)

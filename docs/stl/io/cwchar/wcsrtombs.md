---
title: std::wcsrtombs
summary: "ワイド文字列を、マルチバイト文字列に変換する（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcsrtombs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`wchar_t` の文字列を、ファイルに書いたり、`char` を受け取る関数に渡したりするために、`char` の文字列に直します。文字列全体を 1 回の呼び出しで変換するのが `wcsrtombs` で、`mbsrtowcs` の逆の働きです。

!!! tip "ポイント"
    - `dst` を `nullptr` にすると、必要なバイト数だけを返す
    - 第 2 引数は `const wchar_t**`。変換した位置まで進む。全部変換できたら `nullptr`
    - 戻り値は書いたバイト数（終端は含まない）。変換できない文字があれば `(size_t)-1`
    - バイト数は文字数ではない。複数バイトの文字があると、文字数より大きい

!!! info "このページを読む前に"
    [`std::mbsrtowcs`](mbsrtowcs.md) と [`std::wcrtomb`](wcrtomb.md) を先に読んでください。

## 関数の詳しい説明

### std::wcsrtombs {#wcsrtombs}

```cpp
std::size_t wcsrtombs(char* dst, const wchar_t** src, std::size_t len, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dst` | `char*` | 変換結果の書き込み先。`nullptr` なら長さだけ調べる |
| `src` | `const wchar_t**` | 変換元の文字列へのポインタのポインタ。変換した位置まで進む |
| `len` | `std::size_t` | 書き込む最大のバイト数 |
| `ps` | `std::mbstate_t*` | 変換の途中状態 |

`*src` のワイド文字列を、終端まで（または `len` バイトに達するまで）変換して、`dst` に書き込みます。1 文字の途中で `len` に達しそうなときは、その文字は書かず、手前で止まります。

必要な大きさは、`dst` を `nullptr` にして呼んで調べます。戻り値は<strong>バイト数</strong>で、文字数ではありません。日本語を UTF-8 に変換すると、1 文字が 3 バイトになるので、文字数の 3 倍近くになります。

不正な（そのロケールで表せない）文字があると、`(size_t)-1` を返し、`errno` が `EILSEQ` になります。そのとき `*src` は、その文字を指します。

出力のバッファは、ワイド文字の数 × `MB_CUR_MAX` + 1 バイトを確保しておけば、必ず収まります。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <cwchar>
#include <print>

int main() {
  const wchar_t* text = L"HP30";
  std::mbstate_t state{};

  // 1. 必要なバイト数だけを調べる
  const wchar_t* p = text;
  const std::size_t n = std::wcsrtombs(nullptr, &p, 0, &state);
  std::println("バイト数: {}", n);

  // 2. 変換する
  char out[16] = {};
  p = text;
  state = std::mbstate_t{};
  std::wcsrtombs(out, &p, sizeof(out), &state);
  std::println("変換できた: {}", std::strcmp(out, "HP30") == 0);
}
```

```text title="実行結果"
バイト数: 4
変換できた: true
```

## ゲームでの使いどころ

Windows API から受け取った UTF-16 の文字列を、ログ ファイルに UTF-8 で書くときの変換などで使います。Windows では `WideCharToMultiByte(CP_UTF8, ...)` が、ロケールに依存せず確実です。

## よくあるミス

??? failure "バッファの大きさを文字数で見積もる"
    必要なのはバイト数です。日本語を含むと、文字数の 3 倍以上になります。`nullptr` で先にバイト数を調べます。

??? failure "ロケールが "C" のまま日本語を変換する"
    "C" ロケールでは、ASCII 以外の文字を変換できず、`(size_t)-1` が返ります。ロケールを設定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbsrtowcs`](mbsrtowcs.md) | 逆方向の変換 |
| [`wcrtomb`](wcrtomb.md) | 1 文字ずつ変換する |
| `WideCharToMultiByte` | Windows の API。UTF-8 を直接指定できる |

## コンパイラ対応

C++98 から使えます。MSVC は、`wcsrtombs` に警告（C4996）を出すことがあり、`wcsrtombs_s` を勧めます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcsrtombs` は、ワイド文字列を `char` の文字列にまとめて変換する
    - [x] `dst` を `nullptr` にすると、必要なバイト数が分かる
    - [x] バイト数は文字数より大きいことがある

## 関連ページ

- [cpprefjp: wcsrtombs](https://cpprefjp.github.io/reference/cwchar/wcsrtombs.html)
- [cppreference: wcsrtombs](https://en.cppreference.com/w/cpp/string/multibyte/wcsrtombs)

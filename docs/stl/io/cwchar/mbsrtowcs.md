---
title: std::mbsrtowcs
summary: "マルチバイト文字列を、ワイド文字列に変換する（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::mbsrtowcs

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`char` の文字列を、`wchar_t` の文字列にまとめて変換したい。1 文字ずつ `mbrtowc` を呼ぶ代わりに、文字列全体を 1 回の呼び出しで変換するのが `mbsrtowcs` です。UTF-8 のファイルから読んだ文字列を、`wchar_t` の API に渡すときの、C の標準の方法です。

!!! tip "ポイント"
    - `dst` を `nullptr` にすると、変換後の文字数だけを返す。先に必要な大きさを知れる
    - 第 2 引数は `const char**`。変換できた所まで、ポインタが進む。全部変換できたら `nullptr`
    - 戻り値は書いた文字数（終端は含まない）。不正なら `(size_t)-1`
    - 結果はロケールで変わる

!!! info "このページを読む前に"
    [`std::mbrtowc`](mbrtowc.md) と [`std::mbstate_t`](mbstate_t.md) を先に読んでください。

## 関数の詳しい説明

### std::mbsrtowcs {#mbsrtowcs}

```cpp
std::size_t mbsrtowcs(wchar_t* dst, const char** src, std::size_t len, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dst` | `wchar_t*` | 変換結果の書き込み先。`nullptr` なら長さだけ調べる |
| `src` | `const char**` | 変換元の文字列へのポインタのポインタ。変換した位置まで進む |
| `len` | `std::size_t` | 書き込む最大の文字数 |
| `ps` | `std::mbstate_t*` | 変換の途中状態 |

`*src` の指す文字列を、終端まで（または `len` 文字に達するまで）変換して、`dst` に書き込みます。終端まで変換できた場合は、`dst` にも終端が書かれますが、戻り値は終端を数えません。

第 2 引数が二重のポインタなのは、変換がどこまで進んだかを、呼び出し側に返すためです。終端まで変換できたときは `*src` が `nullptr` になり、`len` に達して途中で止まったときは、止まった位置を指します。

必要な大きさは、まず `dst` を `nullptr` にして呼んで知ります。

```cpp
const char* p = text;
std::mbstate_t state{};
const std::size_t n = std::mbsrtowcs(nullptr, &p, 0, &state);   // 文字数だけ調べる
```

`n` に 1 を足した大きさの領域を確保し、もう一度 `p` を戻してから呼びます。1 回目の呼び出しで `p` が進んでいることに、注意します。

不正なバイト列に当たると、`(size_t)-1` を返し、`errno` が `EILSEQ` になります。そのとき `*src` は、不正だった位置を指します。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  const char* text = "HP30";
  std::mbstate_t state{};

  // 1. 必要な文字数だけを調べる
  const char* p = text;
  const std::size_t n = std::mbsrtowcs(nullptr, &p, 0, &state);
  std::println("文字数: {}", n);

  // 2. 変換する（終端の分、1 つ多く確保）
  wchar_t out[8] = {};
  p = text;
  state = std::mbstate_t{};
  std::mbsrtowcs(out, &p, 8, &state);
  std::println("変換できた: {}", std::wcscmp(out, L"HP30") == 0);
  std::println("全部変換して nullptr: {}", p == nullptr);
}
```

```text title="実行結果"
文字数: 4
変換できた: true
全部変換して nullptr: true
```

## ゲームでの使いどころ

ファイルから読んだ `char` の文字列を `wchar_t` の API に渡すときに使えます。ただし、Windows のゲームでは、UTF-8 を直接指定できる `MultiByteToWideChar(CP_UTF8, ...)` が定番です。

## よくあるミス

??? failure "長さを調べたあと、ポインタを戻さない"
    1 回目の呼び出しで `p` が進みます（全部変換すると `nullptr`）。2 回目の前に、`p = text;` と元に戻します。

??? failure "len に足りない値を渡して、終端が付かない"
    `len` に達して止まると、`dst` には終端が書かれません。`len` は必要な文字数に 1 を足した値にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wcsrtombs`](wcsrtombs.md) | 逆方向の変換 |
| [`mbrtowc`](mbrtowc.md) | 1 文字ずつ変換する |
| `MultiByteToWideChar` | Windows の API。UTF-8 を直接指定できる |

## コンパイラ対応

C++98 から使えます。MSVC は、`mbsrtowcs` に警告（C4996）を出すことがあり、`mbsrtowcs_s` を勧めます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mbsrtowcs` は、`char` の文字列を `wchar_t` の文字列にまとめて変換する
    - [x] `dst` を `nullptr` にすると、必要な文字数が分かる
    - [x] `src` は変換した位置まで進む。再び呼ぶ前に戻す

## 関連ページ

- [cpprefjp: mbsrtowcs](https://cpprefjp.github.io/reference/cwchar/mbsrtowcs.html)
- [cppreference: mbsrtowcs](https://en.cppreference.com/w/cpp/string/multibyte/mbsrtowcs)

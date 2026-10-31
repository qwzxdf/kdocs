---
title: std::wcrtomb
summary: "ワイド文字を、マルチバイト文字に変換する（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcrtomb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`wchar_t` の 1 文字を、ファイルやネットワークに出すための `char` のバイト列に直したい。`wcrtomb` は、ワイド文字 1 つを、現在のロケールのマルチバイト表現に変換して、バッファに書き込み、書いたバイト数を返します。`mbrtowc` の逆の働きです。

!!! tip "ポイント"
    - 書き込み先は `MB_CUR_MAX` バイト以上の領域
    - 戻り値は書いたバイト数。変換できないときは `(size_t)-1`（`errno` が `EILSEQ`）
    - 文字列の最後に、初期状態に戻す列を出したいときは `wc` に `L'\0'` を渡す
    - 結果はロケールで変わる

!!! info "このページを読む前に"
    [`std::mbstate_t`](mbstate_t.md) と [`std::mbrtowc`](mbrtowc.md) を先に読んでください。

## 関数の詳しい説明

### std::wcrtomb {#wcrtomb}

```cpp
std::size_t wcrtomb(char* s, wchar_t wc, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | `char*` | 書き込み先。`MB_CUR_MAX` バイト以上の領域 |
| `wc` | `wchar_t` | 変換するワイド文字 |
| `ps` | `std::mbstate_t*` | 変換の途中状態 |

`wc` を現在のロケールのマルチバイト表現に変換して、`s` に書き込みます。書き込んだバイト数が戻り値です。ASCII なら 1 バイト、UTF-8 の日本語なら 3 バイトです。

書き込み先は、1 文字の最大バイト数 `MB_CUR_MAX` 以上の大きさが必要です。UTF-8 なら 4 バイトです。1 バイトの配列に、ワイド文字を書き込もうとすると、あふれて壊します。

終端は付きません。文字列として使うなら、全部を変換し終えたあとに、自分で `'\0'` を足します。

`wc` を `L'\0'` にすると、状態を初期状態に戻すための列（ISO-2022-JP のような状態を持つ方式の場合）と、終端の `'\0'` を書き込みます。通常の UTF-8 では、`'\0'` の 1 バイトだけです。

変換できないワイド文字（そのロケールで表せない文字）を渡すと、`(size_t)-1` を返し、`errno` が `EILSEQ` になります。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::mbstate_t state{};
  char buffer[16] = {};  // MB_CUR_MAX 以上の大きさ

  const std::size_t n = std::wcrtomb(buffer, L'A', &state);
  std::println("書いたバイト数: {}", n);
  std::println("中身は 'A': {}", buffer[0] == 'A');
}
```

```text title="実行結果"
書いたバイト数: 1
中身は 'A': true
```

## ゲームでの使いどころ

C の標準だけで書き出したいとき以外は、Windows の `WideCharToMultiByte` で UTF-16 から UTF-8 に変換するほうが確実です。

## よくあるミス

??? failure "書き込み先が小さい"
    `char c; wcrtomb(&c, wc, &state);` は、複数バイトになる文字で領域の外に書きます。`MB_CUR_MAX` 以上の配列を用意します。

??? failure "戻り値の -1 を確かめない"
    変換できない文字で `-1` が返ったとき、バッファの中身は不定です。検査してから使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbrtowc`](mbrtowc.md) | 逆方向の変換 |
| [`wctob`](wctob.md) | 1 バイトで表せる文字だけ |
| [`wcsrtombs`](wcsrtombs.md) | 文字列全体を変換する |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcrtomb` は、ワイド文字 1 つを `char` の列に変換して、バイト数を返す
    - [x] 書き込み先は `MB_CUR_MAX` バイト以上
    - [x] 終端は付かない。`-1` は変換できない

## 関連ページ

- [cpprefjp: wcrtomb](https://cpprefjp.github.io/reference/cwchar/wcrtomb.html)
- [cppreference: wcrtomb](https://en.cppreference.com/w/cpp/string/multibyte/wcrtomb)

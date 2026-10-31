---
title: std::wcstol
summary: "ワイド文字列を long に変換する。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcstol

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

ユーザーが入力した `L"123"` や、設定ファイルの `L"0x1F"` のような、文字列で書かれた数を、整数に直したい。`wcstol` は、`wchar_t` の文字列を `long` に変換する関数です。`char` 版は `strtol` です。数字のあとに余計な文字が続いていても、読めた所までを変換して、どこまで読めたかを教えてくれます。

!!! tip "ポイント"
    - 先頭の空白は読み飛ばし、`+` / `-` を受け付ける
    - `base` に 0 を渡すと、`0x` なら 16 進、`0` なら 8 進、それ以外は 10 進と自動判定する
    - 読み終えた位置を `str_end` で受け取れる。何も変換できなかったときは `str` と同じ
    - 範囲を超えると `LONG_MAX` か `LONG_MIN` を返し、`errno` が `ERANGE` になる

!!! info "このページを読む前に"
    [`<cwchar>`](../cwchar.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::wcstol {#wcstol}

```cpp
long wcstol(const wchar_t* str, wchar_t** str_end, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `const wchar_t*` | 変換する文字列 |
| `str_end` | `wchar_t**` | 読み終えた位置を受け取るポインタ。不要なら `nullptr` |
| `base` | `int` | 進数。2〜36 か 0 |

`str` の先頭の空白を飛ばし、符号と数字を読み、数字でない文字に出会ったところで止まります。`str_end` が `nullptr` でなければ、止まった位置（読めなかった最初の文字）を `*str_end` に入れます。

`base` が 10 なら 10 進、16 なら 16 進です。16 進のときは、先頭の `0x` があっても受け付けます。0 を渡すと、先頭の様子から自動で判定します。`0x` で始まれば 16 進、`0` で始まれば 8 進、それ以外は 10 進です。

何も変換できなかったときは、0 を返し、`*str_end` は `str` のままです。ただし、`"0"` を正しく変換した結果の 0 と区別するには、`str_end` が `str` と同じかを見ます。

範囲を超えたときは、`LONG_MAX` または `LONG_MIN` を返して、`errno` に `ERANGE` を入れます。Windows では `long` が 32 ビットなので、扱える範囲は約 ±21 億です。64 ビットの範囲が要るなら、`wcstoll` を使います。

入力が外から来る値なら、`str_end` を確認して、全部が数字だったか（`*end == L'\0'`）を調べます。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  wchar_t* end = nullptr;

  const long a = std::wcstol(L"123abc", &end, 10);
  std::println("{} 残り先頭: {}", a, static_cast<char>(*end));

  const long b = std::wcstol(L"0x1F", nullptr, 16);
  std::println("16 進: {}", b);

  const long c = std::wcstol(L"  -42", nullptr, 10);
  std::println("符号と空白: {}", c);

  const wchar_t* text = L"xyz";
  std::wcstol(text, &end, 10);
  std::println("何も読めなかった: {}", end == text);
}
```

```text title="実行結果"
123 残り先頭: a
16 進: 31
符号と空白: -42
何も読めなかった: true
```

## ゲームでの使いどころ

Windows のコマンドライン引数（`wmain` の `wchar_t* argv[]`）を数に直すときに使います。自分のコードでは、`std::from_chars` や `std::stoi` を使うほうが、エラーの扱いが明確です。

## よくあるミス

??? failure "余計な文字が続いていても気づかない"
    `L"12abc"` は、エラーにならずに 12 を返します。入力を厳密に検査するなら、`*end == L'\0'` を確かめます。

??? failure "0 が返ったのを、失敗と決めつける"
    `L"0"` も 0 を返します。失敗かどうかは、`end == str` で判断します。

??? failure "errno を事前に 0 にしない"
    `ERANGE` を見るなら、呼ぶ前に `errno = 0;` にしておきます。前の関数が残した値と区別できなくなります。

## 類似

| 名前 | 違い |
| --- | --- |
| `wcstoll` | `long long` に変換する |
| `wcstod` | `double` に変換する |
| `std::stoi` / `std::stol` | `std::string` / `std::wstring` から変換する。失敗は例外 |
| `std::from_chars` | 例外なしで速い。`char` 版のみ |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcstol` は、ワイド文字列を `long` に変換し、読み終えた位置を返す
    - [x] 全部が数字だったかは `*end == L'\0'` で確かめる
    - [x] 範囲を超えると `ERANGE`。64 ビットなら `wcstoll`

## 関連ページ

- [cpprefjp: wcstol](https://cpprefjp.github.io/reference/cwchar/wcstol.html)
- [cppreference: wcstol](https://en.cppreference.com/w/cpp/string/wide/wcstol)

---
title: std::mbrtowc
summary: "マルチバイト文字を、ワイド文字に変換する（途中状態つき）。"
order: 900
tags:
  - 入出力・文字列
---

# std::mbrtowc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

UTF-8 や Shift_JIS の `char` の並びから、`wchar_t` の 1 文字を取り出したい。`mbrtowc` は、先頭の 1 文字ぶんのバイトを読み、対応するワイド文字を書き込んで、使ったバイト数を返します。続けて呼べば、文字列を 1 文字ずつ変換できます。名前の `r` は restartable（再開可能）の意味で、途中で区切れたバイト列も、状態を引き継いで続きから変換できます。

!!! tip "ポイント"
    - 戻り値は使ったバイト数。0 なら終端文字、`(size_t)-1` は不正、`(size_t)-2` は途中
    - 変換結果は `pwc` に書き込む。`nullptr` なら、変換せずに長さだけを調べる
    - 状態は `mbstate_t`。文字列ごとに `{}` で初期化する
    - 結果はロケールに左右される。UTF-8 を扱うには、ロケールの設定が要る

!!! info "このページを読む前に"
    [`std::mbstate_t`](mbstate_t.md) と [`std::mbrlen`](mbrlen.md) を先に読んでください。

## 関数の詳しい説明

### std::mbrtowc {#mbrtowc}

```cpp
std::size_t mbrtowc(wchar_t* pwc, const char* s, std::size_t n, std::mbstate_t* ps);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pwc` | `wchar_t*` | 変換結果の書き込み先。`nullptr` ならば書き込まない |
| `s` | `const char*` | 変換元のバイト列 |
| `n` | `std::size_t` | 調べてよい最大のバイト数 |
| `ps` | `std::mbstate_t*` | 変換の途中状態 |

`s` の先頭から最大 `n` バイトを調べ、1 文字が完成したら、そのワイド文字を `*pwc` に書き込み、その文字に使ったバイト数を返します。

戻り値は `mbrlen` と同じ決まりです。1 以上は使ったバイト数、0 は終端文字（`*pwc` に `L'\0'` が入る）、`(size_t)-1` は不正なバイト列（`errno` が `EILSEQ`）、`(size_t)-2` は文字の途中で `n` バイトが尽きたことを表します。

文字列を全部変換するには、戻り値のぶんだけ `s` を進めて、繰り返し呼びます。

```cpp
std::mbstate_t state{};
const char* p = text;
wchar_t wc;
while (true) {
  const std::size_t len = std::mbrtowc(&wc, p, MB_CUR_MAX, &state);
  if (len == 0 || len == static_cast<std::size_t>(-1)) break;   // 終端か不正
  p += len;
  // wc を使う
}
```

`n` には、1 文字の最大バイト数である `MB_CUR_MAX` を渡すのが定番です。それより少ない値だと、`(size_t)-2` が返ることがあります。

UTF-16 の環境（Windows）では、基本多言語面の外の文字は、`wchar_t` 1 つに収まりません。この関数は 1 つの `wchar_t` しか返さないため、そうした文字は変換できません。完全な変換には、Windows の `MultiByteToWideChar` を使います。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  const char* text = "HP30";
  std::mbstate_t state{};
  const char* p = text;
  wchar_t wc = 0;
  int count = 0;

  while (true) {
    const std::size_t len = std::mbrtowc(&wc, p, MB_CUR_MAX, &state);
    if (len == 0 || len == static_cast<std::size_t>(-1)) break;
    p += len;
    ++count;
  }
  std::println("変換した文字数: {}", count);
  std::println("終端で止まった: {}", wc == L'\0');
}
```

```text title="実行結果"
変換した文字数: 4
終端で止まった: true
```

終端文字に当たると、`len` が 0 になり、ループを抜けます。ここで `wc` は `L'\0'` になっています。

## ゲームでの使いどころ

C の標準だけで、環境に依存しない変換を書きたい場面で使いますが、実際の Windows ゲームでは `MultiByteToWideChar` と `WideCharToMultiByte` を使うことがほとんどです。ロケールの設定に依存せず、UTF-8 を直接指定できるからです。

## よくあるミス

??? failure "状態を初期化しない"
    `mbstate_t` が不定のまま呼ぶと、結果が壊れます。`{}` で初期化します。

??? failure "n を 1 にする"
    複数バイトの文字は、1 バイトだけでは完成しないので、`(size_t)-2` が返ります。`MB_CUR_MAX` を渡します。

??? failure "len が -1 のとき p を進める"
    不正なバイト列で `p += len` とすると、ポインタが飛びます。必ず `-1` を先に検査します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`mbrlen`](mbrlen.md) | 長さだけを返す |
| [`wcrtomb`](wcrtomb.md) | 逆方向の変換 |
| [`mbsrtowcs`](mbsrtowcs.md) | 文字列全体を変換する |
| [`btowc`](btowc.md) | 1 バイトで完結する文字だけ |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `mbrtowc` は、先頭の 1 文字をワイド文字に変換して、使ったバイト数を返す
    - [x] `n` は `MB_CUR_MAX`。状態は `{}` で初期化する
    - [x] 0 は終端、`-1` は不正、`-2` は途中

## 関連ページ

- [cpprefjp: mbrtowc](https://cpprefjp.github.io/reference/cwchar/mbrtowc.html)
- [cppreference: mbrtowc](https://en.cppreference.com/w/cpp/string/multibyte/mbrtowc)

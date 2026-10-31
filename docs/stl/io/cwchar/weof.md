---
title: WEOF
summary: "ワイド文字の終端またはエラーを表す定数。"
order: 900
tags:
  - 入出力・文字列
---

# WEOF

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`fgetwc` で、ファイルから 1 文字ずつ読んでいくとき、最後の文字を読み終えたあとに何が返るのでしょうか。そのときに返るのが `WEOF` です。ファイルの終わりに達したときと、読み込みでエラーが起きたときの、両方で使われます。`char` 版の `EOF` に当たる、ワイド文字版の定数です。

!!! tip "ポイント"
    - `wint_t` 型の値。`wchar_t` ではない
    - ファイルの終わりとエラーの、両方を表す。どちらかは `feof` と `ferror` で調べる
    - `EOF` とは別の値の場合がある。比べる相手の型に合わせる
    - 比べるときは、`wint_t` の変数と `!= WEOF`

!!! info "このページを読む前に"
    [`std::wint_t`](wint_t.md) を先に読んでください。

## 関数の詳しい説明

### WEOF {#weof}

```cpp
#define WEOF /* wint_t の値（実装定義） */
```

値は処理系が決めます。MSVC では `0xFFFF`、Linux の glibc では `0xFFFFFFFF` です。`EOF`（`-1`）と同じ値とは限らないので、`wint_t` を返す関数の結果は `WEOF` と、`int` を返す関数の結果は `EOF` と、比べます。

ファイルの終わりかエラーかを見分けるには、`feof(stream)` と `ferror(stream)` を呼びます。`WEOF` が返ったあとに調べて、終わりに達しただけなら正常に処理を終え、エラーなら中断します。

```cpp
std::wint_t ch;
while ((ch = std::fgetwc(file)) != WEOF) {
  // 1 文字ずつ処理する
}
if (std::ferror(file)) {
  // 読み込みのエラー
}
```

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  // btowc は、変換できない入力（EOF）に WEOF を返す
  const std::wint_t r = std::btowc(EOF);
  std::println("WEOF が返った: {}", r == WEOF);

  // 通常の文字は WEOF ではない
  std::println("'A' は WEOF ではない: {}", std::btowc('A') != WEOF);
}
```

```text title="実行結果"
WEOF が返った: true
'A' は WEOF ではない: true
```

## ゲームでの使いどころ

低水準のファイル読み込みで、`fgetwc` のループを書くときくらいです。普段は `std::wifstream` を使い、終端の判定をストリームに任せます。

## よくあるミス

??? failure "WEOF と EOF を取り違える"
    ワイド文字を返す関数（`fgetwc`、`btowc`）は `WEOF`、`char` を返す関数（`fgetc`）は `EOF` です。値が違う環境で、比較が成り立ちません。

??? failure "wchar_t に代入してから比べる"
    `wchar_t c = fgetwc(f); if (c == WEOF)` は、`WEOF` が `wchar_t` に収まらない環境で、判定が成り立ちません。`wint_t` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wint_t`](wint_t.md) | `WEOF` を入れられる型 |
| `EOF` | `char` の入出力版 |
| `feof` / `ferror` | 終わりとエラーを区別する |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `WEOF` は、ワイド文字の入出力の、終わり（またはエラー）を表す値
    - [x] `wint_t` の変数と比べる。`EOF` とは別
    - [x] 終わりかエラーかは、`feof` と `ferror` で調べる

## 関連ページ

- [cpprefjp: WEOF](https://cpprefjp.github.io/reference/cwchar/weof.html)
- [cppreference: WEOF](https://en.cppreference.com/w/cpp/string/wide/WEOF)

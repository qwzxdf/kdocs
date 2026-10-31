---
title: std::wctob
summary: "ワイド文字を、1 バイトの文字に変換する。"
order: 900
tags:
  - 入出力・文字列
---

# std::wctob

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`btowc` の逆で、`wchar_t` の 1 文字を、`char` の 1 バイトに戻します。ASCII の範囲なら、ほぼそのまま戻りますが、日本語のように 1 バイトに収まらない文字は、変換できません。変換できたかどうかを、戻り値が `EOF` かで判定します。

!!! tip "ポイント"
    - 現在のロケールで、1 バイトで表せる文字だけが変換できる
    - 変換できないときは `EOF` を返す
    - 戻り値は `int`。変換できたら `unsigned char` の範囲の値
    - 複数バイトになる文字は `wcrtomb`

!!! info "このページを読む前に"
    [`std::btowc`](btowc.md) を先に読んでください。

## 関数の詳しい説明

### std::wctob {#wctob}

```cpp
int wctob(std::wint_t c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | `std::wint_t` | 変換するワイド文字 |

`c` が、現在のロケールで 1 バイトの文字に対応するなら、その `unsigned char` の値を返します。そうでなければ `EOF` を返します。

「1 バイトで表せるか」は、ロケールで決まります。"C" ロケールでは、ASCII の 0〜127 が確実に変換できます。UTF-8 のロケールでは、128 以上のワイド文字は、2〜4 バイトで表されるので、`EOF` になります。

引数が `wint_t` なのは、`WEOF` を渡せるようにするためで、`WEOF` を渡すと `EOF` が返ります。

## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::println("L'A' → 'A': {}", std::wctob(L'A') == 'A');
  std::println("WEOF → EOF: {}", std::wctob(WEOF) == EOF);

  // btowc と組み合わせると、元に戻る
  std::println("往復: {}", std::wctob(std::btowc('Z')) == 'Z');
}
```

```text title="実行結果"
L'A' → 'A': true
WEOF → EOF: true
往復: true
```

## ゲームでの使いどころ

ほとんど使いません。UTF-16 の文字列を `char` の文字列に直すには、1 文字ずつ `wctob` ではなく、`wcsrtombs` か、Windows の `WideCharToMultiByte` を使います。

## よくあるミス

??? failure "EOF を確かめずに char にキャストする"
    `char c = wctob(wc);` では、変換に失敗した `EOF` が、そのまま `char` の `-1` になります。戻り値が `EOF` でないことを確かめます。

??? failure "日本語の 1 文字を変換しようとする"
    日本語は 1 バイトに収まらないので、必ず `EOF` が返ります。`wcrtomb` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`btowc`](btowc.md) | 逆方向の変換 |
| [`wcrtomb`](wcrtomb.md) | 複数バイトの文字にも対応する |
| [`wcsrtombs`](wcsrtombs.md) | 文字列をまとめて変換する |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wctob` は、ワイド文字を 1 バイトの文字に戻す
    - [x] 変換できなければ `EOF`
    - [x] 複数バイトになる文字は `wcrtomb`

## 関連ページ

- [cpprefjp: wctob](https://cpprefjp.github.io/reference/cwchar/wctob.html)
- [cppreference: wctob](https://en.cppreference.com/w/cpp/string/multibyte/wctob)

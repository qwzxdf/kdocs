---
title: std::btowc
summary: "1 バイトの文字を、ワイド文字に変換する。"
order: 900
tags:
  - 入出力・文字列
---

# std::btowc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`char` の 1 文字を、`wchar_t` に変換します。変換できなければ `WEOF` が返ります。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::btowc {#btowc}

```cpp
std::wint_t btowc(int c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | int | 変換する文字（`unsigned char` の値か `EOF`） |

- 戻り値: 変換したワイド文字。できなければ `WEOF`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::println("{}", static_cast<int>(std::btowc('A')));
}
```

```text title="実行結果"
65
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ASCII 文字をワイド文字に直す |

## よくあるミス

??? failure "マルチバイト文字に使う"
    1 バイトで表せる文字だけが対象です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wctob`](wctob.md) | 逆の変換 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 バイトの文字を、ワイド文字に変換する
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::btowc](https://cpprefjp.github.io/reference/cwchar/btowc.html)
- [cppreference: std::btowc](https://en.cppreference.com/w/cpp/string/wide/btowc)

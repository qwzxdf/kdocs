---
title: std::fputwc
summary: "ファイルにワイド文字を 1 文字書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::fputwc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`fputc` の `wchar_t` 版です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::fputwc {#fputwc}

```cpp
std::wint_t fputwc(wchar_t ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | wchar_t | 書く文字 |
| `stream` | FILE* | 書き込み先 |

- 戻り値: 書いた文字。失敗したら `WEOF`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputwc(L'A', f);
  std::rewind(f);
  std::println("{}", static_cast<char>(std::fgetwc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
A
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字を 1 文字ずつ書く |

## よくあるミス

??? failure "戻り値を確かめない"
    失敗したら `WEOF` が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputc`](../cstdio/fputc.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルにワイド文字を 1 文字書く
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fputwc](https://cpprefjp.github.io/reference/cwchar/fputwc.html)
- [cppreference: std::fputwc](https://en.cppreference.com/w/cpp/string/wide/fputwc)

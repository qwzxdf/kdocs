---
title: std::fgetwc
summary: "ファイルからワイド文字を 1 文字読む。"
order: 900
tags:
  - 入出力・文字列
---

# std::fgetwc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`fgetc` の `wchar_t` 版です。終端やエラーのときは `WEOF` が返ります。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::fgetwc {#fgetwc}

```cpp
std::wint_t fgetwc(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 読み込み元 |

- 戻り値: 読んだ文字。終端やエラーなら `WEOF`
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
| 使いどころ | ワイド文字を 1 文字ずつ読む |

## よくあるミス

??? failure "`wchar_t` で受ける"
    `WEOF` との区別のため、`wint_t` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetc`](../cstdio/fgetc.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルからワイド文字を 1 文字読む
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fgetwc](https://cpprefjp.github.io/reference/cwchar/fgetwc.html)
- [cppreference: std::fgetwc](https://en.cppreference.com/w/cpp/string/wide/fgetwc)

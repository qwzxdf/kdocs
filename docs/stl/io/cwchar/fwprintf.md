---
title: std::fwprintf
summary: "書式を指定して、ワイド文字でファイルに出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::fwprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`fprintf` の `wchar_t` 版です。出力先の `FILE*` を指定できます。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::fwprintf {#fwprintf}

```cpp
int fwprintf(std::FILE* stream, const wchar_t* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 出力先 |
| `format` | const wchar_t* | 書式文字列 |
| `...` | 可変引数 | 書式に対応する値 |

- 戻り値: 書き込んだ文字数。失敗したら負の値
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>

int main() {
  std::fwprintf(stdout, L"%d\n", 42);
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字列をファイルに書く |

## よくあるミス

??? failure "`fprintf` と混ぜる"
    ストリームの向きが食い違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fprintf`](../cstdio/fprintf.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式を指定して、ワイド文字でファイルに出力する
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fwprintf](https://cpprefjp.github.io/reference/cwchar/fwprintf.html)
- [cppreference: std::fwprintf](https://en.cppreference.com/w/cpp/string/wide/fwprintf)

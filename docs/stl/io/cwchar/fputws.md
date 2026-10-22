---
title: std::fputws
summary: "ファイルにワイド文字列を書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::fputws

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`fputs` の `wchar_t` 版です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::fputws {#fputws}

```cpp
int fputws(const wchar_t* str, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const wchar_t* | 書く文字列 |
| `stream` | FILE* | 書き込み先 |

- 戻り値: 成功なら負でない値、失敗なら `EOF`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputws(L"abc", f);
  std::rewind(f);
  wchar_t buf[8] = {};
  std::fgetws(buf, 8, f);
  std::println("{}", std::wcslen(buf));
  std::fclose(f);
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字列をファイルに書く |

## よくあるミス

??? failure "改行が付くと思う"
    `fputws` は改行を付けません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputs`](../cstdio/fputs.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルにワイド文字列を書く
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fputws](https://cpprefjp.github.io/reference/cwchar/fputws.html)
- [cppreference: std::fputws](https://en.cppreference.com/w/cpp/string/wide/fputws)

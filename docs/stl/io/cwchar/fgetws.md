---
title: std::fgetws
summary: "ファイルからワイド文字列を 1 行読む。"
order: 900
tags:
  - 入出力・文字列
---

# std::fgetws

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`fgets` の `wchar_t` 版です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::fgetws {#fgetws}

```cpp
wchar_t* fgetws(wchar_t* str, int count, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | wchar_t* | 読み込み先 |
| `count` | int | 読む最大の文字数（終端を含む） |
| `stream` | FILE* | 読み込み元 |

- 戻り値: 成功なら `str`、失敗なら `nullptr`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <cwchar>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputws(L"abc\n", f);
  std::rewind(f);
  wchar_t buf[8];
  std::fgetws(buf, 8, f);
  std::println("{}", std::wcslen(buf));
  std::fclose(f);
}
```

```text title="実行結果"
4
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字列を 1 行読む |

## よくあるミス

??? failure "改行が含まれることを忘れる"
    改行も読み込まれます。長さに 1 含まれます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgets`](../cstdio/fgets.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルからワイド文字列を 1 行読む
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fgetws](https://cpprefjp.github.io/reference/cwchar/fgetws.html)
- [cppreference: std::fgetws](https://en.cppreference.com/w/cpp/string/wide/fgetws)

---
title: std::swprintf
summary: "書式を指定して、ワイド文字の配列に書き込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::swprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`snprintf` の `wchar_t` 版です。大きさを指定するので、あふれにくくなっています。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::swprintf {#swprintf}

```cpp
int swprintf(wchar_t* buffer, std::size_t bufsz, const wchar_t* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | wchar_t* | 書き込み先 |
| `bufsz` | size_t | 書き込める最大の文字数（終端を含む） |
| `format` | const wchar_t* | 書式文字列 |

- 戻り値: 書き込んだ文字数。入りきらなければ負の値
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  wchar_t buf[16];
  int n = std::swprintf(buf, 16, L"%d", 42);
  std::println("{}", n);
}
```

```text title="実行結果"
2
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | Windows API 用のワイド文字列を組み立てる |

## よくあるミス

??? failure "入りきらなくても成功と思う"
    あふれたときは、負の値が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`snprintf`](../cstdio/snprintf.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式を指定して、ワイド文字の配列に書き込む
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::swprintf](https://cpprefjp.github.io/reference/cwchar/swprintf.html)
- [cppreference: std::swprintf](https://en.cppreference.com/w/cpp/string/wide/swprintf)

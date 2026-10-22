---
title: std::wprintf
summary: "書式を指定して、ワイド文字で標準出力に出す。"
order: 900
tags:
  - 入出力・文字列
---

# std::wprintf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`printf` の `wchar_t` 版です。書式文字列も `L"..."` のワイド文字列を使います。1 つのストリームに、ふつうの `printf` とワイドの `wprintf` を混ぜて使うと、向き（orientation）が食い違って、動作しなくなります。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wprintf {#wprintf}

```cpp
int wprintf(const wchar_t* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | const wchar_t* | 書式文字列 |
| `...` | 可変引数 | 書式に対応する値 |

- 戻り値: 書き込んだ文字数。失敗したら負の値
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>

int main() {
  std::wprintf(L"%d\n", 42);
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | Windows のワイド文字列の出力 |

## よくあるミス

??? failure "`printf` と混ぜる"
    向きが食い違い、出力が壊れます。どちらかに統一します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`printf`](../cstdio/printf.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 書式を指定して、ワイド文字で標準出力に出す
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wprintf](https://cpprefjp.github.io/reference/cwchar/wprintf.html)
- [cppreference: std::wprintf](https://en.cppreference.com/w/cpp/string/wide/wprintf)

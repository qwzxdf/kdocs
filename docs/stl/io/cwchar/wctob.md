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

`wchar_t` の 1 文字を `char` に変換します。1 バイトで表せなければ `EOF` が返ります。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wctob {#wctob}

```cpp
int wctob(std::wint_t c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | wint_t | 変換するワイド文字 |

- 戻り値: 変換した 1 バイト。できなければ `EOF`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::println("{}", std::wctob(L'A'));
}
```

```text title="実行結果"
65
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字を ASCII に戻す |

## よくあるミス

??? failure "日本語の文字に使う"
    1 バイトで表せない文字は、`EOF` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`btowc`](btowc.md) | 逆の変換 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字を 1 バイトの文字に変換する
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wctob](https://cpprefjp.github.io/reference/cwchar/wctob.html)
- [cppreference: std::wctob](https://en.cppreference.com/w/cpp/string/wide/wctob)

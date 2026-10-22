---
title: std::wscanf
summary: "ワイド文字で、標準入力から書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::wscanf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`scanf` の `wchar_t` 版です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wscanf {#wscanf}

```cpp
int wscanf(const wchar_t* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | const wchar_t* | 書式文字列 |
| `...` | ポインタ | 読み込んだ値を入れる場所 |

- 戻り値: 読み込めた個数。入力が終わったら `WEOF`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  int n = 0;
  std::wscanf(L"%d", &n);
  std::println("{}", n);
}
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字の入力 |

## よくあるミス

??? failure "`&` を忘れる"
    変数のアドレスを渡さないと、未定義動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`scanf`](../cstdio/scanf.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字で、標準入力から書式を指定して読み込む
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wscanf](https://cpprefjp.github.io/reference/cwchar/wscanf.html)
- [cppreference: std::wscanf](https://en.cppreference.com/w/cpp/string/wide/wscanf)

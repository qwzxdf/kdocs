---
title: std::wcstol
summary: "ワイド文字列を long に変換する。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcstol

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`strtol` の `wchar_t` 版です。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wcstol {#wcstol}

```cpp
long wcstol(const wchar_t* str, wchar_t** str_end, int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | const wchar_t* | 変換する文字列 |
| `str_end` | wchar_t** | 読み終えた位置を受け取る（不要なら `nullptr`） |
| `base` | int | 進数 |

- 戻り値: 変換した値
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  std::println("{}", std::wcstol(L"42", nullptr, 10));
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | Windows API から来た文字列を数値にする |

## よくあるミス

??? failure "範囲外を確かめない"
    範囲外のとき、`errno` が `ERANGE` になります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`strtol`](../../numeric/cstdlib/strtol.md) | char 版 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字列を long に変換する
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wcstol](https://cpprefjp.github.io/reference/cwchar/wcstol.html)
- [cppreference: std::wcstol](https://en.cppreference.com/w/cpp/string/wide/wcstol)

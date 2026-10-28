---
title: std::wmemcpy
summary: "ワイド文字の配列を、指定した個数だけコピーする。"
order: 900
tags:
  - 入出力・文字列
---

# std::wmemcpy

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

`memcpy` の `wchar_t` 版です。バイト数ではなく、**文字数**で指定します。

!!! tip "ポイント"
    - `wchar_t`（ワイド文字）版の C の関数。
    - `char` 版は `<cstdio>`・`<cstring>`・`<cstdlib>`。
    - Windows の API でよく使われる。

!!! info "このページを読む前に"
    [文字コード](../../../encoding/index.md) の考え方を先に読んでください。

## 関数の詳しい説明

### std::wmemcpy {#wmemcpy}

```cpp
wchar_t* wmemcpy(wchar_t* dest, const wchar_t* src, std::size_t count);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `dest` | wchar_t* | コピー先 |
| `src` | const wchar_t* | コピー元 |
| `count` | size_t | コピーする文字数 |

- 戻り値: `dest`
- 計算量: 文字数に比例


## 実際に動かしてみる

```cpp
#include <cwchar>
#include <print>

int main() {
  wchar_t dst[4] = {};
  std::wmemcpy(dst, L"abc", 3);
  std::println("{}", std::wcslen(dst));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ワイド文字の配列のコピー |

## よくあるミス

??? failure "バイト数で指定する"
    `wmemcpy` は文字数です。`sizeof` で渡すと大きすぎます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`memcpy`](../../memory/cstring/memcpy.md) | バイト単位 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ワイド文字の配列を指定した個数だけコピーする
    - [x] `wchar_t`（ワイド文字）版の C の関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::wmemcpy](https://cpprefjp.github.io/reference/cwchar/wmemcpy.html)
- [cppreference: std::wmemcpy](https://en.cppreference.com/w/cpp/string/wide/wmemcpy)

---
title: <cuchar>
summary: "マルチバイト文字と UTF-8 / 16 / 32 の変換をする C 由来の関数群。"
order: 100
tags:
  - 入出力・文字列
---

# <cuchar>

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11〜</span>
`#include <cuchar>`
</div>

`<cuchar>` には、`mbrtoc16`・`c16rtomb`・`mbrtoc32`・`c32rtomb` など、マルチバイト文字と `char16_t` / `char32_t` を行き来する関数があります。UTF-8 から UTF-32 への 1 文字ずつの変換などに使えますが、ロケールに依存します。C++23 で `char8_t` 版（`mbrtoc8`・`c8rtomb`）が加わりました。

!!! tip "ポイント"
    - `mbrtoc32` は、マルチバイトから UTF-32 の 1 文字へ。
    - 現在のロケールに依存する。
    - C++23 で `char8_t` 版が追加。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### mbrtoc32 {#mbrtoc32}

```cpp
size_t mbrtoc32(char32_t* pc32, const char* s, size_t n, mbstate_t* ps);
```

| 引数 | 意味 |
| --- | --- |
| `pc32` | 結果の 1 文字 |
| `s` | 入力のバイト列 |
| `n` | 読む最大バイト数 |
| `ps` | 変換の状態 |

- 読み取ったバイト数、または特別な値 `(size_t)-1` `(size_t)-2` `(size_t)-3` を返します

## 実際に動かしてみる

```cpp
#include <cstdint>
#include <cuchar>
#include <iostream>

int main() {
  std::mbstate_t st{};
  char32_t c;
  std::size_t n = std::mbrtoc32(&c, "A", 1, &st);
  std::cout << n << " " << static_cast<std::uint32_t>(c) << "\n";
}
```

```text title="実行結果"
1 65
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 1 文字ずつ UTF-32 に直す | `std::mbrtoc32` |

## よくあるミス

??? failure "ロケールが UTF-8 でない"
    既定の "C" ロケールでは、UTF-8 の多バイト文字を正しく読めません。`setlocale` が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [文字コード](../../encoding/index.md) | 変換の考え方 |

## コンパイラ対応

C++11 から使えます。`char8_t` 版は C++23 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] マルチバイトと UTF-16 / 32 を変換する。
    - [x] ロケールに依存する。
    - [x] `char8_t` 版は C++23。

## 関連ページ

- [cpprefjp: mbrtoc32](https://cpprefjp.github.io/reference/cuchar/index.html)
- [cppreference: mbrtoc32](https://en.cppreference.com/w/cpp/header/cuchar)

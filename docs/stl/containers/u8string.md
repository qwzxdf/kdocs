---
title: std::u8string
summary: "`char8_t` を文字の型にもつ文字列。"
order: 900
tags:
  - コンテナ
---

# std::u8string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <string>`
</div>

`std::u8string` は、`char8_t` の文字列で、UTF-8 であることを型で表す文字列です。C++20 で追加された `char8_t` を要素にした `basic_string<char8_t>` の別名です。`u8"..."` のリテラルが、この型になります。

!!! tip "ポイント"
    - `basic_string<char8_t>` の別名。C++20
    - `u8"..."` のリテラルは `const char8_t[]`
    - `std::string` とは別の型。暗黙に変換できない
    - 既存の API は `char` が前提なので、橋渡しが要る

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::u8string {#u8string}

<span class="ver ver-20">C++20</span>

```cpp
using u8string = basic_string<char8_t>;
```

`char8_t` は、`char` の別名ではなく、独立した型です。UTF-8 であることが型で分かる利点がありますが、`std::println`、`fopen`、`std::filesystem::path`（一部）など、`char` を前提にした API に渡すには、`reinterpret_cast` などが要ります。

そのため、実用上は、UTF-8 の `std::string` と、ソース ファイルの UTF-8（MSVC の `/utf-8`）で済ませることが多いです。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  const std::u8string s = u8"あいう";
  std::println("バイト数: {}", s.size());

  // char として見直す
  const std::string c(reinterpret_cast<const char*>(s.data()), s.size());
  std::println("{}", c);
}
```

```text title="実行結果"
バイト数: 9
あいう
```

## ゲームでの使いどころ

UTF-8 を型で明示したいライブラリを書くときに使います。普段は `std::string` です。

## よくあるミス

??? failure "char の API に直接渡す"
    型が違います。変換が要ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`string`](string.md) | ふつうの UTF-8 はこちら |
| [`u16string`](u16string.md) | UTF-16 |
| [`u32string`](u32string.md) | UTF-32 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::u8string](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::u8string](https://en.cppreference.com/w/cpp/string/basic_string)

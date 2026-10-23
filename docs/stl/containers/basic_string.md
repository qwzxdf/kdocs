---
title: std::basic_string
summary: "文字列クラスの正体。char 以外の文字型（wchar_t、char8_t など）にも使える。"
order: 28
tags:
  - コンテナ
---

# std::basic_string

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
<span class="perf perf-3">○ 普通</span>
<span class="ver ver-11">C++98〜</span>
`#include <string>`
</div>

Windows API の W 版に渡す文字列は `wchar_t` の並びで、UTF-8 を型で区別したいなら `char8_t` の並びです。`std::string` だけでは、これらを扱えません。`std::basic_string<CharT>` は、文字列クラスの本体で、`std::string` は `basic_string<char>` の別名です。`std::wstring`、`std::u8string`、`std::u16string` なども、すべてこのクラスから作られます。

!!! tip "ポイント"
    - 普段は `std::string` で足りる。このページは「ほかの種類の文字列」を知るためのもの。
    - Windows API（W 版）に渡すなら `std::wstring`。UTF-16 を直接扱うなら `std::u16string`。
    - UTF-8 を**型で区別したい**なら `std::u8string`（C++20）。ただし、標準ライブラリの入出力は対応しきれていない。

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 文字列の種類

| 型 | 文字の型 | 用途 |
| --- | --- | --- |
| [`std::string`](string.md) | `char` | 普通の文字列。UTF-8 で使うのが基本 |
| `std::wstring` | `wchar_t` | Windows API（W 版）。UTF-16（Windows）または UTF-32（Linux） |
| `std::u8string` | `char8_t` | UTF-8 を型で区別したいとき（C++20） |
| `std::u16string` | `char16_t` | UTF-16 |
| `std::u32string` | `char32_t` | UTF-32（1 要素が 1 コードポイント） |

## 宣言

```cpp
template <class CharT, class Traits = std::char_traits<CharT>, class Allocator = std::allocator<CharT>>
class basic_string;
```

## 関数の詳しい説明

### size {#size}

```cpp
size_type size() const noexcept;
```

- 戻り値: 要素の数。`char` なら**バイト数**、`char32_t` なら**文字数**に近い
- 計算量: O(1)

```cpp
#include <print>
#include <string>

int main() {
  std::u8string u8 = u8"こんにちは";   // UTF-8 のバイト列（char8_t）
  std::u16string u16 = u"こんにちは";   // UTF-16
  std::u32string u32 = U"こんにちは";   // UTF-32（1 要素 = 1 文字）

  std::println("u8: {} / u16: {} / u32: {}", u8.size(), u16.size(), u32.size());
}
```

```text title="実行結果"
u8: 15 / u16: 5 / u32: 5
```

## ゲームでの使いどころ

Windows API を呼ぶとき、パスや名前を `std::wstring` で受け渡します。`CreateFileW` や `MessageBoxW` などの W 版の関数に渡す文字列がこの型です。標準の文字列と W 版の変換には、`MultiByteToWideChar` を使います。

UTF-8 を型として区別したいときは、`std::u8string` を使います。ただし、標準ライブラリの対応がまだ薄く、`std::cout` に直接出せないなど、扱いにくい面があります。ゲームでは、内部は `std::string` の UTF-8 で統一し、Windows API の境界でだけ `wstring` に変換する構成が現実的です。

`basic_string` を直接書くことは、ほとんどありません。独自の `char_traits` で大文字小文字を区別しない文字列を作る、といった特殊な場面だけです。

## よくあるミス

??? failure "size() が「文字数」だと思う"
    `std::string`（UTF-8）の `size()` はバイト数です。「こんにちは」は 15 です。文字数を数えるには、UTF-32 に変換するか、専用のライブラリを使います。

??? failure "wchar_t の大きさが環境で違う"
    `wchar_t` は Windows では 2 バイト（UTF-16）、Linux では 4 バイト（UTF-32）です。環境をまたぐコードでは `char8_t` / `char16_t` / `char32_t` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::string`](string.md) | `basic_string<char>`。普段はこれ |
| [`std::string_view`](../utilities/string_view.md) | 文字列を「見る」だけ。`basic_string_view` の別名 |
| 文字コード（[encoding](../../encoding/index.md)） | UTF-8 / UTF-16 / UTF-32 の違い |

## コンパイラ対応

`std::string` と `std::wstring` は C++98、`u16string` / `u32string` は C++11、`u8string` は C++20 です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::string` は `basic_string<char>`
    - [x] `wstring` / `u8string` / `u16string` / `u32string` がある
    - [x] `size()` は要素数であって、文字数ではない

## 関連ページ

- [cpprefjp: std::basic_string](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::basic_string](https://en.cppreference.com/w/cpp/string/basic_string)

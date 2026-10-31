---
title: std::u8string_view
summary: "`char8_t` を文字の型にもつ、文字列を借りて見るだけの型。"
order: 900
tags:
  - ユーティリティ
---

# std::u8string_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <string_view>`
</div>

`std::u8string_view` は、`char8_t` の文字列を所有せずに見る型です。`char8_t` は、UTF-8 であることを型で表したもので、C++20 から使えます。`u8"あ"` のリテラルの型が `const char8_t[]` になったため、それを見るために必要です。

!!! tip "ポイント"
    - `basic_string_view<char8_t>` の別名。C++20
    - UTF-8 であることを型で示す
    - `u8"..."` のリテラルは、`const char8_t[]`（C++20 以降）
    - `char` の `string_view` とは、暗黙に変換できない

!!! info "このページを読む前に"
    [`std::basic_string_view`](basic_string_view.md) と [文字コード](../../encoding/index.md)を先に読んでください。

## 関数の詳しい説明

### std::u8string_view {#u8string_view}

<span class="ver ver-20">C++20</span>

```cpp
using u8string_view = basic_string_view<char8_t>;
```

`char` の `string_view` と型が別なので、`std::println` に直接渡せません。`char` として解釈し直す必要があります。

```cpp
std::u8string_view u8 = u8"あ";
std::string_view s(reinterpret_cast<const char*>(u8.data()), u8.size());
```

C++20 の `char8_t` は、`char` の別名ではありません。UTF-8 の文字列を、型で区別できる利点はありますが、既存の API は `char` を前提にしているものが多く、橋渡しの `reinterpret_cast` が必要になります。

`u8string_view` の `size()` は、UTF-8 のバイト数です。「あ」は 3 です。

## 実際に動かしてみる

```cpp
#include <print>
#include <string_view>

int main() {
  const std::u8string_view v = u8"あいう";
  std::println("バイト数: {}", v.size());

  // char として見直す（reinterpret_cast）
  const std::string_view s(reinterpret_cast<const char*>(v.data()), v.size());
  std::println("{}", s);

  static_assert(!std::is_same_v<std::u8string_view, std::string_view>);
}
```

```text title="実行結果"
バイト数: 9
あいう
```

## ゲームでの使いどころ

UTF-8 の文字列を、型で明示したいライブラリを書くときに使います。普段は `char` の `string_view` と UTF-8 のソース ファイルで足ります。

## よくあるミス

??? failure "char の API に直接渡す"
    型が違うのでコンパイルできません。橋渡しの `reinterpret_cast` が要ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::string_view`](string_view.md) | `char` 版。ふつうの UTF-8 はこちら |
| [`u16string_view`](u16string_view.md) | UTF-16 |
| [`u32string_view`](u32string_view.md) | UTF-32 |

## コンパイラ対応

C++20 から使えます。

## 関連ページ

- [cpprefjp: std::u8string_view](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)
- [cppreference: std::u8string_view](https://en.cppreference.com/w/cpp/string/basic_string_view)

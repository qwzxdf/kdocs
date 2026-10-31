---
title: std::u16string
summary: "`char16_t` を文字の型にもつ文字列。"
order: 900
tags:
  - コンテナ
---

# std::u16string

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::u16string` は、`char16_t` の文字列で、UTF-16 を表します。`wchar_t` と違い、全環境で 16 ビットと決まっているので、UTF-16 を扱う API（ICU など）との橋渡しに向いています。

!!! tip "ポイント"
    - `basic_string<char16_t>` の別名
    - リテラルは `u"..."`
    - 基本多言語面の外の文字は、2 要素のサロゲート ペア
    - Windows の `wstring` とは別の型

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::u16string {#u16string}

<span class="ver ver-11">C++11</span>

```cpp
using u16string = basic_string<char16_t>;
```

`size()` は、文字数ではなく、UTF-16 の要素（16 ビット）の数です。絵文字は 2 になります。

Windows では、`wchar_t` と `char16_t` は同じ大きさ（16 ビット）ですが、別の型です。Windows API に渡すときは、`reinterpret_cast<const wchar_t*>` で橋渡しします。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  const std::u16string a = u"あ";
  const std::u16string b = u"😀";
  std::println("「あ」: {} 要素", a.size());
  std::println("絵文字: {} 要素", b.size());
}
```

```text title="実行結果"
「あ」: 1 要素
絵文字: 2 要素
```

## ゲームでの使いどころ

UTF-16 のライブラリとやりとりするときだけ使います。

## よくあるミス

??? failure "size() を文字数と思う"
    絵文字は 2 要素です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wstring`](wstring.md) | `wchar_t` 版 |
| [`u8string`](u8string.md) | UTF-8 |
| [`u32string`](u32string.md) | UTF-32 |

## コンパイラ対応

C++11 から使えます。

## 関連ページ

- [cpprefjp: std::u16string](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::u16string](https://en.cppreference.com/w/cpp/string/basic_string)

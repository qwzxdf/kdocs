---
title: std::u16string_view
summary: "`char16_t` を文字の型にもつ、文字列を借りて見るだけの型。"
order: 900
tags:
  - ユーティリティ
---

# std::u16string_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <string_view>`
</div>

`std::u16string_view` は、`char16_t` の文字列を所有せずに見る型です。`char16_t` は UTF-16 の 1 単位を表す型で、環境によらず 16 ビットです。`wchar_t` と違い、全環境で UTF-16 と決まっています。

!!! tip "ポイント"
    - `basic_string_view<char16_t>` の別名
    - UTF-16 の 1 要素 = 16 ビット。環境によらない
    - 基本多言語面の外の文字は、2 要素（サロゲート ペア）
    - リテラルは `u"..."`

!!! info "このページを読む前に"
    [`std::basic_string_view`](basic_string_view.md) を先に読んでください。

## 関数の詳しい説明

### std::u16string_view {#u16string_view}

<span class="ver ver-17">C++17</span>

```cpp
using u16string_view = basic_string_view<char16_t>;
```

日本語の多くの文字（「あ」など）は 1 要素ですが、絵文字などは 2 要素になります。`size()` は文字数ではなく、要素数です。

Windows の `wchar_t` も UTF-16 ですが、型は `wchar_t` で、`char16_t` とは別の型です。変換には `reinterpret_cast` が要ります（Windows では同じ大きさです）。

## 実際に動かしてみる

```cpp
#include <print>
#include <string_view>

int main() {
  const std::u16string_view a = u"あ";
  const std::u16string_view b = u"😀";

  std::println("「あ」: {} 要素", a.size());
  std::println("絵文字: {} 要素（サロゲート ペア）", b.size());
  std::println("先頭は高位サロゲート: {}", b[0] >= 0xD800 && b[0] <= 0xDBFF);
}
```

```text title="実行結果"
「あ」: 1 要素
絵文字: 2 要素（サロゲート ペア）
先頭は高位サロゲート: true
```

## ゲームでの使いどころ

UTF-16 を扱う API（ICU など）に渡す文字列を、型で明示するときに使います。

## よくあるミス

??? failure "size() を文字数だと思う"
    絵文字は 2 要素です。文字数を数えるなら、サロゲート ペアを考慮します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`wstring_view`](wstring_view.md) | `wchar_t` 版。大きさが環境で違う |
| [`u8string_view`](u8string_view.md) | UTF-8 |
| [`u32string_view`](u32string_view.md) | UTF-32 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::u16string_view](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)
- [cppreference: std::u16string_view](https://en.cppreference.com/w/cpp/string/basic_string_view)

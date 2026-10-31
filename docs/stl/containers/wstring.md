---
title: std::wstring
summary: "`wchar_t` を文字の型にもつ文字列。"
order: 900
tags:
  - コンテナ
---

# std::wstring

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <string>`
</div>

`std::wstring` は、`wchar_t` の文字列で、`std::basic_string<wchar_t>` の別名です。Windows API が `wchar_t`（UTF-16）の文字列を要求するので、API の境界で使います。ゲームの内部では、UTF-8 の `std::string` にそろえ、API の直前で `wstring` に変換するのが標準的な作りです。

!!! tip "ポイント"
    - `basic_string<wchar_t>` の別名
    - Windows では UTF-16、Linux では UTF-32
    - `std::string` と同じメンバー関数が使える
    - `std::println` には直接渡せない

!!! info "このページを読む前に"
    [`std::string`](string.md) を先に読んでください。

## 関数の詳しい説明

### std::wstring {#wstring}

<span class="ver ver-11">C++11</span>

```cpp
using wstring = basic_string<wchar_t>;
```

リテラルは `L"..."` です。`std::wstring_view` が、所有しない版です。

`wchar_t` の大きさが環境で違うので、`size()` の意味が変わります。Windows の絵文字は、サロゲート ペアで 2 要素です。

`std::string` との変換は、標準では面倒です（`codecvt` は非推奨）。Windows では `MultiByteToWideChar(CP_UTF8, ...)` と `WideCharToMultiByte(CP_UTF8, ...)` を使います。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>

int main() {
  std::wstring name = L"Hero";
  name += L" the Brave";
  std::println("長さ: {}", name.size());
  std::println("一致: {}", name == L"Hero the Brave");
  std::println("検索: {}", name.find(L"the"));
}
```

```text title="実行結果"
長さ: 14
一致: true
検索: 5
```

## ゲームでの使いどころ

Windows API に渡すパスやタイトルを扱うときに使います。内部は UTF-8 の `std::string` です。

## よくあるミス

??? failure "内部の文字列を wstring で持つ"
    外部とのやり取りに変換が要り、混在します。UTF-8 にそろえます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`string`](string.md) | `char` 版 |
| [`u16string`](u16string.md) | UTF-16 を明示する |
| [`to_wstring`](to_wstring.md) | 数値から作る |

## コンパイラ対応

C++98 から使えます。

## 関連ページ

- [cpprefjp: std::wstring](https://cpprefjp.github.io/reference/string/basic_string.html)
- [cppreference: std::wstring](https://en.cppreference.com/w/cpp/string/basic_string)

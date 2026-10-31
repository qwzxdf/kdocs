---
title: std::wstring_view
summary: "`wchar_t` を文字の型にもつ、文字列を借りて見るだけの型。"
order: 900
tags:
  - ユーティリティ
---

# std::wstring_view

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-17">C++17</span>
`#include <string_view>`
</div>

`std::wstring_view` は、`wchar_t` の文字列を、所有せずに見る型です。`basic_string_view<wchar_t>` の別名で、Windows API が返した `wchar_t*` の文字列を、コピーせずに扱うときに使います。

!!! tip "ポイント"
    - `basic_string_view<wchar_t>` の別名
    - `std::wstring`、`L"..."`、`const wchar_t*` から作れる
    - Windows の `wchar_t` は UTF-16。`size()` は UTF-16 の要素数
    - ゲームの内部の文字列は UTF-8 の `string_view`

!!! info "このページを読む前に"
    [`std::basic_string_view`](basic_string_view.md) を先に読んでください。

## 関数の詳しい説明

### std::wstring_view {#wstring_view}

<span class="ver ver-17">C++17</span>

```cpp
using wstring_view = basic_string_view<wchar_t>;
```

機能は `string_view` と同じです。`wchar_t` の大きさが環境で違う（Windows は 16 ビット、Linux は 32 ビット）ので、1 文字の数え方が変わります。基本多言語面の外の文字（多くの絵文字）は、Windows では 2 要素のサロゲート ペアです。

`std::wstring_view` を `std::wstring` に変換するときは、コンストラクターを明示的に呼びます（`std::wstring(sv)`）。暗黙の変換はできません。

## 実際に動かしてみる

```cpp
#include <print>
#include <string>
#include <string_view>

int main() {
  const std::wstring name = L"Hero";
  std::wstring_view v = name;

  std::println("長さ: {}", v.size());
  std::println("先頭 2 文字が He: {}", v.substr(0, 2) == L"He");
  std::println("Hero で始まる: {}", v.starts_with(L"He"));

  // wstring に戻すときは明示する
  const std::wstring copy(v);
  std::println("コピーは同じ内容: {}", copy == name);
}
```

```text title="実行結果"
長さ: 4
先頭 2 文字が He: true
Hero で始まる: true
コピーは同じ内容: true
```

## ゲームでの使いどころ

Windows API から受け取ったパスやタイトルを、コピーせずに検査するときに使います。

## よくあるミス

??? failure "wstring_view を wstring に暗黙に変換しようとする"
    暗黙の変換はありません。`std::wstring(sv)` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`basic_string_view`](basic_string_view.md) | 元のテンプレート |
| [`std::string_view`](string_view.md) | `char` 版 |
| [`u16string_view`](u16string_view.md) | UTF-16 を明示する型 |

## コンパイラ対応

C++17 から使えます。

## 関連ページ

- [cpprefjp: std::wstring_view](https://cpprefjp.github.io/reference/string_view/basic_string_view.html)
- [cppreference: std::wstring_view](https://en.cppreference.com/w/cpp/string/basic_string_view)

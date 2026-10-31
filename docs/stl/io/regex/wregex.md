---
title: std::wregex
summary: "`wchar_t` 用の正規表現。"
order: 900
tags:
  - 入出力・文字列
---

# std::wregex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

Windows の API から受け取った `wchar_t` の文字列を、そのまま正規表現で検索したいときに使うのが `std::wregex` です。`std::regex` の `wchar_t` 版で、パターンも `L"..."` で書きます。使い方は `regex` と同じで、結果を受け取る型も、`wsmatch` や `wcmatch` のように、`w` が付きます。

!!! tip "ポイント"
    - `basic_regex<wchar_t>` の別名。パターンも検索対象も `wchar_t`
    - 結果は `wsmatch`（`wstring` 用）か `wcmatch`（`const wchar_t*` 用）で受ける
    - Windows の `wchar_t` は UTF-16。サロゲート ペアは 1 文字として扱われない
    - ゲームでは、UTF-8 の `char` と `std::regex` のほうが扱いやすい

!!! info "このページを読む前に"
    [`std::basic_regex`](basic_regex.md) を先に読んでください。

## 関数の詳しい説明

### std::wregex {#wregex}

```cpp
using wregex = basic_regex<wchar_t>;
```

使い方は `std::regex` と同じです。パターンと検索対象を、`wchar_t` の文字列にします。

`\d`、`\w`、`\s` などの文字クラスの判定は、`wchar_t` ごとに行われます。全角の数字や、日本語の文字が `\w` に含まれるかは、ロケールと実装によって違います。日本語の文字を含む文字列を検索するときは、パターンに文字そのものを書くか、範囲（`[ぁ-ん]`）を指定します。

UTF-16 では、基本多言語面の外の文字（多くの絵文字）は、2 つの `wchar_t`（サロゲート ペア）で表されます。`wregex` は、これを 2 文字として扱うので、`.` が絵文字 1 つにマッチしない場合があります。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  const std::wregex re(L"\\d+");
  std::println("123 に全体一致: {}", std::regex_match(L"123", re));
  std::println("abc に全体一致: {}", std::regex_match(L"abc", re));

  const std::wstring text = L"HP 30 MP 12";
  std::wsmatch m;
  std::regex_search(text, m, re);
  std::println("最初の数字の位置: {}", m.position());
}
```

```text title="実行結果"
123 に全体一致: true
abc に全体一致: false
最初の数字の位置: 3
```

## ゲームでの使いどころ

Windows API から受け取ったパスや名前を、`wchar_t` のまま検査するときに使えます。内部の文字列を UTF-8 に統一していれば、`std::regex` で足ります。

## よくあるミス

??? failure "パターンを char の文字列で書く"
    `std::wregex re("\\d+")` はコンパイルできません。`L"..."` で書きます。

??? failure "wregex に std::string を渡す"
    型が合いません。`std::wstring` を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::regex`](../regex.md) | `char` 用 |
| [`std::wsmatch`](wsmatch.md) | `wstring` 用の結果の型 |
| [`std::wcmatch`](wcmatch.md) | `const wchar_t*` 用の結果の型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wregex` は、`wchar_t` 用の正規表現
    - [x] パターンは `L"..."`、結果は `wsmatch` / `wcmatch`
    - [x] ゲームでは `char` の UTF-8 と `regex`

## 関連ページ

- [cpprefjp: wregex](https://cpprefjp.github.io/reference/regex/wregex.html)
- [cppreference: std::wregex](https://en.cppreference.com/w/cpp/regex/basic_regex)

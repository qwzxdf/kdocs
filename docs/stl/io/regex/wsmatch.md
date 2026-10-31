---
title: std::wsmatch
summary: "wstring 用の match_results。"
order: 900
tags:
  - 入出力・文字列
---

# std::wsmatch

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::wstring` を検索した結果を入れる型が `std::wsmatch` です。`smatch` の `wchar_t` 版で、`match_results<std::wstring::const_iterator>` の別名です。パターンは `std::wregex` で書き、`m[n]` は `std::wssub_match` になります。

!!! tip "ポイント"
    - `match_results<std::wstring::const_iterator>` の別名
    - 検索対象は `std::wstring`。名前のある変数にする
    - パターンは `std::wregex`
    - `const wchar_t*` を検索するなら `std::wcmatch`

!!! info "このページを読む前に"
    [`std::smatch`](../smatch.md) と [`std::wregex`](wregex.md) を先に読んでください。

## 関数の詳しい説明

### std::wsmatch {#wsmatch}

```cpp
using wsmatch = match_results<std::wstring::const_iterator>;
```

機能は `smatch` と同じです。`m[n]`、`m.size()`、`m.prefix()`、`m.suffix()`、`m.position(n)` が使えます。

`std::regex_search` に渡す `std::wstring` は、一時オブジェクトではなく、名前のある変数にします。一時オブジェクトを渡すと、結果が破棄された文字列を指してしまうため、コンパイル エラーになります。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  const std::wstring text = L"HP 30 MP 12";
  const std::wregex re(L"(\\w+) (\\d+)");

  std::wsmatch m;
  if (std::regex_search(text, m, re)) {
    std::println("size={}", m.size());
    std::println("位置: {}  数値は '30': {}", m.position(0), m[2].str() == L"30");
    std::println("後ろの長さ: {}", m.suffix().length());
  }
}
```

```text title="実行結果"
size=3
位置: 0  数値は '30': true
後ろの長さ: 6
```

`suffix()` は、最初の一致の後ろの ` MP 12`（6 文字）です。

## ゲームでの使いどころ

`wchar_t` の文字列を扱う Windows 向けのコードで、検索結果を取り出すときに使います。

## よくあるミス

??? failure "wstring の一時オブジェクトを検索する"
    `regex_search(GetTitle(), m, re)` は、コンパイルできません。変数に入れてから検索します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::smatch`](../smatch.md) | `std::string` 用 |
| [`std::wcmatch`](wcmatch.md) | `const wchar_t*` 用 |
| [`std::wregex`](wregex.md) | 対になる正規表現の型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wsmatch` は、`std::wstring` を検索した結果を入れる型
    - [x] パターンは `wregex`、検索対象は名前のある変数
    - [x] `const wchar_t*` なら `wcmatch`

## 関連ページ

- [cpprefjp: wsmatch](https://cpprefjp.github.io/reference/regex/wsmatch.html)
- [cppreference: std::wsmatch](https://en.cppreference.com/w/cpp/regex/match_results)

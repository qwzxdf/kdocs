---
title: std::wcmatch
summary: "wchar_t の C 文字列用の match_results。"
order: 900
tags:
  - 入出力・文字列
---

# std::wcmatch

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`const wchar_t*` のワイド文字列を検索した結果を入れる型が `std::wcmatch` です。`cmatch` の `wchar_t` 版で、`match_results<const wchar_t*>` の別名です。パターンは `std::wregex` で書き、`m[n]` は `std::wcsub_match` になります。

!!! tip "ポイント"
    - `match_results<const wchar_t*>` の別名
    - 検索対象は `L"..."` や、`const wchar_t*`
    - パターンは `std::wregex`
    - `std::wstring` を検索するなら `std::wsmatch`

!!! info "このページを読む前に"
    [`std::cmatch`](cmatch.md) と [`std::wregex`](wregex.md) を先に読んでください。

## 関数の詳しい説明

### std::wcmatch {#wcmatch}

```cpp
using wcmatch = match_results<const wchar_t*>;
```

使い方は `cmatch` と同じです。違いは、文字の型が `wchar_t` であることだけです。`m[n].str()` は `std::wstring` を返します。

`std::println` は `std::wstring` を直接表示できないので、表示するときは、UTF-8 に変換するか、`std::wcout` を使います。この環境で動作を確かめるときは、長さや比較の結果を出力します。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  const wchar_t* s = L"x=5";
  std::wcmatch m;
  const std::wregex re(L"(\\w)=(\\d)");

  if (std::regex_search(s, m, re)) {
    std::println("size={}", m.size());
    std::println("値は '5': {}", m[2].str() == L"5");
  }
}
```

```text title="実行結果"
size=3
値は '5': true
```

`m[2].str()` は `std::wstring` なので、`L"5"` と比べています。

## ゲームでの使いどころ

Windows API が返した `wchar_t*` の文字列を、コピーせずに検査するときに使えます。

## よくあるミス

??? failure "std::println に wstring を渡す"
    書式つき出力は、`wchar_t` の文字列を直接は表示できません。UTF-8 の文字列に変換してから出します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::cmatch`](cmatch.md) | `const char*` 用 |
| [`std::wsmatch`](wsmatch.md) | `std::wstring` 用 |
| [`std::wregex`](wregex.md) | 対になる正規表現の型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wcmatch` は、`const wchar_t*` を検索した結果を入れる型
    - [x] パターンは `wregex`
    - [x] `std::wstring` なら `wsmatch`

## 関連ページ

- [cpprefjp: wcmatch](https://cpprefjp.github.io/reference/regex/wcmatch.html)
- [cppreference: std::wcmatch](https://en.cppreference.com/w/cpp/regex/match_results)

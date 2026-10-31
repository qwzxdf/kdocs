---
title: std::cregex_iterator
summary: "C 文字列から、正規表現に一致する部分を順に取り出すイテレータ。"
order: 900
tags:
  - 入出力・文字列
---

# std::cregex_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::sregex_iterator` が `std::string` 用なのに対し、`const char*` の C 文字列用の別名が `std::cregex_iterator` です。`regex_iterator<const char*>` の別名で、一致は `std::cmatch` として得られます。

!!! tip "ポイント"
    - `regex_iterator<const char*>` の別名
    - 範囲は、先頭のポインタと、終端のポインタ（`s + std::strlen(s)`）で渡す
    - `*it` は `std::cmatch`
    - `std::string` を検索するなら `std::sregex_iterator`

!!! info "このページを読む前に"
    [`std::regex_iterator`](regex_iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::cregex_iterator {#cregex_iterator}

```cpp
using cregex_iterator = regex_iterator<const char*>;
```

使い方は `regex_iterator` と同じです。範囲を `std::string` のイテレータではなく、`const char*` のポインタで渡します。終端は、`s + std::strlen(s)` のようにして求めます。

`std::string_view` を検索したいときにも使えます。`sv.data()` と `sv.data() + sv.size()` を範囲として渡します。`std::string_view` 用の専用の別名は、標準にはありません。

## 実際に動かしてみる

```cpp
#include <cstring>
#include <iterator>
#include <print>
#include <regex>

int main() {
  const char* s = "a1b22c333";
  const std::regex re(R"(\d+)");

  std::cregex_iterator it(s, s + std::strlen(s), re);
  const std::cregex_iterator end;
  std::println("一致の個数: {}", std::distance(it, end));

  for (; it != end; ++it) {
    std::println("{}", it->str());
  }
}
```

```text title="実行結果"
一致の個数: 3
1
22
333
```

## ゲームでの使いどころ

`std::string_view` で持っているテキスト（読み込んだファイルの中身など）を、コピーせずに検索したいときに使えます。

## よくあるミス

??? failure "終端を忘れる"
    `std::cregex_iterator it(s, re)` のような書き方はありません。範囲を、2 つのポインタで渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex_iterator`](regex_iterator.md) | 元のテンプレート |
| [`std::sregex_iterator`](../sregex_iterator.md) | `std::string` 用 |
| [`std::cmatch`](cmatch.md) | 取り出す一致の型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `cregex_iterator` は、`const char*` を検索して、一致を順に取り出す
    - [x] 範囲は、2 つのポインタで渡す
    - [x] `string_view` の検索にも使える

## 関連ページ

- [cpprefjp: cregex_iterator](https://cpprefjp.github.io/reference/regex/cregex_iterator.html)
- [cppreference: std::cregex_iterator](https://en.cppreference.com/w/cpp/regex/regex_iterator)

---
title: std::sregex_token_iterator
summary: "string 用の regex_token_iterator。"
order: 900
tags:
  - 入出力・文字列
---

# std::sregex_token_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::string` を検索対象にした `regex_token_iterator` の別名が、`std::sregex_token_iterator` です。`regex_token_iterator<std::string::const_iterator>` で、分割や、グループの取り出しに使います。型名が短くなるだけで、機能は変わりません。

!!! tip "ポイント"
    - `regex_token_iterator<std::string::const_iterator>` の別名
    - 範囲は `s.begin()` と `s.end()`。`s` は名前のある変数にする
    - `std::distance` で、要素の個数を数えられる
    - `const char*` なら `std::cregex_token_iterator`

!!! info "このページを読む前に"
    [`std::regex_token_iterator`](regex_token_iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::sregex_token_iterator {#sregex_token_iterator}

```cpp
using sregex_token_iterator = regex_token_iterator<std::string::const_iterator>;
```

使い方は `regex_token_iterator` と同じです。`std::string` の分割には、`-1` を渡します。

分割した結果を `std::vector<std::string>` に入れたいときは、イテレータの範囲を、コンストラクターに渡します。`*it` は `std::ssub_match` で、`std::string` に変換できます。

```cpp
std::vector<std::string> parts(
    std::sregex_token_iterator(s.begin(), s.end(), sep, -1),
    std::sregex_token_iterator());
```

## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <regex>
#include <string>
#include <vector>

int main() {
  const std::string s = "elf,orc,dwarf";
  const std::regex sep(",");

  // 数える
  std::sregex_token_iterator it(s.begin(), s.end(), sep, -1);
  const std::sregex_token_iterator end;
  std::println("要素の数: {}", std::distance(it, end));

  // vector に入れる
  const std::vector<std::string> parts(
      std::sregex_token_iterator(s.begin(), s.end(), sep, -1),
      std::sregex_token_iterator());
  std::println("{} / {} / {}", parts[0], parts[1], parts[2]);
}
```

```text title="実行結果"
要素の数: 3
elf / orc / dwarf
```

イテレータの組から、`std::vector` を直接作れます。

## ゲームでの使いどころ

プレイヤーが入力した `"elf orc dwarf"` のような、区切り文字つきの入力を、`std::vector<std::string>` に分けるときに使います。

## よくあるミス

??? failure "一時オブジェクトの string を渡す"
    `s.begin()` が、破棄された文字列を指します。名前のある変数に入れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex_token_iterator`](regex_token_iterator.md) | 元のテンプレート |
| [`std::sregex_iterator`](../sregex_iterator.md) | 一致を `match_results` として返す |
| `std::views::split` | C++20 の固定の区切りでの分割 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `sregex_token_iterator` は、`std::string` 用の `regex_token_iterator`
    - [x] `-1` で分割できる。`vector` に直接入れられる
    - [x] 文字列は名前のある変数にする

## 関連ページ

- [cpprefjp: sregex_token_iterator](https://cpprefjp.github.io/reference/regex/sregex_token_iterator.html)
- [cppreference: std::sregex_token_iterator](https://en.cppreference.com/w/cpp/regex/regex_token_iterator)

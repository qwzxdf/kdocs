---
title: std::regex_token_iterator
summary: "文字列を、正規表現で分割して（または一致を取り出して）、順に返すイテレータ。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_token_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`"a,b,c"` を `,` で分けたい。標準の `std::string` には、分割の関数がありません。`regex_token_iterator` は、パターンに一致した部分で文字列を分けて、その間の部分を順に返せるので、分割の道具として使えます。一致した部分そのものや、一致の中のグループだけを取り出す使い方もできます。

!!! tip "ポイント"
    - 最後の引数 `submatch` で、何を返すかを選ぶ。`-1` なら、一致と一致の間（分割）
    - `0` なら一致の全体、`1` なら 1 番目のグループ
    - `{1, 2}` のように配列で渡すと、複数のグループを交互に返す
    - `-1` では、連続した区切りの間の空文字列も返される

!!! info "このページを読む前に"
    [`std::regex_iterator`](regex_iterator.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_token_iterator {#regex_token_iterator}

```cpp
template <class BidirIt, class CharT = typename std::iterator_traits<BidirIt>::value_type,
          class Traits = std::regex_traits<CharT>>
class regex_token_iterator;
```

`std::sregex_token_iterator` が `std::string` 用の別名です。`std::cregex_token_iterator` が `const char*`、`std::wsregex_token_iterator` と `std::wcregex_token_iterator` が `wchar_t` 用です。

### コンストラクター {#ctor}

```cpp
regex_token_iterator(BidirIt a, BidirIt b, const regex_type& re,
                     int submatch = 0, match_flag_type m = match_default);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `a`, `b` | `BidirIt` | 検索する範囲 |
| `re` | `const regex_type&` | パターン |
| `submatch` | `int` | 返す部分。`-1` は一致の間、`0` は全体、`1` 以上はグループ |
| `m` | `match_flag_type` | 検索の動作 |

### submatch の選択 {#submatch}

`submatch` が `-1` のとき、一致と一致の間にある部分（区切りの間）を返します。パターンを区切り文字にして、文字列を分割するのと同じです。

`submatch` が `0` なら、一致した全体を返します。`regex_iterator` で `it->str()` を取り出すのと同じです。`1` 以上なら、その番号のグループを返します。

複数の部分を取り出したいときは、`std::vector<int>` や配列を渡します。たとえば `{1, 2}` なら、一致のたびに、グループ 1、グループ 2 の順に返します。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  // 1. 分割: 区切りの間を返す（-1）
  const std::string s = "a,b,,c";
  const std::regex sep(",");
  std::sregex_token_iterator it(s.begin(), s.end(), sep, -1);
  const std::sregex_token_iterator end;
  for (; it != end; ++it) {
    std::println("[{}]", it->str());
  }

  // 2. グループだけを取り出す: key=value の value
  const std::string kv = "hp=30 mp=12";
  const std::regex pair(R"((\w+)=(\d+))");
  std::sregex_token_iterator v(kv.begin(), kv.end(), pair, 2);
  for (; v != end; ++v) {
    std::println("value {}", v->str());
  }
}
```

```text title="実行結果"
[a]
[b]
[]
[c]
value 30
value 12
```

`a,b,,c` を `,` で分けると、`b` と `c` の間の空の部分が、`[]` として現れます。連続した区切りを 1 つにまとめたい場合は、パターンを `,+` にします。

## ゲームでの使いどころ

CSV のような簡単な区切りの文字列を分割する、ちょっとしたツールで使います。大きなデータを速く分割するなら、`std::views::split` や、手書きの分割のほうが向いています。

## よくあるミス

??? failure "先頭や末尾の区切りの扱いを、考えていない"
    `",a"` を `,` で分割すると、先頭に空の要素が現れます。末尾の区切りは、空の要素を作りません（実装により異なります）。

??? failure "regex の一時オブジェクトを渡す"
    `std::regex(",")` を直接渡すと、コンパイルできません。変数に入れます。

??? failure "-1 と 0 を取り違える"
    `-1` は「一致の間」、`0` は「一致そのもの」です。分割したいときに `0` を渡すと、区切り文字だけが返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex_iterator`](regex_iterator.md) | 一致を `match_results` として返す |
| [`sregex_token_iterator`](sregex_token_iterator.md) | `std::string` 用の別名 |
| `std::views::split` | C++20 の分割。正規表現ではなく、固定の区切りを使う |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `regex_token_iterator` は、一致の間・一致・グループを、順に返す
    - [x] `-1` で分割、`0` で一致の全体、`1` 以上でグループ
    - [x] 連続した区切りは、空の要素になる

## 関連ページ

- [cpprefjp: regex_token_iterator](https://cpprefjp.github.io/reference/regex/regex_token_iterator.html)
- [cppreference: std::regex_token_iterator](https://en.cppreference.com/w/cpp/regex/regex_token_iterator)

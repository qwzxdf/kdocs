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

文字列を「,」で分割したいとき、`regex_token_iterator` で区切りの正規表現を渡し、最後の引数に `-1` を渡すと、区切りの**間**の部分を順に取り出せます。`0` なら一致した部分、`1` ならグループ 1 を取り出します。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_token_iterator {#regex_token_iterator}

```cpp
template <class BidirIt, class CharT = typename iterator_traits<BidirIt>::value_type, class Traits = regex_traits<CharT>>
class regex_token_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `BidirIt` | 型 | 文字列のイテレータの型 |

- 戻り値: 部分文字列（`sub_match`）を順に返す
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  std::string s = "a,b,c";
  std::regex sep(",");
  std::regex_token_iterator<std::string::const_iterator> it(s.begin(), s.end(), sep, -1);
  std::regex_token_iterator<std::string::const_iterator> end;
  for (; it != end; ++it) {
    std::println("{}", it->str());
  }
}
```

```text title="実行結果"
a
b
c
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 文字列を区切り文字で分割する |

## よくあるミス

??? failure "最後の引数を忘れる"
    `-1` を渡さないと、区切り自体が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sregex_token_iterator`](sregex_token_iterator.md) | string 用の別名 |
| [`views::split`](../../algorithms/views/split.md) | 新しい分割の書き方 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列を、正規表現で分割して（または一致を取り出して）、順に返すイテレータ
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::regex_token_iterator](https://cpprefjp.github.io/reference/regex/regex_token_iterator.html)
- [cppreference: std::regex_token_iterator](https://en.cppreference.com/w/cpp/regex/regex_token_iterator)

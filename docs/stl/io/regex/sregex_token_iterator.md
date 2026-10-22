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

`regex_token_iterator<std::string::const_iterator>` の別名です。`std::string` を正規表現で分割するときに使います。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::sregex_token_iterator {#sregex_token_iterator}

```cpp
using sregex_token_iterator = regex_token_iterator<std::string::const_iterator>;
```

- 戻り値: 部分文字列（`ssub_match`）を順に返す
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <regex>
#include <string>

int main() {
  std::string s = "a,b,c";
  std::regex sep(",");
  std::sregex_token_iterator it(s.begin(), s.end(), sep, -1);
  std::sregex_token_iterator end;
  std::println("{}", std::distance(it, end));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | `std::string` を区切り文字で分割する |

## よくあるミス

??? failure "一時オブジェクトの `string` を渡す"
    イテレータが指す文字列が先に消えると、壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex_token_iterator`](regex_token_iterator.md) | 元のテンプレート |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] string 用の regex_token_iterator
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::sregex_token_iterator](https://cpprefjp.github.io/reference/regex/sregex_token_iterator.html)
- [cppreference: std::sregex_token_iterator](https://en.cppreference.com/w/cpp/regex/sregex_token_iterator)

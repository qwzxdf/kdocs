---
title: std::sregex_iterator
summary: "パターンに合う部分を、全部順に回す。"
order: 90
tags:
  - 入出力・文字列
---

# std::sregex_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::sregex_iterator` は、**文字列の中でパターンに合う部分を、先頭から順にすべて取り出す**イテレータです。`regex_search` は最初の 1 つだけですが、こちらは全部を回せます。

!!! tip "ポイント"
    - `std::sregex_iterator it(s.begin(), s.end(), re), end;` と作り、`it != end` で回す。
    - 要素は [`std::smatch`](smatch.md)。
    - 一致が重ならないように、順に進む。

!!! info "このページを読む前に"
    [`std::regex`](regex.md) を先に読んでください。

## 関数の詳しい説明

### std::sregex_iterator {#sregex_iterator}

```cpp
using sregex_iterator = std::regex_iterator<std::string::const_iterator>;
```

- 一致する部分を前から順に全部たどります

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  std::string text = "HP:120 MP:30 SP:5";
  const std::regex kNumber(R"(\d+)");
  for (auto it = std::sregex_iterator(text.begin(), text.end(), kNumber);
       it != std::sregex_iterator(); ++it) {
    std::print("{} ", it->str());
  }
  std::println("");
}
```

```text title="実行結果"
120 30 5 
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| テキストの中の数字を全部集める | `for (auto it = ...; it != end; ++it)` |

## よくあるミス

??? failure "一時的な文字列に使う"
    イテレータは元の文字列を指します。一時的な文字列を渡さないでください。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::regex_search`](regex_search.md) | 最初の 1 つだけ |
| [`std::smatch`](smatch.md) | 要素の型 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全部の一致を順に回す
    - [x] 要素は `smatch`
    - [x] 元の文字列が生きている間だけ

## 関連ページ

- [cpprefjp: std::sregex_iterator](https://cpprefjp.github.io/reference/regex/regex_iterator.html)
- [cppreference: std::sregex_iterator](https://en.cppreference.com/w/cpp/regex/regex_iterator)

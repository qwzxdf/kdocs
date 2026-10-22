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

`regex_iterator<const char*>` の別名です。`std::string` ではなく、C の文字列（`const char*`）に対して、全部の一致を順に取り出します。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::cregex_iterator {#cregex_iterator}

```cpp
using cregex_iterator = regex_iterator<const char*>;
```

- 戻り値: 一致（`cmatch`）を順に返す
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <cstring>
#include <iterator>
#include <print>
#include <regex>

int main() {
  const char* s = "a1b22c333";
  std::regex re("\\d+");
  std::cregex_iterator it(s, s + std::strlen(s), re);
  std::cregex_iterator end;
  std::println("{}", std::distance(it, end));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | C の文字列から、一致を全部取り出す |

## よくあるミス

??? failure "終端の指定を忘れる"
    `s + strlen(s)` で終端を渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex_iterator`](regex_iterator.md) | 元のテンプレート |
| [`sregex_iterator`](../sregex_iterator.md) | string 用 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] C 文字列から、正規表現に一致する部分を順に取り出すイテレータ
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::cregex_iterator](https://cpprefjp.github.io/reference/regex/cregex_iterator.html)
- [cppreference: std::cregex_iterator](https://en.cppreference.com/w/cpp/regex/cregex_iterator)

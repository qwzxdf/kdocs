---
title: std::regex_iterator
summary: "文字列から、正規表現に一致する部分を、順に取り出すイテレータ。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_iterator

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`regex_search` は最初の一致だけを返します。全部の一致を順に処理したいとき、`regex_iterator` を使います。`std::sregex_iterator` は、これの `string` 用の別名です。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_iterator {#regex_iterator}

```cpp
template <class BidirIt, class CharT = typename iterator_traits<BidirIt>::value_type, class Traits = regex_traits<CharT>>
class regex_iterator;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `BidirIt` | 型 | 文字列のイテレータの型 |

- 戻り値: 一致（`match_results`）を順に返す
- 計算量: パターンと文字列に依存


## 実際に動かしてみる

```cpp
#include <iterator>
#include <print>
#include <regex>
#include <string>

int main() {
  std::string s = "a1b22c333";
  std::regex re("\\d+");
  std::regex_iterator<std::string::const_iterator> it(s.begin(), s.end(), re);
  std::regex_iterator<std::string::const_iterator> end;
  std::println("{}", std::distance(it, end));
}
```

```text title="実行結果"
3
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テキストから数字を全部取り出す |

## よくあるミス

??? failure "一致が空の正規表現を渡す"
    空の一致があると、無限ループにならないよう、1 文字ずつ進みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sregex_iterator`](../sregex_iterator.md) | string 用の別名 |
| [`cregex_iterator`](cregex_iterator.md) | C 文字列用 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列から、正規表現に一致する部分を、順に取り出すイテレータ
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::regex_iterator](https://cpprefjp.github.io/reference/regex/regex_iterator.html)
- [cppreference: std::regex_iterator](https://en.cppreference.com/w/cpp/regex/regex_iterator)

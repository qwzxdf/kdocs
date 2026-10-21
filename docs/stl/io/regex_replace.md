---
title: std::regex_replace
summary: "パターンに合う部分を、別の文字列に置き換える。"
order: 88
tags:
  - 入出力・文字列
---

# std::regex_replace

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex_replace` は、**正規表現に合う部分を、別の文字列に置き換えた結果**を返します。置換後の文字列では、`$1` のように、かっこで囲んだ部分を使い回せます。

!!! tip "ポイント"
    - 元の文字列は変わらず、置き換えた新しい文字列が返る。
    - `$1` `$2` で、かっこ（グループ）の中身を参照できる。
    - 単純な置き換えなら `std::string::replace` や手書きのほうが速い。

!!! info "このページを読む前に"
    [`std::regex`](regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_replace {#regex_replace}

```cpp
std::string regex_replace(const std::string& s, const std::regex& re, const std::string& fmt);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `s` | 文字列 | 元の文字列 |
| `re` | `std::regex` | 探すパターン |
| `fmt` | 文字列 | 置き換える文字列。`$1` でグループ 1、`$&` で一致した全体 |

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  std::string date = "2026-10-17";
  std::println("{}", std::regex_replace(date, std::regex(R"((\d+)-(\d+)-(\d+))"), "$3/$2/$1"));
}
```

```text title="実行結果"
17/10/2026
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ログの数値をマスクする | `std::regex_replace(line, std::regex(R"(\d+)"), "#")` |

## よくあるミス

??? failure "置換の $ が展開されて意図しない結果になる"
    `$` を文字として使うなら `$$` と書きます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::regex_search`](regex_search.md) | 探すだけ |
| `std::string::replace` | 位置を指定した置き換え |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 合う部分を置き換えた文字列を返す
    - [x] `$1` でグループを参照
    - [x] 元は変わらない

## 関連ページ

- [cpprefjp: std::regex_replace](https://cpprefjp.github.io/reference/regex/regex_replace.html)
- [cppreference: std::regex_replace](https://en.cppreference.com/w/cpp/regex/regex_replace)

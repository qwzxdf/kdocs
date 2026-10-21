---
title: std::regex_match
summary: "文字列の全体が、パターンに一致するか調べる。"
order: 87
tags:
  - 入出力・文字列
---

# std::regex_match

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex_match` は、**文字列の全体が正規表現に一致するか**を調べます。入力の形式チェック（数字だけか、メールの形か）に使います。一部だけ合えばよいなら [`regex_search`](regex_search.md) です。

!!! tip "ポイント"
    - **全体**が一致して初めて `true`。
    - `^` や `$` を付けなくても、全体が対象。
    - 一致した部分は `smatch` で取り出せる。

!!! info "このページを読む前に"
    [`std::regex`](regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_match {#regex_match}

```cpp
bool regex_match(const std::string& s, const std::regex& re);
bool regex_match(const std::string& s, std::smatch& m, const std::regex& re);
```

- 文字列**全体**が一致したときだけ `true`

```cpp
#include <print>
#include <regex>

int main() {
  const std::regex kDigits(R"(\d+)");
  std::println("{} {}", std::regex_match("123", kDigits), std::regex_match("a123", kDigits));
  std::println("{}", std::regex_search("a123", kDigits));
}
```

```text title="実行結果"
true false
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 入力の形式チェック（数字だけ、など） | `std::regex_match(s, std::regex(R"(\d+)"))` |

## よくあるミス

??? failure "一部の一致で true を期待する"
    `regex_match("abc123", R"(\d+)")` は false です。含まれるかなら `regex_search`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::regex_search`](regex_search.md) | 部分の一致 |
| [`std::from_chars`](from_chars.md) | 数値かの確認だけなら、こちらが速い |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全体が一致するか
    - [x] `regex_search` との違いに注意
    - [x] regex は使い回す

## 関連ページ

- [cpprefjp: std::regex_match](https://cpprefjp.github.io/reference/regex/regex_match.html)
- [cppreference: std::regex_match](https://en.cppreference.com/w/cpp/regex/regex_match)

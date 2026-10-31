---
title: std::regex_constants
summary: "正規表現のオプションとエラーコードをまとめた名前空間。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_constants

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex::icase` や `std::regex_constants::match_continuous` のように、正規表現の動作を指定する定数は、`std::regex_constants` という名前空間にまとまっています。文法とオプションの `syntax_option_type`、検索の動作の `match_flag_type`、エラーの原因の `error_type` の 3 種類があります。

!!! tip "ポイント"
    - 3 種類の定数がある: 文法とオプション、検索の動作、エラー コード
    - 文法のオプションは、`std::regex::icase` のようにクラスのメンバーとしても書ける
    - ビットマスク型なので、`|` で組み合わせる
    - 一致の動作は `regex_match` / `regex_search` の最後の引数で指定する

!!! info "このページを読む前に"
    [`std::basic_regex`](basic_regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_constants {#regex_constants}

```cpp
namespace std::regex_constants {
  // syntax_option_type: icase, nosubs, optimize, collate, ECMAScript, ...
  // match_flag_type:    match_default, match_not_bol, match_continuous, ...
  // error_type:         error_paren, error_brack, error_range, ...
}
```

| 種類 | 使う場所 | 詳しい説明 |
| --- | --- | --- |
| `syntax_option_type` | `std::regex` のコンストラクターの第 2 引数 | [`syntax_option_type`](syntax_option_type.md) |
| `match_flag_type` | `regex_match`、`regex_search`、`regex_replace` の最後の引数 | [`match_flag_type`](match_flag_type.md) |
| `error_type` | `regex_error::code()` の戻り値 | [`regex_error`](regex_error.md) |

`syntax_option_type` の定数は、`std::regex::icase` のように、`basic_regex` のクラスのメンバーとしても使えます。`std::regex_constants::icase` と同じものです。短く書けるので、こちらがよく使われます。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  // 文法とオプション: クラスのメンバーでも、名前空間でも同じ
  const std::regex a("abc", std::regex::icase);
  const std::regex b("abc", std::regex_constants::icase);
  std::println("同じ動き: {}",
               std::regex_match("ABC", a) == std::regex_match("ABC", b));

  // 検索の動作: 先頭からの一致だけを認める
  const std::regex re("abc");
  std::println("xabc: {}",
               std::regex_search("xabc", re, std::regex_constants::match_continuous));
  std::println("abcx: {}",
               std::regex_search("abcx", re, std::regex_constants::match_continuous));
}
```

```text title="実行結果"
同じ動き: true
xabc: false
abcx: true
```

## ゲームでの使いどころ

大文字小文字を区別しない検索（`icase`）と、先頭からの一致の判定（`match_continuous`）が、よく使われます。

## よくあるミス

??? failure "match_flag_type を、regex のコンストラクターに渡す"
    型が違うので、コンパイル エラーになるか、意図しない動作になります。コンストラクターには `syntax_option_type`、検索には `match_flag_type` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`syntax_option_type`](syntax_option_type.md) | 文法とオプション |
| [`match_flag_type`](match_flag_type.md) | 検索の動作 |
| [`regex_error`](regex_error.md) | エラー コード |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `regex_constants` は、正規表現の3 種類の定数をまとめた名前空間
    - [x] 文法は `std::regex::icase` のように、クラスのメンバーでも書ける
    - [x] 組み合わせるときは `|`

## 関連ページ

- [cpprefjp: regex_constants](https://cpprefjp.github.io/reference/regex/regex_constants.html)
- [cppreference: std::regex_constants](https://en.cppreference.com/w/cpp/regex/regex_constants)

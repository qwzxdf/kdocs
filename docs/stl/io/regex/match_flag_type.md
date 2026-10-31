---
title: std::regex_constants::match_flag_type
summary: "一致や置換の動作を指定するビットマスク型。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_constants::match_flag_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`regex_search` は、既定では、文字列の先頭から探し、どこでも一致を認めます。「先頭から一致しなければ失敗にしたい」「`^` を先頭の行頭として扱いたくない」「置換のときに、一致しない部分は出力しない」。こうした検索や置換の細かな動作を指定するフラグが `match_flag_type` です。

`regex_match`、`regex_search`、`regex_replace` の最後の引数に渡し、`|` で組み合わせられます。

!!! tip "ポイント"
    - 検索の動作は `match_` で始まる定数、置換の動作は `format_` で始まる定数
    - `match_continuous` は、探し始めの位置から一致しなければ失敗にする
    - `match_not_bol` は、先頭を行頭とみなさず、`^` が先頭に一致しなくなる
    - `format_no_copy` と `format_first_only` は、`regex_replace` だけで効く

!!! info "このページを読む前に"
    [`std::regex_constants`](regex_constants.md) と [`std::regex_search`](../regex_search.md) を先に読んでください。

## 関数の詳しい説明

### 検索の動作 {#match}

| 定数 | 意味 |
| --- | --- |
| `match_default` | 既定の動作 |
| `match_not_bol` | 先頭を行頭とみなさない。`^` が先頭に一致しなくなる |
| `match_not_eol` | 末尾を行末とみなさない。`$` が末尾に一致しなくなる |
| `match_not_bow` | 先頭を単語の先頭とみなさない。`\b` や `\<` に影響する |
| `match_not_eow` | 末尾を単語の末尾とみなさない |
| `match_any` | 複数の一致候補があるとき、どれでもよい（最長を探さない） |
| `match_not_null` | 空文字列への一致を認めない |
| `match_continuous` | 探し始めの位置から、ちょうど一致する場合だけ認める |
| `match_prev_avail` | 先頭の 1 つ前に文字がある（`^` や `\b` の判定に影響） |

### match_continuous {#continuous}

`regex_search` の探し始めの位置から、一致が始まっていなければ失敗にします。文字列の途中まで読み進めながら、次のトークンを切り出していく、字句解析のような処理に使います。

### match_not_bol と match_not_eol {#bol-eol}

`^` と `$` が、先頭と末尾に一致するかを制御します。文字列の途中から検索を再開するときに、途中の位置を行頭と間違えないために使います。

### match_not_null {#not-null}

`\d*` のように、空文字列に一致するパターンで、空の一致を認めません。`regex_iterator` で全部の一致を取り出すとき、空の一致で進めなくなるのを避けられます。

### 置換の動作 {#format}

`regex_replace` で使える定数です。

| 定数 | 意味 |
| --- | --- |
| `format_default` | 既定。ECMAScript の書式（`$1`、`$&`）で置換する |
| `format_sed` | `sed` の書式（`\1`、`&`）で置換する |
| `format_no_copy` | 一致しなかった部分を、出力にコピーしない |
| `format_first_only` | 最初の一致だけを置換する |

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  const std::regex re("abc");
  std::println("match_continuous: xabc={} abcx={}",
               std::regex_search("xabc", re, std::regex_constants::match_continuous),
               std::regex_search("abcx", re, std::regex_constants::match_continuous));

  const std::regex head("^a");
  std::println("match_not_bol: {}",
               std::regex_search("ab", head, std::regex_constants::match_not_bol));

  const std::regex digit(R"(\d)");
  const std::string s = "a1b2";
  std::println("既定: {}", std::regex_replace(s, digit, "#"));
  std::println("format_first_only: {}",
               std::regex_replace(s, digit, "#", std::regex_constants::format_first_only));
  std::println("format_no_copy: {}",
               std::regex_replace(s, digit, "#", std::regex_constants::format_no_copy));
}
```

```text title="実行結果"
match_continuous: xabc=false abcx=true
match_not_bol: false
既定: a#b#
format_first_only: a#b2
format_no_copy: ##
```

`format_no_copy` では、一致した部分の置換結果だけが残り、`a` と `b` は出力されません。

## ゲームでの使いどころ

コマンドの解析やスクリプトの字句解析で、先頭から順に切り出すときに、`match_continuous` を使います。ただし、`std::regex` は遅いので、ゲーム本体の処理では、手書きの解析のほうが速いです。

## よくあるミス

??? failure "match_continuous のつもりで ^ を使う"
    `^` は、文字列の先頭にしか一致しません。途中の位置から再開するときは、`^` が効かなくなるので、`match_continuous` を使います。

??? failure "format_ の定数を regex_search に渡す"
    `format_*` は、置換にだけ意味があります。検索に渡しても、無視されます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`syntax_option_type`](syntax_option_type.md) | パターンの文法と、構築時のオプション |
| [`regex_constants`](regex_constants.md) | 定数をまとめた名前空間 |
| [`std::regex_replace`](../regex_replace.md) | 置換の動作を、このフラグで指定する |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `match_flag_type` は、検索と置換の細かな動作を指定する
    - [x] `match_continuous`、`match_not_bol`、`format_no_copy`、`format_first_only` をよく使う
    - [x] `format_*` は `regex_replace` だけで効く

## 関連ページ

- [cpprefjp: regex_constants::match_flag_type](https://cpprefjp.github.io/reference/regex/match_flag_type.html)
- [cppreference: std::regex_constants::match_flag_type](https://en.cppreference.com/w/cpp/regex/match_flag_type)

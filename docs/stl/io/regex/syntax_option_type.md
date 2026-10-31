---
title: std::regex_constants::syntax_option_type
summary: "正規表現の構文やオプションを指定するビットマスク型。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_constants::syntax_option_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

同じ `a|b` というパターンでも、JavaScript のような ECMAScript 系の文法と、`grep` のような POSIX の文法とでは、書き方や意味が違う部分があります。`std::regex` は、複数の文法に対応していて、コンストラクターの第 2 引数のフラグで選びます。文法に加えて、大文字小文字の扱いなどのオプションも、同じフラグで指定します。

このフラグの型が `syntax_option_type` で、`|` で組み合わせられるビットマスクです。

!!! tip "ポイント"
    - 文法は 1 つだけ選ぶ。省略すると `ECMAScript`
    - オプションは `icase`（大文字小文字を区別しない）、`nosubs`、`optimize`、`collate`、`multiline`
    - `std::regex::icase` のように、`basic_regex` のメンバーとしても書ける
    - `|` で組み合わせる（`std::regex::icase | std::regex::extended`）

!!! info "このページを読む前に"
    [`std::basic_regex`](basic_regex.md) と [`std::regex_constants`](regex_constants.md) を先に読んでください。

## 関数の詳しい説明

### 文法の選択 {#grammar}

| 定数 | 文法 |
| --- | --- |
| `ECMAScript` | JavaScript と同じ系統。既定。`\d`、`\w`、`(?:...)`、先読みが使える |
| `basic` | POSIX の基本正規表現（`grep` の既定）。`+` や `|` の扱いが違う |
| `extended` | POSIX の拡張正規表現（`egrep`）。`+`、`?`、`|` が使える |
| `awk` | `awk` の文法。拡張正規表現に近く、エスケープが多い |
| `grep` | `grep` の文法。`basic` に改行を区切りとする機能を足したもの |
| `egrep` | `egrep` の文法。`extended` に改行を区切りとする機能を足したもの |

ゲームで使うなら、選ぶ理由がない限り、既定の ECMAScript で足ります。`\d` が使えて、書き方が JavaScript の知識で通用します。`extended` や `basic` は、既存の `grep` のパターンを、そのまま持ち込みたいときに使います。

### icase {#icase}

大文字小文字を区別せずに一致させます。`"abc"` のパターンが、`"ABC"` や `"aBc"` にも一致します。ユーザーが入力したコマンドの判定に、よく使います。

### nosubs {#nosubs}

グループ（`(...)`）の内容を記録しません。全体が一致したかだけを調べたいときに、結果を保持する手間が省けて、速くなります。ただし、`match_results` の中身は全体の一致だけになります。

### optimize {#optimize}

パターンの変換に時間をかけて、検索を速くします。同じパターンを何度も使うときに指定します。実装によっては、効果がありません。

### collate {#collate}

`[a-z]` のような範囲指定を、ロケールの並び順で解釈します。

### multiline {#multiline}

`^` と `$` が、文字列全体の先頭・末尾だけでなく、各行の先頭・末尾に一致します。C++17 で追加された、ECMAScript 用のオプションです。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  // icase: 大文字小文字を区別しない
  const std::regex a("hero", std::regex::icase);
  std::println("icase: {}", std::regex_match("HeRo", a));

  // ECMAScript では \d が使える
  const std::regex b(R"(\d+)");
  std::println("ECMAScript の \\d: {}", std::regex_match("123", b));

  // extended では | で選択できる
  const std::regex c("cat|dog", std::regex::extended);
  std::println("extended: cat={} dog={} bird={}",
               std::regex_match("cat", c), std::regex_match("dog", c),
               std::regex_match("bird", c));

  // フラグの組み合わせ
  const std::regex d("cat|dog", std::regex::extended | std::regex::icase);
  std::println("組み合わせ: {}", std::regex_match("DOG", d));
}
```

```text title="実行結果"
icase: true
ECMAScript の \d: true
extended: cat=true dog=true bird=false
組み合わせ: true
```

`extended | icase` のように、文法とオプションを `|` で組み合わせられます。

## ゲームでの使いどころ

デバッグ コンソールのコマンドの判定に、`icase` を付けます。`Hero`、`hero`、`HERO` を同じ入力として扱えます。

## よくあるミス

??? failure "文法を 2 つ選ぶ"
    `std::regex::extended | std::regex::basic` は不正で、`std::regex_error` になります。文法は 1 つだけです。

??? failure "文法を指定すると、ECMAScript のオプションが効かなくなる"
    `std::regex::icase` だけ指定すれば、文法は ECMAScript のままです。`extended` を足すと文法が変わり、`\d` が使えなくなります。

??? failure "nosubs で、グループの結果を期待する"
    グループは記録されません。`m[1]` を参照しても、値はありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`match_flag_type`](match_flag_type.md) | 検索の動作を指定するフラグ |
| [`regex_constants`](regex_constants.md) | 定数をまとめた名前空間 |
| [`basic_regex`](basic_regex.md) | このフラグを受け取るクラス |

## コンパイラ対応

C++11 から使えます。`multiline` は C++17 からで、実装により対応に差があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `syntax_option_type` は、文法とオプションを指定するビットマスク
    - [x] 文法は 1 つだけ。省略すると ECMAScript
    - [x] 大文字小文字を区別しないなら `std::regex::icase`

## 関連ページ

- [cpprefjp: regex_constants::syntax_option_type](https://cpprefjp.github.io/reference/regex/syntax_option_type.html)
- [cppreference: std::regex_constants::syntax_option_type](https://en.cppreference.com/w/cpp/regex/syntax_option_type)

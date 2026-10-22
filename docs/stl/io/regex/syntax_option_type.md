---
title: std::syntax_option_type
summary: "正規表現の構文やオプションを指定するビットマスク型。"
order: 900
tags:
  - 入出力・文字列
---

# std::syntax_option_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex` を作るときの第 2 引数に渡す型です。`icase | ECMAScript` のように `|` でつなぎます。構文は 1 つだけ選び、`icase` などのオプションは重ねられます。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_constants::syntax_option_type {#syntax_option_type}

```cpp
enum syntax_option_type : /* 実装定義 */;
```

- 戻り値: ビットマスク型

### std::regex_constants::icase {#icase}

```cpp
constexpr syntax_option_type icase = /* 実装定義 */;
```

- 戻り値: 大文字小文字を区別しない

大文字小文字を区別しない。

### std::regex_constants::nosubs {#nosubs}

```cpp
constexpr syntax_option_type nosubs = /* 実装定義 */;
```

- 戻り値: グループを記録しない（速くなる）

グループを記録しない（速くなる）。

### std::regex_constants::optimize {#optimize}

```cpp
constexpr syntax_option_type optimize = /* 実装定義 */;
```

- 戻り値: 実行速度を優先して準備する（構築が遅くなる）

実行速度を優先して準備する（構築が遅くなる）。

### std::regex_constants::collate {#collate}

```cpp
constexpr syntax_option_type collate = /* 実装定義 */;
```

- 戻り値: 範囲指定（`[a-z]`）をロケールの順序で解釈する

範囲指定（`[a-z]`）をロケールの順序で解釈する。

### std::regex_constants::multiline {#multiline}

```cpp
constexpr syntax_option_type multiline = /* 実装定義 */;
```

- 戻り値: `^` と `$` を、行の先頭・末尾にも一致させる（C++17）

`^` と `$` を、行の先頭・末尾にも一致させる（C++17）。

### std::regex_constants::ECMAScript {#ECMAScript}

```cpp
constexpr syntax_option_type ECMAScript = /* 実装定義 */;
```

- 戻り値: ECMAScript（JavaScript）風の構文（既定）

ECMAScript（JavaScript）風の構文（既定）。

### std::regex_constants::basic {#basic}

```cpp
constexpr syntax_option_type basic = /* 実装定義 */;
```

- 戻り値: POSIX の基本正規表現

POSIX の基本正規表現。

### std::regex_constants::extended {#extended}

```cpp
constexpr syntax_option_type extended = /* 実装定義 */;
```

- 戻り値: POSIX の拡張正規表現

POSIX の拡張正規表現。

### std::regex_constants::awk {#awk}

```cpp
constexpr syntax_option_type awk = /* 実装定義 */;
```

- 戻り値: POSIX の awk の構文

POSIX の awk の構文。

### std::regex_constants::grep {#grep}

```cpp
constexpr syntax_option_type grep = /* 実装定義 */;
```

- 戻り値: POSIX の grep の構文

POSIX の grep の構文。

### std::regex_constants::egrep {#egrep}

```cpp
constexpr syntax_option_type egrep = /* 実装定義 */;
```

- 戻り値: POSIX の egrep（grep -E）の構文

POSIX の egrep（grep -E）の構文。


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  std::regex::flag_type f = std::regex_constants::icase | std::regex_constants::ECMAScript;
  std::regex re("abc", f);
  std::println("{}", std::regex_match("ABC", re));
}
```

```text title="実行結果"
true
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 構文とオプションを指定して正規表現を作る |

## よくあるミス

??? failure "構文を 2 つ選ぶ"
    構文（`ECMAScript`・`basic` など）は 1 つだけ選びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex_constants`](regex_constants.md) | 定数の名前空間 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 正規表現の構文やオプションを指定するビットマスク型
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::syntax_option_type](https://cpprefjp.github.io/reference/regex/syntax_option_type.html)
- [cppreference: std::syntax_option_type](https://en.cppreference.com/w/cpp/regex/syntax_option_type)

---
title: std::match_flag_type
summary: "一致や置換の動作を指定するビットマスク型。"
order: 900
tags:
  - 入出力・文字列
---

# std::match_flag_type

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`regex_search`・`regex_match`・`regex_replace` の最後の引数に渡す型です。`match_continuous` や `format_first_only` のように、`|` でつなぎます。

!!! tip "ポイント"
    - `<regex>` の部品。
    - ふつうは別名（`regex`・`smatch` など）を使う。
    - 正規表現は、複雑になりすぎる前に別の方法も検討する。

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_constants::match_flag_type {#match_flag_type}

```cpp
enum match_flag_type : /* 実装定義 */;
```

- 戻り値: ビットマスク型

### std::regex_constants::match_default {#match_default}

```cpp
constexpr match_flag_type match_default = /* 実装定義 */;
```

- 戻り値: 既定の動作

既定の動作。

### std::regex_constants::match_not_bol {#match_not_bol}

```cpp
constexpr match_flag_type match_not_bol = /* 実装定義 */;
```

- 戻り値: `^` を先頭に一致させない（文字列の先頭を行頭と扱わない）

`^` を先頭に一致させない（文字列の先頭を行頭と扱わない）。

### std::regex_constants::match_not_eol {#match_not_eol}

```cpp
constexpr match_flag_type match_not_eol = /* 実装定義 */;
```

- 戻り値: `$` を末尾に一致させない

`$` を末尾に一致させない。

### std::regex_constants::match_not_bow {#match_not_bow}

```cpp
constexpr match_flag_type match_not_bow = /* 実装定義 */;
```

- 戻り値: `\b` を単語の先頭に一致させない

`\b` を単語の先頭に一致させない。

### std::regex_constants::match_not_eow {#match_not_eow}

```cpp
constexpr match_flag_type match_not_eow = /* 実装定義 */;
```

- 戻り値: `\b` を単語の末尾に一致させない

`\b` を単語の末尾に一致させない。

### std::regex_constants::match_any {#match_any}

```cpp
constexpr match_flag_type match_any = /* 実装定義 */;
```

- 戻り値: 複数の一致があるとき、どれでもよい（最初に見つかったもの）

複数の一致があるとき、どれでもよい（最初に見つかったもの）。

### std::regex_constants::match_not_null {#match_not_null}

```cpp
constexpr match_flag_type match_not_null = /* 実装定義 */;
```

- 戻り値: 空の一致を認めない

空の一致を認めない。

### std::regex_constants::match_continuous {#match_continuous}

```cpp
constexpr match_flag_type match_continuous = /* 実装定義 */;
```

- 戻り値: 文字列の先頭からの一致だけを認める

文字列の先頭からの一致だけを認める。

### std::regex_constants::match_prev_avail {#match_prev_avail}

```cpp
constexpr match_flag_type match_prev_avail = /* 実装定義 */;
```

- 戻り値: 前の文字が使える（先頭ではない）ものとして扱う

前の文字が使える（先頭ではない）ものとして扱う。

### std::regex_constants::format_default {#format_default}

```cpp
constexpr match_flag_type format_default = /* 実装定義 */;
```

- 戻り値: 置換の書式に ECMAScript を使う（既定）

置換の書式に ECMAScript を使う（既定）。

### std::regex_constants::format_sed {#format_sed}

```cpp
constexpr match_flag_type format_sed = /* 実装定義 */;
```

- 戻り値: 置換の書式に POSIX の sed を使う

置換の書式に POSIX の sed を使う。

### std::regex_constants::format_no_copy {#format_no_copy}

```cpp
constexpr match_flag_type format_no_copy = /* 実装定義 */;
```

- 戻り値: 置換で、一致しない部分をコピーしない

置換で、一致しない部分をコピーしない。

### std::regex_constants::format_first_only {#format_first_only}

```cpp
constexpr match_flag_type format_first_only = /* 実装定義 */;
```

- 戻り値: 置換で、最初の一致だけを置き換える

置換で、最初の一致だけを置き換える。


## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  std::regex re("abc");
  std::println("{}", std::regex_search("xabc", re, std::regex_constants::match_continuous));
}
```

```text title="実行結果"
false
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 先頭からの一致だけを調べる |

## よくあるミス

??? failure "置換用のフラグを検索に使う"
    `format_*` は `regex_replace` 用です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`regex_constants`](regex_constants.md) | 定数の名前空間 |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 一致や置換の動作を指定するビットマスク型
    - [x] `<regex>` の部品
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::match_flag_type](https://cpprefjp.github.io/reference/regex/match_flag_type.html)
- [cppreference: std::match_flag_type](https://en.cppreference.com/w/cpp/regex/match_flag_type)

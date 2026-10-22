---
title: std::regex
summary: "正規表現による文字列の検索・置換。便利だが遅い。"
order: 69
tags:
  - 文字列
---

# std::regex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="perf perf-1">× 重い</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex` は、**正規表現（文字列のパターン）で検索・一致判定・置き換えをする**ライブラリです。`"\\d+"`（数字の並び）のようなパターンで、メールアドレスの形式チェックや、ログから特定の行を抜き出す処理が短く書けます。ただし標準の regex は**とても遅く**、パターンの組み立て（コンパイル）も重いので、ゲームの中で毎フレーム使うものではありません。

!!! tip "ポイント"
    - ゲーム本体ではほぼ使わない。ツールやエディタで、たまに文字列を調べるくらい。
    - 使うなら `std::regex` を**一度だけ作って使い回す**（作るのが重い）。
    - 全体が一致するかは `regex_match`、どこかに含まれるかは `regex_search`、置き換えは `regex_replace`。
    - 速さが必要なら、手で書いた処理（`find`、`starts_with`、`from_chars`）か外部ライブラリ（RE2、CTRE など）。

## 関数一覧

| 関数・型 | 重要度 | 何をする |
| --- | --- | --- |
| [`std::regex`](#regex) | <span class="rank rank-sometimes">たまに</span> | パターンを表す型 |
| [`std::regex_search`](regex_search.md) | <span class="rank rank-sometimes">たまに</span> | 文字列の**どこかに**パターンがあるか |
| [`std::regex_match`](regex_match.md) | <span class="rank rank-sometimes">たまに</span> | 文字列**全体が**パターンに一致するか |
| [`std::regex_replace`](regex_replace.md) | <span class="rank rank-sometimes">たまに</span> | 一致した部分を置き換える |
| [`std::smatch`](smatch.md) | <span class="rank rank-sometimes">たまに</span> | 一致した部分（グループ）の結果 |
| [`std::sregex_iterator`](sregex_iterator.md) | <span class="rank rank-rare">知ってるだけ</span> | 一致するものを全部たどる |

## よくある使い方

```cpp
#include <print>
#include <regex>
#include <string>

int main() {
  const std::regex kPattern(R"((\w+)=(\d+))");  // 名前=数字

  std::string line = "volume=80";
  std::smatch m;
  if (std::regex_match(line, m, kPattern)) {
    std::println("キー {} / 値 {}", m[1].str(), m[2].str());
  }

  std::string log = "[ERROR] code 404 at stage 3";
  std::println("ERROR を含む？ {}", std::regex_search(log, std::regex(R"(\[ERROR\])")));
  std::println("{}", std::regex_replace(log, std::regex(R"(\d+)"), "#"));
}
```

```text title="実行結果"
キー volume / 値 80
ERROR を含む？ true
[ERROR] code # at stage #
```

`R"(...)"` は生文字列リテラルで、`\` をそのまま書けます（`"\\d"` と書かなくていい）。

## 関数の詳しい説明

### std::regex {#regex}

```cpp
explicit basic_regex(const std::string& pattern, flag_type flags = ECMAScript);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `pattern` | 文字列 | 正規表現のパターン |
| `flags` | `std::regex::flag_type` | 文法や大文字小文字の扱い（[フラグ](#フラグオプション)） |

- パターンが間違っていると `std::regex_error` 例外
- 作るのが重いので、`static const` やメンバ変数にして使い回します

## フラグ・オプション

`std::regex` を作るときのフラグ（`std::regex::` または `std::regex_constants::`）です。

| 値 | 重要度 | 意味 |
| --- | --- | --- |
| `ECMAScript`（省略時） | <span class="rank rank-sometimes">たまに</span> | JavaScript と同じ文法。普通はこれ |
| `icase` | <span class="rank rank-sometimes">たまに</span> | 大文字と小文字を区別しない |
| `optimize` | <span class="rank rank-rare">知ってるだけ</span> | 作るのは遅くなるが、検索を速くする（効果は実装次第） |
| `nosubs` | <span class="rank rank-rare">知ってるだけ</span> | グループの結果を保存しない（少し速い） |
| `multiline` | <span class="rank rank-rare">知ってるだけ</span> | `^` と `$` を各行の先頭・末尾にも一致させる <span class="ver ver-17">C++17</span> |
| `basic` / `extended` / `awk` / `grep` / `egrep` | <span class="rank rank-rare">知ってるだけ</span> | POSIX などの別の文法 |
| `collate` | <span class="rank rank-rare">知ってるだけ</span> | `[a-z]` などをロケールに従って比べる |

検索・置き換えのときのフラグ（`std::regex_constants::match_flag_type`）もあります。

| 値 | 意味 |
| --- | --- |
| `format_first_only` | `regex_replace` で最初の 1 つだけ置き換える |
| `format_no_copy` | `regex_replace` で一致しなかった部分を出力しない |
| `match_not_bol` / `match_not_eol` | 先頭・末尾を行の始まり・終わりとみなさない |

```cpp
#include <print>
#include <regex>

int main() {
  std::regex re("error", std::regex::icase);
  std::println("{}", std::regex_search("FATAL ERROR", re));
  std::println("{}", std::regex_replace("a1b2c3", std::regex(R"(\d)"), "_",
                                        std::regex_constants::format_first_only));
}
```

```text title="実行結果"
true
a_b2c3
```

### assign {#assign}

```cpp
basic_regex& assign(const std::string& s, flag_type f = ECMAScript);
```

- 計算量: O(パターンの長さ)

新しいパターンを設定します（コンパイルし直します）。

### flags {#flags}

```cpp
flag_type flags() const;
```

- 計算量: 定数

構文のオプション（`icase` など）。

### mark_count {#mark_count}

```cpp
unsigned mark_count() const;
```

- 計算量: 定数

パターンの中のグループ（括弧）の数。

### imbue {#imbue}

```cpp
locale_type imbue(locale_type loc);
```

- 計算量: 定数

正規表現が使うロケールを設定します。パターンは破棄されます。

### getloc {#getloc}

```cpp
locale_type getloc() const;
```

- 計算量: 定数

正規表現が使うロケール。

### swap {#swap}

```cpp
void swap(basic_regex& other) noexcept;
```

- 計算量: 定数

2 つの正規表現を入れ替えます。

### operator= {#op_assign}

```cpp
basic_regex& operator=(const basic_regex& rhs);
basic_regex& operator=(const std::string& s);
```

- 計算量: O(パターンの長さ)

別の正規表現、または文字列のパターンを代入します。

## ゲームでの使いどころ

| 場面 | 例 |
| --- | --- |
| ツール | アセット名の命名ルールのチェック |
| エディタ | 検索・置換機能 |
| ログ解析 | 特定のエラーを含む行を抜き出す |

ゲーム中（毎フレーム）には使いません。

## よくあるミス

??? failure "ループの中で regex を作る"
    `std::regex` の作成はパターンを解析して内部の機械を組み立てるので、とても重いです。

??? failure "\\ を二重にし忘れる"
    普通の文字列では `"\\d"` と書く必要があります。生文字列リテラル `R"(\d)"` を使うと楽です。

??? failure "長い文字列でスタックが溢れる"
    実装によっては、長い入力と複雑なパターンで再帰が深くなり落ちることがあります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`string::find` / `contains`](../containers/string.md#find) | 単純な文字列ならこちらがずっと速い |
| CTRE（外部ライブラリ） | コンパイル時に正規表現を組み立てるのでとても速い |
| RE2（外部ライブラリ） | Google 製。速く、悪いパターンでも遅くなりにくい |

## コンパイラ対応

C++11 からある機能です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 全体一致は match、部分一致は search、置換は replace
    - [x] regex は一度作って使い回す
    - [x] 遅いのでゲーム中には使わない

## 関連ページ

- [cpprefjp: <regex>](https://cpprefjp.github.io/reference/regex.html)
- [cppreference: Regular expressions library](https://en.cppreference.com/w/cpp/regex)

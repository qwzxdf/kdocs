---
title: std::basic_regex
summary: "正規表現を保持するクラスの、元になるテンプレート（`regex` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_regex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

`std::regex` は `std::basic_regex<char>` の別名で、`std::wregex` は `std::basic_regex<wchar_t>` の別名です。パターンの文字列を受け取って、検索に使える内部の形に変換して持つのが、このクラスの仕事です。`regex_match` や `regex_search` に渡すのは、文字列のパターンではなく、この変換済みのオブジェクトです。

パターンの変換は、検索よりずっと時間がかかります。そのため、ループの中で `std::regex re("...")` を作り直すと遅くなります。1 度だけ作って使い回します。

!!! tip "ポイント"
    - `std::regex` は `basic_regex<char>`、`std::wregex` は `basic_regex<wchar_t>`
    - パターンの変換（コンストラクター）は重い。ループの外に出して、使い回す
    - 文法は既定で ECMAScript。第 2 引数のフラグで、`icase` や `extended` などを選べる
    - 不正なパターンを渡すと `std::regex_error` を投げる

!!! info "このページを読む前に"
    [`std::regex`](../regex.md) の概要を先に読んでください。

## 関数の詳しい説明

### std::basic_regex {#basic_regex}

```cpp
template <class CharT, class Traits = std::regex_traits<CharT>>
class basic_regex;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `CharT` | 文字の型。`char` や `wchar_t` |
| `Traits` | 文字の分類や大文字小文字の規則。普通は既定のまま |

### コンストラクター {#ctor}

```cpp
explicit basic_regex(const CharT* p, flag_type f = ECMAScript);
basic_regex(const std::basic_string<CharT>& s, flag_type f = ECMAScript);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `p` / `s` | 文字列 | 正規表現のパターン |
| `f` | `flag_type` | 文法と動作のフラグ。[`syntax_option_type`](syntax_option_type.md) の組み合わせ |

パターンの文字列を解析して、検索用の内部の形に変換します。ここで時間がかかります。パターンが不正なとき（括弧が閉じていないなど）は、`std::regex_error` を投げます。

文法は、フラグで選びます。省略した場合は ECMAScript（JavaScript と同じ系統）です。`\d` や `\w`、`(?:...)`、先読み `(?=...)` が使えます。ただし、後読み `(?<=...)` は使えません。

### mark_count {#mark_count}

```cpp
unsigned mark_count() const;
```

パターンの中の、キャプチャ グループ（`(...)`）の個数を返します。`(\d+)-(\d+)` なら 2 です。`(?:...)` は数えません。`match_results` の大きさは、これに 1 を足した値になります。

### flags {#flags}

```cpp
flag_type flags() const;
```

指定したフラグを返します。

### assign {#assign}

```cpp
basic_regex& assign(const CharT* p, flag_type f = ECMAScript);
```

パターンを入れ替えます。コンストラクターと同じく、解析に時間がかかります。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  // 1. 1 度だけ作る。グループは 2 つ
  const std::regex re(R"((\d+)-(\d+))");
  std::println("グループ数: {}", re.mark_count());
  std::println("10-20 に一致: {}", std::regex_match("10-20", re));

  // 2. 大文字小文字を区別しない
  const std::regex name("hero", std::regex::icase);
  std::println("HERO に一致: {}", std::regex_match("HERO", name));

  // 3. パターンを入れ替える
  std::regex re2("a+");
  re2.assign("b+");
  std::println("aaa: {} bbb: {}", std::regex_match("aaa", re2),
               std::regex_match("bbb", re2));
}
```

```text title="実行結果"
グループ数: 2
10-20 に一致: true
HERO に一致: true
aaa: false bbb: true
```

`R"(...)"` の生文字列リテラルを使うと、`\d` のバックスラッシュを二重に書かなくて済みます。

## ゲームでの使いどころ

コンソール コマンドや設定ファイルの 1 行を解析する、小さなツールで使います。コマンド名や数値のように、形が決まっている入力の検査に向いています。

ただし、`std::regex` は、実装によって速度が遅く、ゲームのフレーム内で呼ぶ処理には向きません。起動時の読み込みなど、頻度の低い所に限ります。

## よくあるミス

??? failure "ループの中で regex を作り直す"
    パターンの変換が毎回行われ、検索より桁違いに時間がかかります。`static const std::regex re(...)` や、ループの外に置きます。

??? failure "バックスラッシュの二重化を忘れる"
    `"\d+"` は、C++ の文字列としては不正な（または意図と違う）エスケープです。`"\\d+"` か、生文字列 `R"(\d+)"` にします。

??? failure "不正なパターンの例外を考えていない"
    ユーザーが入力したパターンを渡すときは、`std::regex_error` を `catch` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::wregex`](wregex.md) | `wchar_t` 用 |
| [`regex_error`](regex_error.md) | パターンが不正なときの例外 |
| [`syntax_option_type`](syntax_option_type.md) | 文法とオプションのフラグ |
| [`std::regex_match`](../regex_match.md) | 全体の一致を調べる |

## コンパイラ対応

C++11 から使えます。実装により、速度と、一部の構文の対応に差があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `basic_regex` は、パターンを検索用の形に変換して持つ。`regex` はその別名
    - [x] 変換は重い。1 度だけ作って使い回す
    - [x] 不正なパターンは `regex_error`。生文字列リテラルでエスケープを減らす

## 関連ページ

- [cpprefjp: basic_regex](https://cpprefjp.github.io/reference/regex/basic_regex.html)
- [cppreference: std::basic_regex](https://en.cppreference.com/w/cpp/regex/basic_regex)

---
title: std::regex_traits
summary: "文字の分類や変換の規則をまとめた、正規表現の部品。"
order: 900
tags:
  - 入出力・文字列
---

# std::regex_traits

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <regex>`
</div>

正規表現の `\d` は数字、`\w` は英数字、`[[:alpha:]]` は英字、`icase` では大文字小文字を同じとみなす。こうした「文字をどう分類し、どう比べるか」の規則を持つ部品が `regex_traits` です。`basic_regex` が内部で使っていて、普段は意識しません。

!!! tip "ポイント"
    - `basic_regex` の第 2 テンプレート引数。既定は `std::regex_traits<CharT>`
    - 文字クラスの名前を調べる `lookup_classname`、判定する `isctype`
    - 比較用の変換 `translate_nocase`、長さを求める `length`
    - 自作して、特別な規則の正規表現を作れるが、ゲームではほぼ使わない

!!! info "このページを読む前に"
    [`std::basic_regex`](basic_regex.md) を先に読んでください。

## 関数の詳しい説明

### std::regex_traits {#regex_traits}

```cpp
template <class CharT>
struct regex_traits;
```

主な関数は、次のとおりです。

| 関数 | 役割 |
| --- | --- |
| `static std::size_t length(const CharT* p)` | 文字列の長さを返す |
| `CharT translate(CharT c) const` | 比較のために文字を変換する（何もしない） |
| `CharT translate_nocase(CharT c) const` | 大文字小文字を同一視する変換 |
| `char_class_type lookup_classname(const CharT* first, const CharT* last, bool icase = false) const` | 文字クラスの名前から、判定用の値を得る |
| `bool isctype(CharT c, char_class_type f) const` | 文字 `c` が、そのクラスに属するか |
| `int value(CharT c, int radix) const` | 文字を数値として読む（16 進など） |

### lookup_classname と isctype {#class}

`[[:digit:]]` のような、文字クラスの名前を、判定用の値に直す関数が `lookup_classname` です。`"digit"`、`"alpha"`、`"alnum"`、`"space"`、`"upper"`、`"lower"`、`"punct"` などを受け付けます。得た値を `isctype` に渡すと、文字がそのクラスに属するかを調べられます。

名前が未知なら、0 に相当する値が返ります。

## 実際に動かしてみる

```cpp
#include <print>
#include <regex>

int main() {
  std::regex_traits<char> traits;

  std::println("長さ: {}", std::regex_traits<char>::length("abc"));

  const char name[] = "digit";
  const auto digit = traits.lookup_classname(name, name + 5);
  std::println("'7' は digit: {}", traits.isctype('7', digit));
  std::println("'a' は digit: {}", traits.isctype('a', digit));

  std::println("大文字小文字を同一視: {}",
               traits.translate_nocase('A') == traits.translate_nocase('a'));
}
```

```text title="実行結果"
長さ: 3
'7' は digit: true
'a' は digit: false
大文字小文字を同一視: true
```

## ゲームでの使いどころ

自分で使うことはほとんどありません。ゲーム特有の文字の分類（全角と半角を同一視するなど）を、正規表現に組み込みたいときに、自作のトレイツを作る道があります。

## よくあるミス

??? failure "regex_traits を直接触って、文法の動きを変えようとする"
    パターンの文法は、トレイツではなく、`syntax_option_type` で選びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::basic_regex`](basic_regex.md) | これを使う正規表現のクラス |
| `std::char_traits` | 文字列のクラスが使う、別のトレイツ |

## コンパイラ対応

C++11 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `regex_traits` は、文字の分類と比較の規則を持つ部品
    - [x] `basic_regex` が内部で使う。普段は触らない
    - [x] 文法の選択は `syntax_option_type`

## 関連ページ

- [cpprefjp: regex_traits](https://cpprefjp.github.io/reference/regex/regex_traits.html)
- [cppreference: std::regex_traits](https://en.cppreference.com/w/cpp/regex/regex_traits)

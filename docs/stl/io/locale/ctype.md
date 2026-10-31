---
title: std::ctype
summary: "文字の分類（数字か、英字か）と、大文字小文字の変換を担当するファセット。"
order: 900
tags:
  - 入出力・文字列
---

# std::ctype

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <locale>`
</div>

文字が数字かどうか、英字かどうか、空白かどうか。小文字を大文字に変えたい。`<cctype>` の `isdigit` や `toupper` と同じことを、ロケールに従って行う部品が `std::ctype` です。ストリームの `>>` が、空白を読み飛ばすときの判定に使うのも、これです。

`std::isalpha(c, loc)` のような関数でも使えますが、内部では、この `ctype` を取り出して呼んでいます。

!!! tip "ポイント"
    - `is(分類, c)` で分類を調べ、`toupper` / `tolower` で変換する
    - 文字列の範囲をまとめて変換するオーバーロードがある（`toupper(first, last)`）
    - `widen` は `char` を `CharT` に、`narrow` は逆に直す
    - ストリームの空白の扱いを変えたいときは、自作の `ctype` を差し込む

!!! info "このページを読む前に"
    [`std::use_facet`](use_facet.md) を先に読んでください。ファセットの取り出し方が分かります。

## 関数の詳しい説明

### std::ctype {#ctype}

```cpp
template <class CharT>
class ctype;  // is(), toupper(), tolower(), widen(), narrow() など
```

標準では、`ctype<char>` と `ctype<wchar_t>` が用意されています。ここでは `ctype<char>` を例にします。

### is {#is}

```cpp
bool is(std::ctype_base::mask m, char c) const;
```

文字 `c` が、分類 `m` に当てはまるかを調べます。分類は `ctype_base` の定数で、複数を `|` で合わせて指定できます。

| 分類 | 当てはまる文字 |
| --- | --- |
| `space` | 空白、タブ、改行 |
| `digit` | 数字 `0`〜`9` |
| `alpha` | 英字 |
| `alnum` | 英字か数字 |
| `upper` / `lower` | 大文字 / 小文字 |
| `punct` | 句読点などの記号 |
| `xdigit` | 16 進の数字 |

### toupper と tolower {#toupper}

```cpp
char toupper(char c) const;
const char* toupper(char* first, const char* last) const;
```

1 文字を変換する版と、`[first, last)` の範囲をその場で変換する版があります。変換できない文字（記号や、変換先のない文字）は、そのまま返ります。`tolower` も同じ形です。

### widen と narrow {#widen}

```cpp
char widen(char c) const;
char narrow(char c, char dfault) const;
```

`CharT` と `char` の間で、文字を変換します。`ctype<char>` では何もしませんが、`ctype<wchar_t>` では、`char` を `wchar_t` に直します。`narrow` の第 2 引数は、変換できなかったときの代わりの文字です。

## 実際に動かしてみる

```cpp
#include <locale>
#include <print>
#include <string>

int main() {
  const std::locale loc = std::locale::classic();
  const auto& ct = std::use_facet<std::ctype<char>>(loc);

  std::println("'7' は数字: {}", ct.is(std::ctype_base::digit, '7'));
  std::println("'a' は数字: {}", ct.is(std::ctype_base::digit, 'a'));
  std::println("'a' は英字か数字: {}", ct.is(std::ctype_base::alnum, 'a'));

  std::string name = "hero 01";
  ct.toupper(name.data(), name.data() + name.size());  // 範囲をまとめて変換
  std::println("{}", name);
}
```

```text title="実行結果"
'7' は数字: true
'a' は数字: false
'a' は英字か数字: true
HERO 01
```

`toupper` の範囲版は、文字列をその場で書き換えます。数字と空白は変わりません。

## ゲームでの使いどころ

プレイヤー名の入力で、大文字小文字を区別せずに比べたいときなどに、大文字にそろえてから比べます。

```cpp
const auto& ct = std::use_facet<std::ctype<char>>(std::locale::classic());
ct.toupper(name.data(), name.data() + name.size());
```

ただし、これは 1 バイトずつの変換なので、UTF-8 の日本語などを含む文字列では、`char` 単位の判定が意味を持たない文字があります。ASCII の範囲に限った処理に使います。

## よくあるミス

??? failure "UTF-8 の文字列に使う"
    1 バイトずつ判定するので、複数バイトの文字の途中のバイトを、誤って分類することがあります。ASCII の範囲だけに使います。

??? failure "負の char を <cctype> の関数に渡す"
    `std::toupper` に `char` の負の値を渡すと未定義動作です。`ctype` の関数は、`char` を直接受け取るので、この問題は起きません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isalpha`](../../numeric/cctype/isalpha.md) など | C の関数。現在の C ロケールに従う |
| `std::isalpha(c, loc)` | ロケールを指定して分類する関数。内部でこれを使う |
| [`use_facet`](use_facet.md) | ファセットを取り出す |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ctype` は、ロケールに従う文字の分類と大文字小文字の変換
    - [x] `is`、`toupper`、`tolower`。範囲をまとめて変換する版もある
    - [x] UTF-8 の文字列には使わない

## 関連ページ

- [cpprefjp: ctype](https://cpprefjp.github.io/reference/locale/ctype.html)
- [cppreference: std::ctype](https://en.cppreference.com/w/cpp/locale/ctype)

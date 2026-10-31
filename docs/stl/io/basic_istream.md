---
title: std::basic_istream
summary: "入力ストリームの元になるテンプレート（`istream` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_istream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <istream>`
</div>

`std::istream` は、`basic_istream<char>` の別名です。`wchar_t` の入力に使う `std::wistream` は、`basic_istream<wchar_t>` の別名です。2 つとも、文字の型を引数に取る 1 つのクラステンプレートから作られています。

普段は別名の `istream` だけを使います。`basic_istream` という名前は、コンパイルエラーの長い型名の中で見かけるくらいです。出力側の [`basic_ostream`](basic_ostream.md) と対になっているので、あわせて読むと全体が分かります。

!!! tip "ポイント"
    - `std::istream` は `basic_istream<char>`、`std::wistream` は `basic_istream<wchar_t>` の別名
    - 普段は別名を使う。引数には参照で受ける（コピーできない）
    - `cin`、`ifstream`、`istringstream` は、どれも `istream` の仲間
    - 読み込みの状態（成功、失敗、終端）は、親の `basic_ios` が持っている

!!! info "このページを読む前に"
    [`std::cin`](cin.md) と [`std::istream`](istream.md) を先に読んでください。`>>` や `getline` の使い方は、そちらに書いています。

## 関数の詳しい説明

### std::basic_istream {#basic_istream}

```cpp
template <class CharT, class Traits = std::char_traits<CharT>>
class basic_istream : virtual public std::basic_ios<CharT, Traits>;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `CharT` | 文字の型。`char` や `wchar_t` |
| `Traits` | 文字の比較やコピーのしかたを決める型。普通は既定のまま |

`CharT` が、読み取る文字の型を決めます。`char` のストリームは、バイトの並びを読むので、UTF-8 の日本語も 1 バイトずつ読みます。`wchar_t` のストリームは、Windows では UTF-16 の 1 単位ずつを読みます。

`basic_ios` からの継承は仮想継承です。`std::iostream` が `istream` と `ostream` の両方を継承しても、`basic_ios` を 1 つしか持たないようにするためです。`good()`、`fail()`、`eof()`、`clear()` などは、この `basic_ios` の関数です。

`basic_istream` 自身の持つ操作は、書式つきで読む `operator>>`、1 文字ずつ読む `get`、1 行読む `getline`、読み飛ばす `ignore`、先を見る `peek`、ブロックで読む `read`、位置を動かす `seekg` と `tellg` などです。詳しくは [`std::istream`](istream.md) のページにあります。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <type_traits>

int main() {
  static_assert(std::is_same_v<std::istream, std::basic_istream<char>>);
  static_assert(std::is_same_v<std::wistream, std::basic_istream<wchar_t>>);
  static_assert(!std::is_copy_constructible_v<std::istream>);

  // istringstream は istream の仲間なので、istream& で受けられる
  std::istringstream text("12 34");
  std::istream& in = text;
  int a = 0;
  int b = 0;
  in >> a >> b;
  std::println("{} {}", a, b);
}
```

```text title="実行結果"
12 34
```

`istringstream` を `istream&` の変数に入れても、そのまま読めます。関数の引数を `std::istream&` にしておくと、キーボードでも、ファイルでも、文字列でも、同じ関数で読めるのは、このためです。

## ゲームでの使いどころ

読み込みの関数を `std::istream&` で受けると、ファイルから読む処理を、文字列だけでテストできます。

```cpp
bool LoadStage(std::istream& in, Stage& stage);
```

本番では `ifstream` を渡し、テストでは `istringstream` を渡します。`basic_istream` のテンプレートを書く場面は、まずありません。

## よくあるミス

??? failure "ストリームを値で受ける"
    `void Load(std::istream in)` はコンパイルエラーです。コピーできないからです。`std::istream&` で受けます。

??? failure "wchar_t のストリームに char の文字列を読み込む"
    `std::wcin >> std::string` はコンパイルエラーです。文字の型を合わせて、`std::wstring` に読みます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::istream`](istream.md) | `basic_istream<char>` の別名。普段はこちらを使う |
| [`std::basic_ostream`](basic_ostream.md) | 出力側 |
| [`std::basic_iostream`](basic_iostream.md) | 読み書き両用 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `istream` は `basic_istream<char>` の別名
    - [x] 引数には `std::istream&` で受けると、ファイルでも文字列でも渡せる
    - [x] コピーできない

## 関連ページ

- [cpprefjp: std::basic_istream](https://cpprefjp.github.io/reference/istream/basic_istream.html)
- [cppreference: std::basic_istream](https://en.cppreference.com/w/cpp/io/basic_istream)

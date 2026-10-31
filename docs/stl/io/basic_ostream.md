---
title: std::basic_ostream
summary: "出力ストリームの元になるテンプレート（`ostream` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_ostream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ostream>`
</div>

`std::ostream` という名前は、実は別名です。本体は、文字の型を引数に取るクラステンプレートの `std::basic_ostream` で、`std::ostream` は `basic_ostream<char>` の別名にすぎません。`wchar_t` の文字を出したいときの `std::wostream` は、`basic_ostream<wchar_t>` の別名です。

普段のコードで `basic_ostream` と書くことはほとんどありません。エラーメッセージに `std::basic_ostream<char,std::char_traits<char>>` という長い名前が出てきたときに、「ああ、`ostream` のことか」と読み替えられれば十分です。

!!! tip "ポイント"
    - `std::ostream` は `basic_ostream<char>`、`std::wostream` は `basic_ostream<wchar_t>` の別名
    - 普段は別名を使う。テンプレートそのものは、自作の `operator<<` を `wchar_t` にも対応させるときくらいにしか書かない
    - コピーできない。関数の引数には、参照で受ける
    - 書式の状態（桁数、進数、幅）は `basic_ios` の側が持っている

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::ostream`](ostream.md) を先に読んでください。`<<` の使い方は、そちらに書いています。

## 関数の詳しい説明

### std::basic_ostream {#basic_ostream}

```cpp
template <class CharT, class Traits = std::char_traits<CharT>>
class basic_ostream : virtual public std::basic_ios<CharT, Traits>;
```

| テンプレート引数 | 意味 |
| --- | --- |
| `CharT` | 文字の型。`char` や `wchar_t` |
| `Traits` | 文字の比較やコピーのしかたを決める型。普通は既定の `std::char_traits<CharT>` のまま |

`CharT` で、ストリームが扱う文字が決まります。`char` のストリームに `L"abc"` は流せず、`wchar_t` のストリームに `"abc"` は流せません。`Traits` を変える場面は、ほとんどありません。大文字小文字を区別しない文字列型を、独自に作るときくらいです。

親の `basic_ios` は、仮想継承です。`std::iostream`（読み書き両用）が `istream` と `ostream` の両方から継承するときに、`basic_ios` が 1 つだけ共有されるようにするための仕組みです。状態を調べる関数（`good()`、`fail()`、`eof()`）は、`basic_ios` にあります。

`basic_ostream` 自身が持つ操作は、整形して出す `operator<<` の仲間と、整形しない書き込み（`put`、`write`）、出力位置の移動（`tellp`、`seekp`）、バッファを吐き出す `flush` です。詳しくは [`std::ostream`](ostream.md) のページにあります。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <type_traits>

int main() {
  // ostream と wostream は、basic_ostream の別名
  static_assert(std::is_same_v<std::ostream, std::basic_ostream<char>>);
  static_assert(std::is_same_v<std::wostream, std::basic_ostream<wchar_t>>);

  // どちらも basic_ios から派生している
  static_assert(std::is_base_of_v<std::basic_ios<char>, std::ostream>);

  // コピーはできない
  static_assert(!std::is_copy_constructible_v<std::ostream>);

  std::wostringstream out;
  out << L"HP " << 30;
  std::println("{}", out.str().size());
}
```

```text title="実行結果"
5
```

`static_assert` で、別名の関係とコピーできないことを確かめています。`wostringstream` は `wostream` の仲間なので、`L"HP "` と数値を流せます。書いたのは `HP 30` の 5 文字です。

## ゲームでの使いどころ

テンプレートの形で書く場面は、自作の型を `char` でも `wchar_t` でも出せるようにしたいライブラリ作りくらいです。

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& operator<<(
    std::basic_ostream<CharT, Traits>& os, const Vec2& v) {
  return os << '(' << v.x << ", " << v.y << ')';
}
```

ゲーム本体のコードは、`std::ostream&` で受けるだけで困りません。

## よくあるミス

??? failure "ストリームを値で受ける"
    ストリームはコピーできません。`void Dump(std::ostream os)` と書くとコンパイルエラーです。`std::ostream&` で受けます。

??? failure "char のストリームに wchar_t の文字列を流す"
    `std::cout << L"abc"` は文字列ではなく、ポインタとして扱われて、アドレスが出ます。`wchar_t` を出すなら `std::wcout` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ostream`](ostream.md) | `basic_ostream<char>` の別名。普段はこちらを使う |
| [`std::basic_istream`](basic_istream.md) | 入力側 |
| [`std::basic_iostream`](basic_iostream.md) | 読み書き両用 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ostream` は `basic_ostream<char>` の別名
    - [x] 普段は別名を使い、引数には参照で受ける
    - [x] エラーメッセージに出てきたら、`ostream` のことだと読み替える

## 関連ページ

- [cpprefjp: std::basic_ostream](https://cpprefjp.github.io/reference/ostream/basic_ostream.html)
- [cppreference: std::basic_ostream](https://en.cppreference.com/w/cpp/io/basic_ostream)

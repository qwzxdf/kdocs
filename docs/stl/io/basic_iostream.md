---
title: std::basic_iostream
summary: "読み書き両用のストリームの元になるテンプレート（`iostream` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_iostream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <istream>`
</div>

読むことも書くこともできるストリームが欲しい場面があります。同じ文字列バッファに書いたあとで読み直す `stringstream` や、同じファイルを読んで書き換える `fstream` です。`basic_iostream` は、そのための土台で、読む側の `basic_istream` と書く側の `basic_ostream` の両方を継承しています。

`std::iostream` は `basic_iostream<char>` の別名です。普段は、`fstream` や `stringstream` を通して、間接的に使っています。

!!! tip "ポイント"
    - `basic_istream` と `basic_ostream` の両方を継承する。`>>` と `<<` の両方が使える
    - `std::iostream` は `basic_iostream<char>`、`std::wiostream` は `basic_iostream<wchar_t>` の別名
    - `fstream`・`stringstream` の親。`cin` や `cout` の型ではない
    - 読む位置と書く位置は別に管理される場合と、共通の場合がある（ストリームの種類による）

!!! info "このページを読む前に"
    [`basic_istream`](basic_istream.md) と [`basic_ostream`](basic_ostream.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_iostream {#basic_iostream}

```cpp
template <class CharT, class Traits = std::char_traits<CharT>>
class basic_iostream
    : public std::basic_istream<CharT, Traits>,
      public std::basic_ostream<CharT, Traits>;
```

両方を継承するので、`in >> x` も `out << x` も、同じオブジェクトに対して書けます。状態の管理を行う `basic_ios` は、2 つの親が仮想継承で共有するので、1 つだけです。読み込みで `failbit` が立てば、書き込みもそのストリームの状態を見て失敗します。

読む位置と書く位置が同じなのか別なのかは、中のバッファ（`streambuf`）で決まります。`stringstream` では、読む位置（`tellg`）と書く位置（`tellp`）が別々に動きます。そのため、書いたあとにすぐ読み始めると、先頭から読めます。`fstream` は、読む位置と書く位置が 1 つで、読んだあとに書くときは、`seekp` や `seekg` で位置を決め直す必要があります。

実際に `basic_iostream` を直接作ることは、ほとんどありません。`basic_streambuf` を自作して、それを `std::iostream` に結び付ける、という使い方はできますが、特殊な場面です。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <type_traits>

int main() {
  static_assert(std::is_same_v<std::iostream, std::basic_iostream<char>>);
  static_assert(std::is_base_of_v<std::istream, std::iostream>);
  static_assert(std::is_base_of_v<std::ostream, std::iostream>);

  // stringstream は iostream の仲間。書いたあと、同じものから読める
  std::stringstream ss;
  std::iostream& io = ss;
  io << 12 << ' ' << 34;
  int a = 0;
  int b = 0;
  io >> a >> b;
  std::println("{} {}", a, b);
}
```

```text title="実行結果"
12 34
```

`iostream&` の変数に、`stringstream` を入れています。`<<` で書いたあとに、同じ変数から `>>` で読めました。

## ゲームでの使いどころ

読み書き両用のストリームを引数で受け取る関数は、まず作りません。読むだけなら `std::istream&`、書くだけなら `std::ostream&` で受けるほうが、渡せる相手が広がるからです。たとえば `cout` は `ostream` ですが `iostream` ではないので、`std::iostream&` を引数にすると、`cout` は渡せません。

## よくあるミス

??? failure "cout を iostream& で受けようとする"
    `std::cout` の型は `std::ostream` で、`iostream` ではありません。`void Dump(std::iostream& io)` に渡すとコンパイルエラーです。出力するだけなら `std::ostream&` で受けます。

??? failure "書いた直後に読むと、何も読めない（fstream）"
    `fstream` で書いたあとに読むときは、`seekg(0)` で位置を戻し、必要なら `flush` します。位置を決め直さずに切り替えると、未定義の動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::iostream`](iostream.md) | `basic_iostream<char>` の別名。普段はこちら |
| [`std::basic_istream`](basic_istream.md) | 読む側だけ |
| [`std::basic_ostream`](basic_ostream.md) | 書く側だけ |
| [`std::stringstream`](stringstream.md) | 文字列に読み書きする |
| [`std::fstream`](fstream.md) | ファイルに読み書きする |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `iostream` は、`istream` と `ostream` の両方を継承した読み書き両用
    - [x] `fstream` と `stringstream` の親。`cin` や `cout` はこの型ではない
    - [x] 引数は、必要なほう（`istream&` か `ostream&`）で受ける

## 関連ページ

- [cpprefjp: std::basic_iostream](https://cpprefjp.github.io/reference/istream/basic_iostream.html)
- [cppreference: std::basic_iostream](https://en.cppreference.com/w/cpp/io/basic_iostream)

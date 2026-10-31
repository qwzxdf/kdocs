---
title: std::iostream
summary: "入力も出力もできるストリームのクラス。"
order: 900
tags:
  - 入出力・文字列
---

# std::iostream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <istream>`
</div>

「`<iostream>` を include する」という書き方から、`std::iostream` は `cin` や `cout` の型だと思いがちです。でも、`cin` の型は `std::istream`、`cout` の型は `std::ostream` で、`std::iostream` ではありません。`<iostream>` はヘッダーの名前で、そのヘッダーが `cin` と `cout` を宣言しているだけです。

`std::iostream` というクラスは、`istream` と `ostream` の両方を継承した、読み書き両用のストリームの型です。`std::stringstream` や `std::fstream` が、これを土台にしています。

!!! tip "ポイント"
    - `cin` は `istream`、`cout` は `ostream`。`iostream` ではない
    - `iostream` は `basic_iostream<char>` の別名。`stringstream` と `fstream` の親
    - 関数の引数では、必要なほう（`istream&` か `ostream&`）で受ける
    - ヘッダーの `<iostream>` と、クラスの `std::iostream` は別の物

!!! info "このページを読む前に"
    [`std::basic_iostream`](basic_iostream.md) のページに、テンプレートとしての説明があります。先に [`std::cout`](cout.md) と [`std::cin`](cin.md) を読んでおいてください。

## 関数の詳しい説明

### std::iostream {#iostream}

```cpp
using iostream = basic_iostream<char>;
```

`std::istream` と `std::ostream` の両方の機能を持ちます。そのため、`<<` で書き、`>>` で読み、`getline`、`put`、`seekg`、`seekp` などが、全部 1 つのオブジェクトで使えます。

クラスの階層は、次のようになっています。

- `std::ios_base` → `std::basic_ios` → `std::istream` と `std::ostream` → `std::iostream`
- `std::iostream` → `std::stringstream`（文字列）、`std::fstream`（ファイル）

読み取り専用の `ifstream` や `istringstream` は `istream` から、書き込み専用の `ofstream` や `ostringstream` は `ostream` から派生します。`iostream` を経由するのは、読み書き両用の `stringstream` と `fstream` だけです。

関数の引数にするとき、`iostream` で受けることは、ほとんどありません。読み書きを両方行う関数でない限り、`istream&` か `ostream&` のほうが、渡せる相手が増えます。`std::cin` や `std::cout` は、`iostream` ではないので、`iostream&` の引数には渡せません。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>
#include <type_traits>

int main() {
  // cin と cout の型は iostream ではない
  static_assert(std::is_same_v<decltype(std::cin), std::istream>);
  static_assert(std::is_same_v<decltype(std::cout), std::ostream>);
  static_assert(!std::is_base_of_v<std::iostream, std::istream>);

  // stringstream は iostream の仲間
  static_assert(std::is_base_of_v<std::iostream, std::stringstream>);

  std::println("確認できた");
}
```

```text title="実行結果"
確認できた
```

`static_assert` が全部通れば、コンパイルできます。`cin` の型が `istream`、`cout` の型が `ostream` であることと、`stringstream` が `iostream` の仲間であることを確かめました。

## ゲームでの使いどころ

`std::iostream` を名前で書く場面は少なく、`fstream` や `stringstream` を使うときに、裏で動いています。入出力を 1 つのオブジェクトでこなす設定ファイルの更新や、メモリ上でのデータの書き込みと読み込みのテストに、`std::stringstream` を使います。

## よくあるミス

??? failure "cout や cin を iostream& で受けようとする"
    `void Run(std::iostream& io)` に `std::cout` を渡すと、型が違うのでコンパイルエラーです。出力なら `std::ostream&`、入力なら `std::istream&` で受けます。

??? failure "ヘッダーの iostream と、クラスの iostream を混同する"
    `<iostream>` は `cin`、`cout`、`cerr`、`clog` を宣言するヘッダーです。クラスの `std::iostream` は `<istream>` で宣言されていて、`<iostream>` を include すれば、いっしょに入ります。`cin` や `cout` を使うだけなら、クラスの `std::iostream` を意識する必要はありません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::istream`](istream.md) | 読む側だけ。`cin` の型 |
| [`std::ostream`](ostream.md) | 書く側だけ。`cout` の型 |
| [`std::stringstream`](stringstream.md) | 文字列に読み書きする |
| [`std::fstream`](fstream.md) | ファイルに読み書きする |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `iostream` は、読み書き両用のクラス。`cin` と `cout` の型ではない
    - [x] `stringstream` と `fstream` の親
    - [x] 関数の引数は、`istream&` か `ostream&` で受ける

## 関連ページ

- [cpprefjp: std::iostream](https://cpprefjp.github.io/reference/istream/iostream.html)
- [cppreference: std::iostream](https://en.cppreference.com/w/cpp/io/basic_iostream)

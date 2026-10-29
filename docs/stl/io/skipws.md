---
title: std::skipws
summary: "入力で、先頭の空白を読み飛ばす（既定でオン）。"
order: 900
tags:
  - 入出力・文字列
---

# std::skipws

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

`std::cin >> n;` で数を読むとき、入力が `   42` のように空白から始まっていても、読めます。`>>` が、先頭の空白を黙って読み飛ばしているからです。この動きを決めているのが `skipws` の設定で、既定でオンです。`noskipws` でオフにすると、空白も 1 文字として読めるようになります。

!!! tip "ポイント"
    - 整形入力（`>>`）は、既定で先頭の空白を読み飛ばす（`skipws`）
    - `noskipws` にすると、空白が読み飛ばされず、数を読むときは失敗する
    - 文字を 1 つずつ読んで、空白も数えたいときに `noskipws` を使う
    - 設定は残り続けるので、使い終わったら `skipws` に戻す

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::skipws {#skipws}

```cpp
std::ios_base& skipws(std::ios_base& str);
std::ios_base& noskipws(std::ios_base& str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `ios_base&` | 設定を変えるストリーム |

`skipws` は `str.setf(std::ios_base::skipws)` を呼び、`noskipws` は `str.unsetf(std::ios_base::skipws)` を呼びます。入力ストリームの既定は、オンです。

この設定が効くのは、`>>` による整形入力だけです。`get()`、`getline()`、`read()` のような、整形しない入力関数は、設定に関係なく空白を読み飛ばしません。

## 実際に動かしてみる

```cpp
#include <iostream>
#include <print>
#include <sstream>

int main() {
  std::istringstream in("  42");
  int n = -1;
  in >> n;
  std::println("skipws(既定): n={} ok={}", n, static_cast<bool>(in));

  std::istringstream in2("  42");
  n = -1;
  in2 >> std::noskipws >> n;
  std::println("noskipws: n={} ok={}", n, static_cast<bool>(in2));

  // 文字を 1 つずつ読むとき、空白も欲しいなら noskipws
  std::istringstream in3("a b");
  in3 >> std::noskipws;
  char c;
  int count = 0;
  while (in3 >> c) ++count;
  std::println("文字数: {}", count);
}
```

```text title="実行結果"
skipws(既定): n=42 ok=true
noskipws: n=0 ok=false
文字数: 3
```

1 つ目は、空白を読み飛ばして `42` が読めます。2 つ目は、`noskipws` で空白が残っているため、数として読めず、`failbit` が立って `n` は 0 になります（C++11 以降、失敗した整数の読み込みは 0 を入れます）。3 つ目は、`a b` の 3 文字が、空白も含めて数えられています。`noskipws` を付けないと、空白が飛ばされて 2 文字になります。

## ゲームでの使いどころ

文字を 1 文字ずつ見て、空白の数や位置まで扱いたいときです。簡単な字句解析（スクリプトの命令を、単語に分けるなど）や、字下げを保ったままの文字列の読み込みで使います。

文字を 1 文字読むだけなら、`noskipws` を設定する代わりに `in.get(c)` を使うほうが、設定が残らず安全です。

## よくあるミス

??? failure "`noskipws` を付けたあと、数が読めなくなった"
    設定が残っているためです。数を読む前に `std::skipws` に戻します。

??? failure "`getline` の前に `skipws` を付けたが、効かない"
    `skipws` が効くのは `>>` だけです。`getline` は、設定に関係なく空白を読み飛ばしません。行頭の空白を捨てたいときは、[`ws`](ws.md) を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ws`](ws.md) | 設定ではなく、その場で空白を読み捨てる |
| [`getline`](getline.md) | 設定に関係なく、空白も読む |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `>>` は既定で先頭の空白を読み飛ばす（`skipws`）
    - [x] `noskipws` にすると、空白が 1 文字として読まれ、数の読み込みは失敗する
    - [x] 設定は残る。使い終わったら `skipws` に戻す

## 関連ページ

- [cpprefjp: std::skipws](https://cpprefjp.github.io/reference/ios/skipws.html)
- [cppreference: std::skipws](https://en.cppreference.com/w/cpp/io/manip/skipws)

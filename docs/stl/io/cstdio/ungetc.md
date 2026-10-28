---
title: std::ungetc
summary: "読んだ文字を 1 文字、ファイルに戻す。"
order: 900
tags:
  - 入出力・文字列
---

# std::ungetc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

トークナイザーで、数字が続く限り読みたい。でも、数字でない文字を 1 つ読んでしまってから、「これは次のトークンの先頭だった」と気づく。読んでしまった 1 文字を、読まなかったことにしたいときに使うのが `std::ungetc` です。

<strong>読んだ 1 文字を、入力に押し戻します</strong>。次の読み込みで、同じ文字がもう一度読めます。

!!! tip "ポイント"
    - 押し戻せることが保証されるのは 1 文字だけ。連続して押し戻す数は、環境による
    - 戻り値は、押し戻した文字。失敗は `EOF`
    - ファイルの中身は書き換わらない。読み込み用のバッファーに戻すだけ
    - `EOF` は押し戻せない

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::ungetc {#ungetc}

```cpp
int ungetc(int ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | `int` | 押し戻す文字 |
| `stream` | `FILE*` | 押し戻す先のファイル |

押し戻した文字は、次の `fgetc` などで最初に読まれます。ファイルそのものは変わらず、内部のバッファーに 1 文字置かれるだけです。

規格が保証するのは、<strong>1 文字</strong>だけです。読み込みを挟まず 2 回続けて押し戻すと、失敗する環境があります。先読みが 1 文字で足りる字句解析に向いた道具です。

直前に読んだ文字と、同じ文字を押し戻す必要はありません。ただし、`fseek` や `rewind` を呼ぶと、押し戻した文字は捨てられます。`EOF` を押し戻そうとすると、何も起きず、`EOF` が返ります。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("tok.txt", "w");
  std::fputs("123+45", out);
  std::fclose(out);

  std::FILE* f = std::fopen("tok.txt", "r");
  int value = 0;
  int c;
  while ((c = std::fgetc(f)) != EOF) {
    if (c < '0' || c > '9') {
      std::ungetc(c, f);               // 数字でない文字は、次のトークンのために戻す
      break;
    }
    value = value * 10 + (c - '0');
  }
  std::println("数: {}", value);
  std::println("次の文字: {}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
数: 123
次の文字: +
```

## ゲームでの使いどころ

自作のパーサーや電卓のような、字句解析で使います。数字や識別子は「どこまで続くか」が、1 文字先を見ないと分からないので、読みすぎた 1 文字を戻して、次のトークンの先頭として使います。

C++ のストリームでは、`std::istream::peek()` が、読まずに先を見る手段として使えます。`ungetc` は、`FILE*` を扱うコードで使います。

## よくあるミス

??? failure "2 文字以上続けて押し戻して、失敗する"
    保証されるのは 1 文字です。複数文字の先読みが要るなら、自分でバッファーを持ちます。

??? failure "押し戻したあとに `fseek` して、文字が消える"
    位置を動かすと、押し戻した文字は捨てられます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetc`](fgetc.md) | 1 文字読む |
| `std::istream::peek` | C++ のストリームで、読まずに次の文字を見る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読んだ 1 文字を押し戻す
    - [x] 保証されるのは 1 文字
    - [x] ファイルは変わらない

## 関連ページ

- [cpprefjp: std::ungetc](https://cpprefjp.github.io/reference/cstdio/ungetc.html)
- [cppreference: std::ungetc](https://en.cppreference.com/w/cpp/io/c/ungetc)

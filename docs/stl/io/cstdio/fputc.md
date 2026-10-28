---
title: std::fputc
summary: "ファイルに 1 文字を書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::fputc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルに 1 文字ずつ書き出したい。たとえば、自作のシリアライザーで、記号を 1 つずつ出力する。<strong>1 文字を書き出す</strong>のが `std::fputc` です。

!!! tip "ポイント"
    - `fputc(文字, ファイル)` の形。戻り値は、書いた文字。失敗は `EOF`
    - 文字は `int` で受け取り、`unsigned char` に変換して書く
    - 1 文字ごとに呼ぶと、まとめて書くより遅い
    - `putc` は同じ働きのマクロでもよい版

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fputc {#fputc}

```cpp
int fputc(int ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | `int` | 書き出す文字。`unsigned char` に変換されて書かれる |
| `stream` | `FILE*` | 書き出す先のファイル |

成功すると、書いた文字を `unsigned char` から `int` に直して返します。失敗すると `EOF` を返し、エラーの印を立てます。

1 文字ごとに関数を呼ぶので、数が多いと遅くなります。文字列は `fputs`、バイト列は `fwrite` でまとめて書きます。ただし、バッファーのおかげで、実際のディスクへの書き込みは、まとめて行われます。

読み込み用に開いたファイルに書こうとすると、失敗します。`"r"` で開いたファイルへの `fputc` は `EOF` を返します。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("out.txt", "w");
  for (char ch = 'A'; ch <= 'E'; ++ch) {
    std::fputc(ch, f);          // 1 文字ずつ書く
  }
  std::fputc('\n', f);
  std::fclose(f);

  std::FILE* in = std::fopen("out.txt", "r");
  char buf[16];
  std::fgets(buf, sizeof(buf), in);
  std::print("{}", buf);
  std::fclose(in);
}
```

```text title="実行結果"
ABCDE
```

## ゲームでの使いどころ

ごく単純な文字単位の出力に使います。まとまった量は `fputs` や `fwrite`、書式つきは `fprintf` を使うほうが自然です。

C のコードを読むときには、`putc` や `fputc` が出てきますが、新しく書く C++ では、`std::ofstream` の `put` や `<<` を使います。

## よくあるミス

??? failure "1 文字ずつ大量に書いて、遅くなる"
    `fwrite` でまとめて書きます。

??? failure "読み込み用に開いたファイルに書いて、失敗に気づかない"
    戻り値が `EOF` です。開くときのモードを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`putc`](putc.md) | 同じ働き |
| [`putchar`](putchar.md) | 標準出力に 1 文字 |
| [`fputs`](fputs.md) | 文字列を書き出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 文字を書き出す
    - [x] 失敗は `EOF`
    - [x] まとまった量は `fputs` や `fwrite`

## 関連ページ

- [cpprefjp: std::fputc](https://cpprefjp.github.io/reference/cstdio/fputc.html)
- [cppreference: std::fputc](https://en.cppreference.com/w/cpp/io/c/fputc)

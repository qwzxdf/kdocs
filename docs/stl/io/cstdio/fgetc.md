---
title: std::fgetc
summary: "ファイルから 1 文字を読む。"
order: 900
tags:
  - 入出力・文字列
---

# std::fgetc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

テキスト ファイルを 1 文字ずつ読んで、自作の字句解析（トークナイザー）に渡したい。行ごとでも、バイト数ごとでもなく、<strong>1 文字ずつ取り出す</strong>のが `std::fgetc` です。

!!! tip "ポイント"
    - 戻り値は `int`。文字は `unsigned char` の値として返り、終わりかエラーのときは `EOF`（負の値）
    - 戻り値を `char` に入れると、`EOF` と区別できなくなる。`int` で受ける
    - 1 回呼ぶごとに、読み込み位置が 1 つ進む
    - `getc` は同じ働きのマクロでもよい版。使い分けは気にしなくてよい

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fgetc {#fgetc}

```cpp
int fgetc(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 読み込むファイル |

次の 1 文字を、`unsigned char` として読み、それを `int` に変換して返します。終わりに達したか、エラーが起きたときは `EOF` を返します。`EOF` は、`char` では表せない負の値（ふつう -1）です。

ここで落とし穴になるのが、戻り値を `char` で受けることです。`char c = fgetc(f);` とすると、`EOF` の -1 と、バイト値 `0xFF` が、符号つきの `char` では同じ値になり、区別できなくなります。ファイルの途中の `0xFF` で、読み込みが止まったり、終わりが検出できずに無限ループになったりします。必ず `int c` で受けます。

位置は 1 文字ごとに進むので、先読みしたいときは、[`ungetc`](ungetc.md) で戻せます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("word.txt", "w");
  std::fputs("Hi!", out);
  std::fclose(out);

  std::FILE* f = std::fopen("word.txt", "r");
  int c;                                   // char ではなく int で受ける
  int count = 0;
  while ((c = std::fgetc(f)) != EOF) {
    std::println("{}: {}", count++, static_cast<char>(c));
  }
  std::println("EOF が返った: {}", c == EOF);
  std::fclose(f);
}
```

```text title="実行結果"
0: H
1: i
2: !
EOF が返った: true
```

## ゲームでの使いどころ

自作のパーサー（設定ファイルや、簡単なスクリプトの読み込み）で、1 文字ずつ先頭を見ながら、トークンに切り分けるときに使います。先読みが必要なら、`ungetc` と組み合わせます。

大量のデータを読むには遅いので、速さが要るときは、`fread` でまとめてメモリへ読み、メモリ上で 1 文字ずつ処理します。

## よくあるミス

??? failure "戻り値を `char` で受けて、`0xFF` で止まる、または止まらない"
    `int` で受けて、`EOF` と比べます。

??? failure "`EOF` の確認だけして、エラーを見落とす"
    `EOF` はエラーでも返ります。ループの後で `ferror` も調べます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`getc`](getc.md) | 同じ働き |
| [`getchar`](getchar.md) | 標準入力から 1 文字 |
| [`ungetc`](ungetc.md) | 読んだ 1 文字を戻す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 1 文字読む
    - [x] 戻り値は `int`（`EOF` と区別するため）
    - [x] 先読みは `ungetc`

## 関連ページ

- [cpprefjp: std::fgetc](https://cpprefjp.github.io/reference/cstdio/fgetc.html)
- [cppreference: std::fgetc](https://en.cppreference.com/w/cpp/io/c/fgetc)

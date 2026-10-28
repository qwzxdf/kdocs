---
title: EOF
summary: "ファイルの終端またはエラーを表す定数（負の整数）。"
order: 900
tags:
  - 入出力・文字列
---

# EOF

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

読み込み関数が「もう読めない」ことを、戻り値で伝えたい。ところが `fgetc` の戻り値は、`0` から `255` の文字の値です。どの値も文字として使われうるので、終わりを表す値に、文字の値は使えません。そこで、文字の範囲に入らない負の値を、`EOF` として定めています。

!!! tip "ポイント"
    - `EOF` は負の整数のマクロ。ふつうは `-1`
    - `fgetc` や `getchar` は、終わりかエラーのときに、これを返す
    - 戻り値を受ける変数は `char` ではなく `int`。`char` だと、`0xFF` の文字と区別できない
    - ファイルの終わりかエラーかは、`feof` と `ferror` で見分ける

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### EOF {#EOF}

```cpp
#define EOF (-1)   // 値は処理系定義の、負の整数定数
```

`EOF` の名前は End Of File ですが、読み込みのエラーでも返されます。「もう文字を返せない」ことを表す印と考えます。

値は規格で「負の整数定数」としか決まっておらず、ほとんどの環境で `-1` です。値に頼らず、名前で比較します。

`fgetc` が `0` から `255` の値を返せるように、戻り値は `int` です。`char` で受けると、符号つき `char` の環境では `0xFF` が `-1` に見えて、`EOF` と区別できなくなります。ファイルの途中の 1 バイトで、読み込みが止まってしまいます。

出力関数（`fputc`、`fputs` など）は、失敗したときに `EOF` を返します。入力の終わりという意味ではなく、「失敗」を表す値として使われます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("empty.txt", "w");
  std::fclose(f);

  f = std::fopen("empty.txt", "r");
  int c = std::fgetc(f);              // 空のファイルなので EOF
  std::println("EOF が返った: {}", c == EOF);
  std::println("EOF は負の値: {}", EOF < 0);
  std::println("feof: {}", std::feof(f) != 0);
  std::fclose(f);
}
```

```text title="実行結果"
EOF が返った: true
EOF は負の値: true
feof: true
```

## ゲームでの使いどころ

1 文字ずつ読むループの終了条件に使います。`while ((c = fgetc(f)) != EOF)` が、定番の書き方です。ループを抜けたあとで、`feof` と `ferror` を調べて、終わりなのかエラーなのかを区別します。

`scanf` 系の関数も、入力が終わった（1 つも読めなかった）とき `EOF` を返します。

## よくあるミス

??? failure "`char c = fgetc(f)` と書いて、`0xFF` で止まる"
    `int` で受けます。

??? failure "`EOF` の値が `-1` だと決めつけて、数値で比較する"
    名前で比較します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`feof`](feof.md) | 終わりの印を調べる |
| [`ferror`](ferror.md) | エラーの印を調べる |
| [`fgetc`](fgetc.md) | `EOF` を返す代表的な関数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 終わりやエラーを表す負の値
    - [x] 戻り値は `int` で受ける
    - [x] 名前で比較する

## 関連ページ

- [cpprefjp: EOF](https://cpprefjp.github.io/reference/cstdio/eof.html)
- [cppreference: EOF](https://en.cppreference.com/w/cpp/io/c/EOF)

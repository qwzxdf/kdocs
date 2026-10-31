---
title: std::wscanf
summary: "ワイド文字で、標準入力から書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::wscanf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cwchar>`
</div>

コンソールから、数値や単語を決まった書式で読み込みたい。`scanf` のワイド文字版が `wscanf` です。書式も、読む文字列も `wchar_t` で扱います。`scanf` 同様、書式を間違えたり、バッファの大きさを指定しなかったりすると、未定義動作になりやすい関数です。

標準入力から読むなら、`std::wcin` と `std::getline` のほうが安全です。

!!! tip "ポイント"
    - 戻り値は、読み込めた項目の数。入力が終わったとき（何も読めなかった）は `WEOF` か `EOF`
    - 変数には、アドレス（`&x`）を渡す。`&` を忘れると未定義動作
    - 文字列を読む `%ls` には、幅を付ける（`%31ls`）。付けないとあふれる
    - 文字列を安全に読むなら `std::wcin` と `std::wstring`

!!! info "このページを読む前に"
    [`std::wprintf`](wprintf.md) と、[`scanf`](../cstdio/scanf.md) を先に読んでください。

## 関数の詳しい説明

### std::wscanf {#wscanf}

```cpp
int wscanf(const wchar_t* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `format` | `const wchar_t*` | 書式文字列 |
| `...` | ポインタ | 読み込んだ値を入れる場所 |

書式の変換指定（`%d`、`%f`、`%ls` など）に従って、標準入力からワイド文字を読み、後ろの引数が指す変数に書き込みます。`%d` には `int*`、`%f` には `float*`、`%lf` には `double*` を渡します。

戻り値は、正しく読み込めて、変数に書き込めた項目の数です。`wscanf(L"%d %d", &a, &b)` で両方読めれば 2、最初の 1 つだけなら 1、何も読めなければ 0 です。入力の終わりに達したときは `EOF` を返します。

`%ls` で文字列を読むときの、配列の大きさの扱いが危険です。`wchar_t name[32]` に読むのに、`%ls` と書くと、入力が長ければ配列の外を壊します。`%31ls` のように、幅を最大の文字数（終端の分を引いた値）にします。

書式の空白は、入力の空白（改行も含む）を、いくつでも読み飛ばします。数値の変換に失敗したとき、入力の文字は読まれずに残るため、同じ書式で何度も呼ぶと、無限ループになります。

## 実際に動かしてみる

標準入力を使う関数なので、動かす代わりに、文字列から読む `swscanf` で、書式の働きを見ます。

```cpp
#include <cwchar>
#include <print>

int main() {
  int level = 0;
  double x = 0.0;
  wchar_t name[16] = {};

  // 書式の使い方は wscanf と同じ。入力が文字列になるだけ
  const int n = std::swscanf(L"7 2.5 Hero", L"%d %lf %15ls", &level, &x, name);

  std::println("読めた項目数: {}", n);
  std::println("level={} x={}", level, x);
  std::println("name == Hero: {}", std::wcscmp(name, L"Hero") == 0);
}
```

```text title="実行結果"
読めた項目数: 3
level=7 x=2.5
name == Hero: true
```

`%15ls` で、最大 15 文字までに制限しています。`name` の大きさ 16 から、終端の分を引いた値です。

## ゲームでの使いどころ

コンソールのツールや、開発中のデバッグ コマンドを読むくらいです。入力は 1 行ずつ `std::wcin` と `std::getline` で受け、`std::wistringstream` で分けるほうが、安全で間違えにくくなります。

## よくあるミス

??? failure "& を付け忘れる"
    `wscanf(L"%d", x)` は、`x` の値をアドレスとして書き込もうとして、クラッシュします。

??? failure "%ls に幅を付けない"
    入力が配列より長いと、あふれます。`%15ls` のように、幅を付けます。

??? failure "float に %lf を使う"
    `%f` が `float*`、`%lf` が `double*` です。取り違えると、値が壊れます。

## 類似

| 名前 | 違い |
| --- | --- |
| `swscanf` | 文字列から読む |
| `scanf` | `char` 版 |
| [`std::wcin`](../wcin.md) | C++ のワイド文字の標準入力。普段はこちら |

## コンパイラ対応

C++98 から使えます。MSVC は、`wscanf` に警告（C4996）を出し、`wscanf_s` を勧めます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `wscanf` は、ワイド文字の書式で標準入力から読む
    - [x] 変数のアドレスを渡し、`%ls` には幅を付ける
    - [x] 安全に読むなら `std::wcin` と `std::getline`

## 関連ページ

- [cpprefjp: wscanf](https://cpprefjp.github.io/reference/cwchar/wscanf.html)
- [cppreference: wscanf](https://en.cppreference.com/w/cpp/io/c/wscanf)

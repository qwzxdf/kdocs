---
title: std::sscanf
summary: "文字列から、書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::sscanf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

設定ファイルから読んだ 1 行 `"pos=10,20"` を、2 つの数値に分けたい。文字列を自分で切り分けるのは面倒です。`std::sscanf` は、<strong>文字列の中から、書式に沿って値を取り出す</strong>関数です。

!!! tip "ポイント"
    - `sscanf(文字列, 書式, &変数...)`。戻り値は、取り出せた項目の数
    - 値を入れる変数には、アドレス（`&x`）を渡す。忘れると、未定義動作
    - `%s` は幅の指定がないと、バッファーを溢れさせる。`%31s` のように幅を付ける
    - 戻り値が期待した数より少なければ、書式に合わなかったということ

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::sscanf {#sscanf}

```cpp
int sscanf(const char* buffer, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `buffer` | `const char*` | 読み取る元の文字列 |
| `format` | `const char*` | 書式文字列 |
| `...` | ポインター | 取り出した値を入れる変数のアドレス |

書式の中の `%d`、`%f`、`%s` などに対応する値を、文字列から順に取り出して、渡された変数に入れます。書式の中の空白は、文字列の側の空白（なくてもよい）に一致します。それ以外の文字（`=` や `,`）は、そのとおりに一致する必要があります。

戻り値は、<strong>取り出せた項目の数</strong>です。2 つ取り出すつもりで、1 が返れば、2 つ目の前で書式が合わなくなりました。値を使う前に、戻り値を確かめます。全く取り出せなかったときは 0 で、入力が最初から空など、取り出す前に終わったときは `EOF` です。

`%d` は、`int` へのポインターが要ります。`%f` は `float`、`%lf` は `double` です。`double` に `%f` を使うと、値が壊れます。

`%s` は、空白までを読み、<strong>幅の指定がないと、入力の長さの分だけ書き込みます</strong>。`char name[32]` なら `%31s` のように、大きさ - 1 を指定します。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  const char* line = "pos=10,20";
  int x = 0, y = 0;
  int n = std::sscanf(line, "pos=%d,%d", &x, &y);
  std::println("取り出せた数: {}  x={} y={}", n, x, y);

  // 書式に合わない文字列
  int a = 0;
  int m = std::sscanf("abc", "%d", &a);
  std::println("合わない場合: {}", m);

  // 文字列は幅を付ける
  char name[8];
  std::sscanf("hero 100", "%7s", name);
  std::println("名前: {}", name);
}
```

```text title="実行結果"
取り出せた数: 2  x=10 y=20
合わない場合: 0
名前: hero
```

## ゲームでの使いどころ

短い文字列から値を取り出す場面で使います。設定の行、コマンドライン引数、簡単なコマンド（`move 10 20`）のパースなどです。

C++ では、`std::from_chars`（C++17）が、数値の変換に高速で安全です。複数の値を取り出すなら `std::istringstream` や、自前の分割も選べます。`sscanf` は、書式がそのまま読める手軽さが利点です。

## よくあるミス

??? failure "戻り値を確かめずに、失敗した変数を使う"
    取り出せなかった変数は、書き換わりません。初期値のままか、不定です。

??? failure "`%s` に幅を付けず、バッファーを溢れさせる"
    `%31s` のように、大きさ - 1 の幅を付けます。

??? failure "`double` に `%f` を使って、値が壊れる"
    `double` には `%lf` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`scanf`](scanf.md) | 標準入力から取り出す |
| [`fscanf`](fscanf.md) | ファイルから取り出す |
| `std::from_chars` | C++17 の高速で安全な数値変換 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 文字列から書式で値を取り出す
    - [x] 戻り値は取り出せた数
    - [x] `%s` には幅を付ける

## 関連ページ

- [cpprefjp: std::sscanf](https://cpprefjp.github.io/reference/cstdio/sscanf.html)
- [cppreference: std::sscanf](https://en.cppreference.com/w/cpp/io/c/sscanf)

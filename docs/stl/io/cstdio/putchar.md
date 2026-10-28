---
title: std::putchar
summary: "標準出力に 1 文字を書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::putchar

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

画面（標準出力）に 1 文字だけ出したい。`putchar` は、`fputc(ch, stdout)` と同じです。

!!! tip "ポイント"
    - `putchar(c)` は `fputc(c, stdout)` と同じ。戻り値は書いた文字、失敗は `EOF`
    - 出力は行単位でバッファーされることがある。すぐ出したいなら `fflush(stdout)`
    - 改行は自動では付かない
    - C++23 では `std::print` が使えるので、新しいコードではそちらが楽

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::putchar {#putchar}

```cpp
int putchar(int ch);
```

標準出力に 1 文字を書き出します。引数は `int` ですが、`unsigned char` に変換されて出力されます。

標準出力は、端末につながっているときは<strong>行単位でバッファーされる</strong>のがふつうで、改行が出るまで画面に出ないことがあります。進捗を `\r` で上書きするような表示では、`fflush(stdout)` を呼んで、すぐ出します。

マルチバイト文字（日本語）を 1 文字ずつ `putchar` で出すと、バイトが分断されて、端末が正しく解釈できないことがあります。日本語は、文字列として、まとめて出します。

## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  const char* msg = "OK";
  for (const char* p = msg; *p; ++p) std::putchar(*p);
  std::putchar('\n');
}
```

```text title="実行結果"
OK
```

## ゲームでの使いどころ

ごく単純なコンソール出力で使います。進捗バーのような、1 文字ずつ伸びていく表示（`#` を出す）では、`putchar` と `fflush(stdout)` の組み合わせが手軽です。通常のログは `std::println` を使います。

## よくあるミス

??? failure "画面にすぐ出ないと思って悩む"
    行バッファリングのためです。`fflush(stdout)` を呼びます。

??? failure "日本語を 1 バイトずつ出して、文字化けする"
    文字列としてまとめて出します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputc`](fputc.md) | 任意のファイルに 1 文字 |
| [`puts`](puts.md) | 文字列と改行を出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準出力に 1 文字
    - [x] 改行は付かない
    - [x] すぐ出すなら `fflush(stdout)`

## 関連ページ

- [cpprefjp: std::putchar](https://cpprefjp.github.io/reference/cstdio/putchar.html)
- [cppreference: std::putchar](https://en.cppreference.com/w/cpp/io/c/putchar)

---
title: std::setbuf
summary: "ファイルのバッファを、自分で指定した配列にする（または無効にする）。"
order: 900
tags:
  - 入出力・文字列
---

# std::setbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`setvbuf` の簡易版です。自分で用意したバッファーを、ファイルに使わせたい、または、バッファーを無効にしたい、という単純な場面のために残されています。

!!! tip "ポイント"
    - `setbuf(ファイル, バッファー)`。`BUFSIZ` 以上の大きさの配列を渡す
    - `nullptr` を渡すと、バッファーなしになる
    - 戻り値はなく、成否は分からない
    - 新しいコードでは、方式と大きさを指定できる `setvbuf` を使う

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::setbuf {#setbuf}

```cpp
void setbuf(std::FILE* stream, char* buffer);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 設定するファイル |
| `buffer` | `char*` | 使うバッファー。大きさは `BUFSIZ` 以上。`nullptr` ならバッファーなし |

`buffer` が `nullptr` でないときは `setvbuf(stream, buffer, _IOFBF, BUFSIZ)` と同じ、`nullptr` のときは `setvbuf(stream, nullptr, _IONBF, 0)` と同じです。

戻り値がないので、設定が成功したか分かりません。大きさも [`BUFSIZ`](bufsiz.md) 固定です。方式や大きさを選びたい、失敗を確かめたい、という場合は `setvbuf` を使います。

C++ では、`setbuf` は、C の古いコードを移植するとき以外に、使う場面がありません。C++23 でも非推奨にはなっていませんが、`setvbuf` で十分です。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("unbuf.log", "w");
  std::setbuf(f, nullptr);          // バッファーなし
  std::fputs("A", f);

  std::FILE* peek = std::fopen("unbuf.log", "r");
  int c = std::fgetc(peek);
  std::println("すぐ読める: {}", c == 'A');
  std::fclose(peek);
  std::fclose(f);
}
```

```text title="実行結果"
すぐ読める: true
```

## ゲームでの使いどころ

古い C のコードの移植で、「`setbuf(stdout, NULL)` で標準出力のバッファーを切る」書き方に出会います。同じことは `setvbuf(stdout, nullptr, _IONBF, 0)` で書けます。

## よくあるミス

??? failure "`BUFSIZ` より小さい配列を渡して、メモリを壊す"
    `BUFSIZ` 以上の大きさが要ります。

??? failure "読み書きを始めた後に呼んで、効かない"
    最初の入出力の前に呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setvbuf`](setvbuf.md) | 方式と大きさを選べる。戻り値で成否も分かる |
| [`BUFSIZ`](bufsiz.md) | 既定のバッファーの大きさ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バッファーを指定するだけの簡易版
    - [x] `nullptr` でバッファーなし
    - [x] 新しくは `setvbuf`

## 関連ページ

- [cpprefjp: std::setbuf](https://cpprefjp.github.io/reference/cstdio/setbuf.html)
- [cppreference: std::setbuf](https://en.cppreference.com/w/cpp/io/c/setbuf)

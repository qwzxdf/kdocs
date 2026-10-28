---
title: std::putc
summary: "ファイルに 1 文字を書く（`fputc` と同じ）。"
order: 900
tags:
  - 入出力・文字列
---

# std::putc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fputc` と同じように、ファイルに 1 文字を書き出します。`getc` と `fgetc` の関係と同じで、規格が「`putc` はマクロでもよい」と許している点が違います。

!!! tip "ポイント"
    - `putc(文字, ファイル)` は `fputc` と同じ結果を返す
    - マクロの場合、引数の式が複数回評価されることがある
    - 現代のコンパイラでは `fputc` との速さの差はほとんどない
    - 迷ったら `fputc` を使う

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::putc {#putc}

```cpp
int putc(int ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | `int` | 書き出す文字 |
| `stream` | `FILE*` | 書き出す先のファイル |

動作は [`fputc`](fputc.md) と同じです。成功すれば書いた文字を、失敗すれば `EOF` を返します。

マクロ実装の場合、`putc(c++, f)` のように副作用のある式を渡すと、位置が複数回進むなどの不具合が起きえます。`ch` は変数にして渡します。

最近の標準ライブラリは、関数として実装していることが多く、実際に問題が起きる場面は少ないのですが、規格上は許されています。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("x.txt", "w");
  int r = std::putc('X', f);
  std::println("書いた文字: {}", static_cast<char>(r));
  std::fclose(f);
}
```

```text title="実行結果"
書いた文字: X
```

## ゲームでの使いどころ

`fputc` と同じ場面で使えます。既存のコードに出てきたら、`fputc` と同じものとして読みます。

## よくあるミス

??? failure "副作用のある式を渡す"
    変数に入れてから渡します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputc`](fputc.md) | 関数として必ず存在する版 |
| [`putchar`](putchar.md) | 標準出力専用 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fputc` と同じ
    - [x] マクロかもしれない
    - [x] 迷ったら `fputc`

## 関連ページ

- [cpprefjp: std::putc](https://cpprefjp.github.io/reference/cstdio/putc.html)
- [cppreference: std::putc](https://en.cppreference.com/w/cpp/io/c/putc)

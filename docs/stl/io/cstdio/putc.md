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

`fputc` と同じ働きです。C 言語ではマクロとして実装されることがあります。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::putc {#putc}

```cpp
int putc(int ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | int | 書く文字 |
| `stream` | FILE* | 書き込み先 |

- 戻り値: 書いた文字。失敗したら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::putc('B', f);
  std::rewind(f);
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
B
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 1 文字ずつ書く処理 |

## よくあるミス

??? failure "戻り値を確かめない"
    失敗したら `EOF` が返ります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputc`](fputc.md) | 同じ働き |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルに 1 文字を書く（`fputc` と同じ）
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::putc](https://cpprefjp.github.io/reference/cstdio/putc.html)
- [cppreference: std::putc](https://en.cppreference.com/w/cpp/io/c/putc)

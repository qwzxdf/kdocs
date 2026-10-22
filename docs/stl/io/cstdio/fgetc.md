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

ファイルから、1 バイトを `int` として読みます。終端やエラーのときは `EOF` が返るため、戻り値は `char` ではなく `int` で受けます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fgetc {#fgetc}

```cpp
int fgetc(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 読み込み元 |

- 戻り値: 読んだ文字（`unsigned char` を `int` にした値）。終端やエラーなら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("A", f);
  std::rewind(f);
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
A
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 1 文字ずつ読む処理 |

## よくあるミス

??? failure "戻り値を `char` で受ける"
    `char` で受けると、`EOF` と文字 `0xFF` が区別できなくなります。`int` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`getc`](getc.md) | マクロの場合がある |
| [`fgets`](fgets.md) | 1 行を読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルから 1 文字を読む
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fgetc](https://cpprefjp.github.io/reference/cstdio/fgetc.html)
- [cppreference: std::fgetc](https://en.cppreference.com/w/cpp/io/c/fgetc)

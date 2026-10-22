---
title: std::getc
summary: "ファイルから 1 文字を読む（`fgetc` と同じ）。"
order: 900
tags:
  - 入出力・文字列
---

# std::getc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fgetc` と同じ働きです。C 言語ではマクロとして実装されることがあり、引数が何度も評価される点が違いました。C++ では関数として扱われるので、`fgetc` との違いはありません。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::getc {#getc}

```cpp
int getc(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 読み込み元 |

- 戻り値: 読んだ文字。終端やエラーなら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("A", f);
  std::rewind(f);
  std::println("{}", static_cast<char>(std::getc(f)));
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
    `int` で受けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetc`](fgetc.md) | 同じ働き |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルから 1 文字を読む（`fgetc` と同じ）
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::getc](https://cpprefjp.github.io/reference/cstdio/getc.html)
- [cppreference: std::getc](https://en.cppreference.com/w/cpp/io/c/getc)

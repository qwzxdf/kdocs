---
title: std::fscanf
summary: "ファイルから、書式を指定して読み込む。"
order: 900
tags:
  - 入出力・文字列
---

# std::fscanf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`scanf` の、読み込み元の `FILE*` を指定できる版です。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fscanf {#fscanf}

```cpp
int fscanf(std::FILE* stream, const char* format, ...);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 読み込み元 |
| `format` | const char* | 書式文字列 |
| `...` | ポインタ | 読み込んだ値を入れる場所 |

- 戻り値: 読み込めた個数。入力が終わったら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("42 7", f);
  std::rewind(f);
  int a = 0;
  int b = 0;
  std::fscanf(f, "%d %d", &a, &b);
  std::println("{} {}", a, b);
  std::fclose(f);
}
```

```text title="実行結果"
42 7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | テキストの設定ファイルの数値を読む |

## よくあるミス

??? failure "戻り値を確かめない"
    戻り値が期待した個数でなければ、読み込みに失敗しています。

## 類似

| 名前 | 違い |
| --- | --- |
| [`scanf`](scanf.md) | 標準入力 |
| [`fgets`](fgets.md) | 1 行を読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルから、書式を指定して読み込む
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fscanf](https://cpprefjp.github.io/reference/cstdio/fscanf.html)
- [cppreference: std::fscanf](https://en.cppreference.com/w/cpp/io/c/fscanf)

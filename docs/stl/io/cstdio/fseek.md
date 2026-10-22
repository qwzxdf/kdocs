---
title: std::fseek
summary: "ファイルの読み書き位置を動かす。"
order: 900
tags:
  - 入出力・文字列
---

# std::fseek

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルの途中に飛んで、読み書きを続けたいときに使います。基準は `SEEK_SET`（先頭）・`SEEK_CUR`（現在位置）・`SEEK_END`（末尾）です。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fseek {#fseek}

```cpp
int fseek(std::FILE* stream, long offset, int origin);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |
| `offset` | long | 動かすバイト数 |
| `origin` | int | 基準（`SEEK_SET`・`SEEK_CUR`・`SEEK_END`） |

- 戻り値: 成功なら 0
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("abc", f);
  std::fseek(f, 1, SEEK_SET);
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
b
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | ファイルの途中から読む |

## よくあるミス

??? failure "読みから書きに切り替えるときに呼ばない"
    読み書きを切り替えるときは、間に `fseek` か `fflush` が必要です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ftell`](ftell.md) | 位置を取る |
| [`rewind`](rewind.md) | 先頭に戻る |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルの読み書き位置を動かす
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::fseek](https://cpprefjp.github.io/reference/cstdio/fseek.html)
- [cppreference: std::fseek](https://en.cppreference.com/w/cpp/io/c/fseek)

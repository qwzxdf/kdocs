---
title: SEEK_SET
summary: "`fseek` の基準：ファイルの先頭。"
order: 900
tags:
  - 入出力・文字列
---

# SEEK_SET

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fseek(f, offset, SEEK_SET)` は、ファイルの**先頭**から `offset` バイトの位置に動かします。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### SEEK_SET {#seek_set}

```cpp
#define SEEK_SET /* 実装定義 */
```

- 戻り値: 基準を表す整数
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("abc", f);
  std::fseek(f, 2, SEEK_SET);
  std::println("{}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
c
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 先頭から数えた位置に飛ぶ |

## よくあるミス

??? failure "負のオフセットを指定する"
    `SEEK_SET` では負の値は使えません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`SEEK_CUR`](seek_cur.md) | 現在位置 |
| [`SEEK_END`](seek_end.md) | 末尾 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fseek` の基準：ファイルの先頭
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: SEEK_SET](https://cpprefjp.github.io/reference/cstdio/seek_set.html)
- [cppreference: SEEK_SET](https://en.cppreference.com/w/cpp/io/c/SEEK_SET)

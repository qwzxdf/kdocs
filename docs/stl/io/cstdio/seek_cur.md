---
title: SEEK_CUR
summary: "`fseek` の基準：現在位置。"
order: 900
tags:
  - 入出力・文字列
---

# SEEK_CUR

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`fseek(f, offset, SEEK_CUR)` は、**現在の位置**から `offset` バイト動かします。負の値で戻れます。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### SEEK_CUR {#seek_cur}

```cpp
#define SEEK_CUR /* 実装定義 */
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
  std::rewind(f);
  std::fgetc(f);
  std::fseek(f, 1, SEEK_CUR);
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
| 使いどころ | いまの位置から読み飛ばす |

## よくあるミス

??? failure "テキストモードで使う"
    テキストモードでは、0 以外のオフセットが使えない環境があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`SEEK_SET`](seek_set.md) | 先頭 |
| [`SEEK_END`](seek_end.md) | 末尾 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fseek` の基準：現在位置
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: SEEK_CUR](https://cpprefjp.github.io/reference/cstdio/seek_cur.html)
- [cppreference: SEEK_CUR](https://en.cppreference.com/w/cpp/io/c/SEEK_CUR)

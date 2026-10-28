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

標準では、出力にバッファが付いています。`setbuf(stdout, nullptr)` でバッファを無効にすると、出力がすぐに書き出されます。デバッグ出力の順序を保つときなどに使います。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::setbuf {#setbuf}

```cpp
void setbuf(std::FILE* stream, char* buffer);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | FILE* | 対象のファイル |
| `buffer` | char* | `BUFSIZ` バイト以上の配列。`nullptr` ならバッファなし |

- 戻り値: なし
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::setbuf(stdout, nullptr);  // バッファを無効にする
  std::fputs("unbuffered\n", stdout);
}
```

```text title="実行結果"
unbuffered
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の順序をデバッグで確実にする |

## よくあるミス

??? failure "入出力を始めたあとに呼ぶ"
    最初の入出力の前に呼ぶ必要があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setvbuf`](setvbuf.md) | モードと大きさを選べる |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] ファイルのバッファを自分で指定した配列にする（または無効にする）
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::setbuf](https://cpprefjp.github.io/reference/cstdio/setbuf.html)
- [cppreference: std::setbuf](https://en.cppreference.com/w/cpp/io/c/setbuf)

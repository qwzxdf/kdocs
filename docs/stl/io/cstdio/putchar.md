---
title: std::putchar
summary: "標準出力に 1 文字を書く。"
order: 900
tags:
  - 入出力・文字列
---

# std::putchar

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

`putc(ch, stdout)` と同じです。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::putchar {#putchar}

```cpp
int putchar(int ch);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | int | 書く文字 |

- 戻り値: 書いた文字。失敗したら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>

int main() {
  std::putchar('X');
  std::putchar('\n');
}
```

```text title="実行結果"
X
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | コンソールに 1 文字を出す |

## よくあるミス

??? failure "戻り値を無視する"
    ふつうは無視してかまいませんが、エラー検出が必要なら確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fputc`](fputc.md) | ファイルへ |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 標準出力に 1 文字を書く
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::putchar](https://cpprefjp.github.io/reference/cstdio/putchar.html)
- [cppreference: std::putchar](https://en.cppreference.com/w/cpp/io/c/putchar)

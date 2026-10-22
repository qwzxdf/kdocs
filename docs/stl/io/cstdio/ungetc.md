---
title: std::ungetc
summary: "読んだ文字を 1 文字、ファイルに戻す。"
order: 900
tags:
  - 入出力・文字列
---

# std::ungetc

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

次の文字を見て、読むかどうかを決めたいときに、読んでから戻すことができます。戻せるのは、最低 1 文字までです。

!!! tip "ポイント"
    - C 由来の入出力関数。
    - 戻り値で失敗を調べる。
    - 新しいコードでは `std::print` や `std::ifstream` / `std::ofstream` が安全。

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::ungetc {#ungetc}

```cpp
int ungetc(int ch, std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `ch` | int | 戻す文字 |
| `stream` | FILE* | 戻す先 |

- 戻り値: 戻した文字。失敗したら `EOF`
- 計算量: 入出力の量に比例


## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::tmpfile();
  std::fputs("AB", f);
  std::rewind(f);
  int c = std::fgetc(f);
  std::ungetc(c, f);
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
| 使いどころ | 字句解析で、先読みした文字を戻す |

## よくあるミス

??? failure "2 文字以上戻す"
    保証されるのは 1 文字までです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fgetc`](fgetc.md) | 1 文字読む |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読んだ文字を 1 文字、ファイルに戻す
    - [x] C 由来の入出力関数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::ungetc](https://cpprefjp.github.io/reference/cstdio/ungetc.html)
- [cppreference: std::ungetc](https://en.cppreference.com/w/cpp/io/c/ungetc)

---
title: SEEK_END
summary: "`fseek` の基準：ファイルの末尾。"
order: 900
tags:
  - 入出力・文字列
---

# SEEK_END

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルの大きさを知りたい。末尾の数バイトだけを読みたい。どちらも、基準が<strong>末尾</strong>だと簡単です。そのための `fseek` の基準が `SEEK_END` です。

!!! tip "ポイント"
    - `fseek(f, 0, SEEK_END)` で、末尾へ移る。続けて `ftell` を呼ぶと、ファイルの大きさ
    - `fseek(f, -n, SEEK_END)` で、末尾から `n` バイト手前へ移る
    - バイナリの `SEEK_END` は、規格では保証されない（実際には、ほぼ動く）
    - C++17 以降は、大きさなら `std::filesystem::file_size` が簡単

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### SEEK_END {#SEEK_END}

```cpp
#define SEEK_END /* 整数定数 */
```

位置の基準を「ファイルの末尾」にします。`offset` が 0 なら末尾そのもの、負の値なら末尾から手前へ戻った位置です。

ファイルの大きさを調べる、古くからの定番手順は次のとおりです。

```cpp
std::fseek(f, 0, SEEK_END);
long size = std::ftell(f);
std::rewind(f);
```

末尾の数バイトが特別な意味を持つ形式（ZIP の末尾の目次など）を読むときにも使います。末尾から決まった長さだけ手前に飛んで、そこから読みます。

規格上、バイナリ ストリームでの `SEEK_END` の動作は、意味のある実装を保証していません（ファイルの末尾に余計な 0 が付く古いシステムを考慮したため）。現代の環境では、問題なく動きます。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("abc.txt", "w");
  std::fputs("ABCDEF", out);
  std::fclose(out);

  std::FILE* f = std::fopen("abc.txt", "rb");
  std::fseek(f, 0, SEEK_END);
  std::println("大きさ: {}", std::ftell(f));

  std::fseek(f, -2, SEEK_END);      // 末尾から 2 つ手前
  std::println("末尾から 2 つ手前: {}", static_cast<char>(std::fgetc(f)));
  std::fclose(f);
}
```

```text title="実行結果"
大きさ: 6
末尾から 2 つ手前: E
```

## ゲームでの使いどころ

ZIP のように、ファイルの末尾に目次を持つ形式を読むときに使います。末尾から固定長だけ戻って、目次の位置を読み取り、そこへ飛びます。

大きさを知るためだけなら、`std::filesystem::file_size` が簡単で、位置も動かしません。

## よくあるミス

??? failure "大きさを調べたあと、先頭に戻すのを忘れる"
    `rewind` か `fseek(f, 0, SEEK_SET)` で戻します。

??? failure "2 GB を超えるファイルで、`long` が足りない"
    `_fseeki64` や `_ftelli64` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`SEEK_SET`](seek_set.md) | 先頭を基準にする |
| [`SEEK_CUR`](seek_cur.md) | 今の位置を基準にする |
| [`file_size`](../filesystem/file_size.md) | 大きさだけを知るなら |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 末尾を基準にする
    - [x] 大きさは `SEEK_END` と `ftell`
    - [x] 戻すのを忘れない

## 関連ページ

- [cpprefjp: SEEK_END](https://cpprefjp.github.io/reference/cstdio/seek_end.html)
- [cppreference: SEEK_END](https://en.cppreference.com/w/cpp/io/c/SEEK_END)

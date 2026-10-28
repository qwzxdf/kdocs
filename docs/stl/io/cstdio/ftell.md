---
title: std::ftell
summary: "ファイルの現在位置を返す。"
order: 900
tags:
  - 入出力・文字列
---

# std::ftell

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ファイルのどこまで読んだか、どこに書いたかを知りたい。パックファイルに書いたアセットの位置を、目次に記録したい。<strong>今の読み書きの位置</strong>を、先頭からのバイト数で返すのが `std::ftell` です。

!!! tip "ポイント"
    - 戻り値は、先頭からのバイト数（`long`）。失敗すると `-1L`
    - `fseek(f, 0, SEEK_END)` の後に呼ぶと、ファイルの大きさになる
    - Windows では `long` が 32 ビットなので、2 GB を超える位置は表せない
    - テキスト モードでは、返る値は位置の目印であり、バイト数とは限らない

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::ftell {#ftell}

```cpp
long ftell(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 位置を調べるファイル |

読み書きの位置を、ファイルの先頭からのバイト数で返します。開いた直後は 0 で、`fread` や `fwrite` で進みます。追記モード（`"a"`）で開いたファイルは、書き込みのたびに末尾へ移るため、書く前に調べた位置は当てになりません。

失敗したときは `-1L` を返します。端末のような、位置を持たないものに使うと失敗します。

戻り値をそのまま `fseek` に渡すと、その位置に戻れます。パックファイルを書くとき、アセットを書く直前に `ftell` で位置を記録し、目次に残す、という使い方ができます。

2 GB を超える位置は `long`（Windows では 32 ビット）で表せません。`_ftelli64`（Windows）や `ftello`（POSIX）を使います。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("pack.bin", "wb");

  long pos1 = std::ftell(f);           // 最初のアセットの位置
  std::fwrite("AAAA", 1, 4, f);
  long pos2 = std::ftell(f);           // 2 つ目のアセットの位置
  std::fwrite("BBBBBB", 1, 6, f);
  long end = std::ftell(f);

  std::println("1 つ目: {} から", pos1);
  std::println("2 つ目: {} から", pos2);
  std::println("全体の大きさ: {}", end);
  std::fclose(f);
}
```

```text title="実行結果"
1 つ目: 0 から
2 つ目: 4 から
全体の大きさ: 10
```

## ゲームでの使いどころ

自作のパックファイルを書き出すツールで、各アセットの先頭位置を記録するときに使います。書く直前に `ftell` で位置を取り、書いた後の `ftell` との差が、アセットの大きさになります。目次は最後にまとめて書くか、先頭に空きを取っておいて、あとから書き戻します。

読み込みでは、ファイルを読み進めた量を知るのに使いますが、`fread` の戻り値を足し合わせるほうが、確実です。

## よくあるミス

??? failure "戻り値の `-1` を確かめずに、そのまま位置として使う"
    失敗の値です。`fseek` に渡すと、さらに失敗します。

??? failure "追記モードで、書く前の位置を使う"
    追記モードは、書き込みのたびに末尾へ移ります。書いた後の位置で考えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fseek`](fseek.md) | 位置を動かす |
| [`fgetpos`](fgetpos.md) | 位置を保存する。巨大なファイルにも使える |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 今の位置を先頭からのバイト数で返す
    - [x] 失敗は `-1L`
    - [x] 2 GB を超えるなら 64 ビット版

## 関連ページ

- [cpprefjp: std::ftell](https://cpprefjp.github.io/reference/cstdio/ftell.html)
- [cppreference: std::ftell](https://en.cppreference.com/w/cpp/io/c/ftell)

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

大きなファイルの途中にあるデータだけを読みたい。先頭から全部読んでいては遅いので、<strong>読み書きする位置を、ファイルの好きな場所に動かす</strong>のが `std::fseek` です。パックファイルから、特定のアセットの場所へ飛ぶときの基本の道具です。

!!! tip "ポイント"
    - `fseek(ファイル, 動かす量, 基準)` の形。基準は `SEEK_SET`（先頭）、`SEEK_CUR`（今の位置）、`SEEK_END`（末尾）
    - 戻り値は、成功なら 0、失敗なら 0 以外
    - ファイルの大きさを知るには、`SEEK_END` に動かして `ftell` を呼ぶ定番の手順がある
    - テキスト モードでは、動かせる量に制約がある。バイナリ モードで使う

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fseek {#fseek}

```cpp
int fseek(std::FILE* stream, long offset, int origin);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 位置を動かすファイル |
| `offset` | `long` | 基準から動かすバイト数。負の値で戻れる |
| `origin` | `int` | 基準。[`SEEK_SET`](seek_set.md)、[`SEEK_CUR`](seek_cur.md)、[`SEEK_END`](seek_end.md) のどれか |

`SEEK_SET` は先頭が基準で、`offset` は先頭からの位置です。`SEEK_CUR` は今の位置が基準で、`offset` が負なら戻ります。`SEEK_END` は末尾が基準で、`offset` が 0 なら末尾そのものです。

`long` は、Windows では 32 ビットなので、<strong>2 GB を超えるファイルでは使えません</strong>。大きなファイルを扱うなら、`_fseeki64`（Windows）や `fseeko`（POSIX）を使うか、`std::ifstream::seekg` を使います。

テキスト モードで開いたファイルでは、`offset` に、`ftell` が返した値か 0 しか使えません。`\r\n` の変換があるため、バイト数の計算が合わなくなるからです。位置を計算して飛ぶ処理は、`"rb"` で開いたバイナリ モードで行います。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* out = std::fopen("data.bin", "wb");
  std::fputs("0123456789", out);
  std::fclose(out);

  std::FILE* f = std::fopen("data.bin", "rb");

  std::fseek(f, 5, SEEK_SET);                 // 先頭から 5 バイト目へ
  std::println("先頭から 5: {}", static_cast<char>(std::fgetc(f)));

  std::fseek(f, -1, SEEK_END);                // 末尾の 1 つ前へ
  std::println("末尾の 1 つ前: {}", static_cast<char>(std::fgetc(f)));

  std::fseek(f, 0, SEEK_END);                 // 末尾に移動して大きさを知る
  std::println("大きさ: {}", std::ftell(f));
  std::fclose(f);
}
```

```text title="実行結果"
先頭から 5: 5
末尾の 1 つ前: 9
大きさ: 10
```

## ゲームでの使いどころ

パックファイル（複数のアセットを 1 つにまとめたファイル）の読み込みで使います。先頭の目次から、目的のアセットの位置と大きさを読み取り、`fseek` で位置に飛んでから `fread` で読み込みます。

ファイルの大きさを調べる定番の手順（末尾に動かして `ftell`）にも使いますが、C++17 以降なら、`std::filesystem::file_size` のほうが簡単です。

## よくあるミス

??? failure "2 GB を超えるファイルで失敗する"
    `long` が 32 ビットの環境（Windows）では、位置を表せません。64 ビット版の関数を使います。

??? failure "テキスト モードで位置を計算して、ずれる"
    `\r\n` の変換があり、バイト数が合いません。位置計算をするファイルは、バイナリ モードで開きます。

??? failure "戻り値を確かめずに、失敗に気づかない"
    範囲外に動かすなどで失敗します。0 以外が返ったら、読み書きを続けません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`ftell`](ftell.md) | 今の位置を調べる |
| [`rewind`](rewind.md) | 先頭に戻る |
| [`fgetpos`](fgetpos.md) | 位置を保存する。巨大なファイルにも使える |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 読み書きの位置を動かす
    - [x] 基準は先頭、今の位置、末尾
    - [x] 2 GB を超えるなら 64 ビット版

## 関連ページ

- [cpprefjp: std::fseek](https://cpprefjp.github.io/reference/cstdio/fseek.html)
- [cppreference: std::fseek](https://en.cppreference.com/w/cpp/io/c/fseek)

---
title: std::setvbuf
summary: "ファイルのバッファの方式（全部・行・なし）と大きさを設定する。"
order: 900
tags:
  - 入出力・文字列
---

# std::setvbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ログ ファイルを書き込むとき、行ごとにすぐディスクへ出したい場合と、まとめて効率よく出したい場合があります。標準ライブラリは、ファイルごとに「バッファリング」の方式を持っていて、それを選べるのが `std::setvbuf` です。

<strong>バッファーの方式と大きさを指定する</strong>関数で、ファイルを開いた直後、読み書きの前に呼びます。

!!! tip "ポイント"
    - 方式は 3 つ。`_IOFBF`（全体をバッファー）、`_IOLBF`（行ごとに出す）、`_IONBF`（バッファーなし）
    - ファイルを開いた直後、読み書きを始める前に呼ぶ
    - 戻り値は、成功なら 0
    - 渡したバッファーは、ファイルを閉じるまで生きていなければならない

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::setvbuf {#setvbuf}

```cpp
int setvbuf(std::FILE* stream, char* buffer, int mode, std::size_t size);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 設定するファイル |
| `buffer` | `char*` | 使うバッファー。`nullptr` なら、ライブラリが用意する |
| `mode` | `int` | `_IOFBF`、`_IOLBF`、`_IONBF` のどれか |
| `size` | `size_t` | バッファーの大きさ（バイト） |

`_IOFBF` は、バッファーが一杯になるまで溜めてから書き出します（フル バッファリング）。ディスクへのファイルの標準的な方式で、速さが出ます。`_IOLBF` は、改行が出るたびに書き出します（行バッファリング）。端末への出力の標準です。`_IONBF` は、バッファーを使わず、書くたびに出します。

`_IONBF` にすると、クラッシュしても、書いた分が残るので、デバッグ ログに向きます。そのぶん、書き込みの回数が増えて遅くなります。`stderr` が既定でバッファーなしなのは、この理由です。

`buffer` に自分の配列を渡す場合、その配列は、ファイルを閉じるまで有効でなければなりません。関数のローカル配列を渡して、関数を抜けたあとにファイルを使うと、壊れます。`nullptr` を渡して、ライブラリに任せるほうが安全です。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* f = std::fopen("debug.log", "w");

  // バッファーなし: 書いた分がすぐ OS に渡される
  int r = std::setvbuf(f, nullptr, _IONBF, 0);
  std::println("設定できた: {}", r == 0);

  std::fputs("start\n", f);

  // 閉じる前に別のハンドルで読んでも、書いた内容が見える
  std::FILE* peek = std::fopen("debug.log", "r");
  char buf[16] = {};
  std::fgets(buf, sizeof(buf), peek);
  std::print("読めた: {}", buf);
  std::fclose(peek);
  std::fclose(f);
}
```

```text title="実行結果"
設定できた: true
読めた: start
```

## ゲームでの使いどころ

クラッシュの原因を調べるデバッグ ログで、`_IONBF` にします。クラッシュ直前の行まで、確実にファイルに残るので、原因の特定に役立ちます。製品では、速さを優先して、通常のフル バッファリングに戻します。

コンソールへの出力で、改行なしの進捗表示を即座に出したいときも、`setvbuf(stdout, nullptr, _IONBF, 0)` が使えます。

## よくあるミス

??? failure "読み書きを始めた後に呼んで、効かない"
    最初の入出力の前に呼びます。

??? failure "ローカル配列を渡して、関数を抜けたあとに壊れる"
    ファイルを閉じるまで生きている配列を渡すか、`nullptr` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setbuf`](setbuf.md) | バッファーを指定するだけの簡易版 |
| [`fflush`](fflush.md) | その場で書き出す |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バッファリングの方式と大きさを決める
    - [x] 最初の入出力の前に呼ぶ
    - [x] デバッグ ログは `_IONBF`

## 関連ページ

- [cpprefjp: std::setvbuf](https://cpprefjp.github.io/reference/cstdio/setvbuf.html)
- [cppreference: std::setvbuf](https://en.cppreference.com/w/cpp/io/c/setvbuf)

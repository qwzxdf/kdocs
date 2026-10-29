---
title: std::unitbuf
summary: "出力のたびに、バッファをフラッシュする。"
order: 900
tags:
  - 入出力・文字列
---

# std::unitbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

プログラムが落ちる直前に書いたログが、画面にもファイルにも出ていない。出力が、バッファに溜まったまま、送り出される前にプロセスが終わったからです。`std::unitbuf` は、出力のたびにバッファを送り出す設定で、確実に残したいログのために使います。

!!! tip "ポイント"
    - 設定すると、`<<` による出力のたびに、フラッシュされる
    - `cerr` は、最初からこの設定がオン。`cout` と `clog` は、オフ
    - 戻すには `nounitbuf`
    - 出力のたびに送り出すので、大量に書くと遅くなる

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::unitbuf {#unitbuf}

```cpp
std::ios_base& unitbuf(std::ios_base& str);
std::ios_base& nounitbuf(std::ios_base& str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | `ios_base&` | 設定を変えるストリーム |

`unitbuf` は `str.setf(std::ios_base::unitbuf)` を呼び、`nounitbuf` は `str.unsetf(std::ios_base::unitbuf)` を呼びます。設定は、変えるまで残り続けます。

オンのあいだは、`<<` による 1 回の出力が終わるたびに、バッファが送り出されます。送り出すとは、バッファの中身を、書き込み先（画面、ファイル）に渡す処理で、`flush` を呼ぶのと同じです。1 文字ごとではなく、`<<` 1 回ごとです。

## 実際に動かしてみる

バッファが何回送り出されたかを、数えて確かめます。`stringbuf` を継承して、送り出しのとき呼ばれる `sync()` を数える小さなバッファを作ります。

```cpp
#include <iostream>
#include <print>
#include <sstream>

// flush（sync）が何回呼ばれたか数えるバッファ
struct CountingBuf : std::stringbuf {
  int syncs = 0;
  int sync() override { ++syncs; return std::stringbuf::sync(); }
};

int main() {
  CountingBuf buf;
  std::ostream os(&buf);

  os << "a" << "b" << "c";
  std::println("既定: {} 回", buf.syncs);

  buf.syncs = 0;
  os << std::unitbuf << "a" << "b" << "c" << std::nounitbuf;
  std::println("unitbuf: {} 回", buf.syncs);
}
```

```text title="実行結果"
既定: 0 回
unitbuf: 3 回
```

既定では、3 回書いても 1 度も送り出されません。`unitbuf` をオンにしたあとは、3 回の `<<` で、3 回送り出されています。

## ゲームでの使いどころ

クラッシュの調査に使うログを、ファイルに書くときです。ファイルへの出力は、通常、まとめて書き出されるので、クラッシュ直前の数行が失われます。ファイル ストリームに `unitbuf` を設定しておくと、1 行ごとに送り出されるので、落ちる直前まで残ります。

`cerr` は、最初から `unitbuf` がオンです。画面に出すだけなら、エラーを `cerr` に書くのが、いちばん簡単です。

その代わり、毎回ディスクに書きに行くため、遅くなります。毎フレーム大量のログを書く場所には、向きません。通常のログは溜めて書き、重大なエラーのときだけ `flush` を呼ぶ、という使い分けのほうが、速度を落とさずに済みます。

## よくあるミス

??? failure "`unitbuf` を付けたのに、ファイルに反映されない"
    設定したストリームと、書いているストリームが別です。ファイル用のストリーム（`ofstream`）自体に設定してください。`cout` に設定しても、ファイルには効きません。

??? failure "ログの出力が極端に遅くなった"
    `unitbuf` は、`<<` のたびに送り出します。ループの中で大量に書くときは、`nounitbuf` に戻して、まとめて書き、最後に `flush` します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`flush`](flush.md) | その場で 1 回だけ送り出す |
| [`endl`](endl.md) | 改行を書いて、その場で 1 回送り出す |
| [`cerr`](cerr.md) | 最初から `unitbuf` がオンのストリーム |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `unitbuf` は、`<<` のたびにバッファを送り出す設定。戻すのは `nounitbuf`
    - [x] クラッシュ直前までログを残したいときに使う。`cerr` は最初からオン
    - [x] 毎回送り出すので遅い。大量の出力には向かない

## 関連ページ

- [cpprefjp: std::unitbuf](https://cpprefjp.github.io/reference/ios/unitbuf.html)
- [cppreference: std::unitbuf](https://en.cppreference.com/w/cpp/io/manip/unitbuf)

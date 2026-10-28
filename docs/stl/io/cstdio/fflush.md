---
title: std::fflush
summary: "出力バッファの内容を、いまファイルに書き出す。"
order: 900
tags:
  - 入出力・文字列
---

# std::fflush

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cstdio>`
</div>

ログを `fprintf` で書き出したのに、ゲームがクラッシュしたら、最後の数行がファイルに残っていなかった。書き込みはすぐにはディスクへ行かず、メモリ上のバッファーに溜められ、まとめて書き出されるからです。

`std::fflush` は、<strong>バッファーに溜まっているデータを、今すぐ書き出す</strong>関数です。

!!! tip "ポイント"
    - 出力ストリームに対して、バッファーの内容を OS へ渡す
    - 戻り値は、成功なら 0、失敗なら `EOF`
    - OS がさらにキャッシュするので、ディスクに完全に届いたとは限らない
    - 入力ストリームに使うと未定義動作（`stdin` の入力を捨てる目的で使ってはいけない）

!!! info "このページを読む前に"
    [`std::printf`](printf.md) と [`std::fopen`](fopen.md) を先に読んでください。

## 関数の詳しい説明

### std::fflush {#fflush}

```cpp
int fflush(std::FILE* stream);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `stream` | `FILE*` | 書き出すファイル。`nullptr` を渡すと、開いているすべての出力ストリームが対象 |

出力用のバッファーに残っている分を、OS に渡します。`fclose` は、閉じる前にこの処理を自動で行うので、閉じるなら不要です。

`fflush` が成功しても、データが物理的なディスクにあるとは限りません。OS がさらに内部のキャッシュに持っている場合があります。電源が切れても残したい情報には、OS の機能（Windows の `FlushFileBuffers`、POSIX の `fsync`）まで呼びます。

ログ ファイルのように、クラッシュ時に最後まで残したいものでは、書くたびに `fflush` を呼ぶと、確実さが上がります。そのぶん、書き込みの回数が増えて遅くなるので、重要なログだけにします。

入力ストリーム（`stdin`）に `fflush` を使って、入力の読み残しを捨てる書き方は、標準では未定義動作です。MSVC では動くことがありますが、環境をまたぐと動きません。

## 実際に動かしてみる

```cpp
#include <cstdio>
#include <print>

int main() {
  std::FILE* log = std::fopen("crash.log", "w");
  std::fputs("起動\n", log);
  std::fflush(log);          // ここまでは、クラッシュしても残る

  // ここで別のハンドルから読むと、書いた内容が見える
  std::FILE* peek = std::fopen("crash.log", "r");
  char buf[32] = {};
  std::fgets(buf, sizeof(buf), peek);
  std::println("読めた: {}", buf);
  std::fclose(peek);

  std::fclose(log);
}
```

```text title="実行結果"
読めた: 起動
```

## ゲームでの使いどころ

クラッシュ ログに使います。致命的なエラーを書いた直後に `fflush` しておけば、その後に異常終了しても、ログが残ります。通常のログは、`fflush` を呼ばず、まとめて書き出して、速さを優先します。

標準出力に進捗を表示するときも使います。`stdout` は、行が完成するまで溜められることがあるので、改行なしの進捗表示（`\r` で上書きする表示）を出すなら、`fflush(stdout)` で、すぐ表示させます。

## よくあるミス

??? failure "`fflush(stdin)` で入力を捨てようとする"
    標準では未定義です。入力の読み残しは、`getchar` などで読み捨てます。

??? failure "`fflush` で、ディスクに確実に届いたと考える"
    OS のキャッシュに残っていることがあります。電源断にも耐えるなら、OS の関数まで使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fclose`](fclose.md) | バッファーを書き出して閉じる |
| [`setvbuf`](setvbuf.md) | バッファリングの方式を変える |
| `std::flush` | C++ のストリームでの同等の操作 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バッファーを今すぐ書き出す
    - [x] 入力ストリームには使わない
    - [x] ディスクへの到達までは保証しない

## 関連ページ

- [cpprefjp: std::fflush](https://cpprefjp.github.io/reference/cstdio/fflush.html)
- [cppreference: std::fflush](https://en.cppreference.com/w/cpp/io/c/fflush)

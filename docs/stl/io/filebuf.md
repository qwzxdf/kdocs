---
title: std::filebuf
summary: "ファイルへの読み書きを担当するストリームバッファ。"
order: 900
tags:
  - 入出力・文字列
---

# std::filebuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <fstream>`
</div>

`std::ofstream` で書いたファイルは、実際にはどこで書かれているのでしょうか。`ofstream` の中には、`filebuf` という部品が入っていて、ファイルを開き、文字を溜め、閉じるときに書き出すのは、この `filebuf` です。`ofstream` は、`filebuf` に値を整形して渡す窓口にすぎません。

普段は `ofstream` や `ifstream` を使うので、`filebuf` を直接見ることはありません。`rdbuf()` で取り出すと、ストリームの出力先を付け替えたり、ファイルの中身を別のストリームに丸ごと流したりできます。

!!! tip "ポイント"
    - `ifstream`・`ofstream`・`fstream` の内部にある。`rdbuf()` で取り出せる
    - `open`、`close`、`is_open` がある。ストリームの `open` はこれを呼ぶだけ
    - `out << in.rdbuf()` で、ファイルの中身を丸ごと別のストリームへ流せる
    - ファイルを `cout` に表示したいときにも使える

!!! info "このページを読む前に"
    [`std::basic_streambuf`](basic_streambuf.md) でストリームバッファの役割を、[`std::ofstream`](ofstream.md) でファイルのストリームの使い方を先に読んでください。

## 関数の詳しい説明

### std::filebuf {#filebuf}

```cpp
using filebuf = basic_filebuf<char>;
```

`basic_streambuf` を継承した、ファイル用のバッファです。`char` 版が `filebuf`、`wchar_t` 版が `wfilebuf` です。

入出力は、C の `FILE*` とは別の、`filebuf` 自身のバッファを通ります。書いた内容は、バッファが満杯になるか、`close` や `flush` が呼ばれるまで、ファイルに届かないことがあります。

### open と close {#open-close}

```cpp
std::filebuf* open(const char* filename, std::ios_base::openmode mode);
std::filebuf* close();
bool is_open() const;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `filename` | `const char*` / `std::string` / `std::filesystem::path` | 開くファイル |
| `mode` | `std::ios_base::openmode` | `in`、`out`、`app`、`trunc`、`binary` の組み合わせ |

`open` は、成功したら `this` を、失敗したら `nullptr` を返します。ストリームの `open` と違い、例外も失敗状態も使わないので、戻り値を見て判断します。すでに開いているときに `open` を呼ぶと、失敗です。

`mode` に `out` だけを指定すると、`trunc` が付いたものとして、ファイルの中身を捨てます。追記したいときは `app` を付けます。Windows では、`binary` を付けないと、`\n` が `\r\n` に変換されます。

`close` は、バッファの残りを書き出してから閉じます。デストラクターも呼ぶので、書き忘れはありません。

## 実際に動かしてみる

```cpp
#include <filesystem>
#include <fstream>
#include <print>
#include <string_view>

int main() {
  const char* path = "filebuf_sample.txt";

  std::filebuf fb;
  std::println("開く前: {}", fb.is_open());

  fb.open(path, std::ios::out | std::ios::trunc | std::ios::binary);
  std::println("開いた後: {}", fb.is_open());
  fb.sputn("hello", 5);  // 5 文字書く
  fb.close();            // バッファを書き出して閉じる

  fb.open(path, std::ios::in | std::ios::binary);
  char buf[8] = {};
  const auto n = fb.sgetn(buf, 8);  // 最大 8 文字読む
  fb.close();
  std::println("{} 文字: {}", n, std::string_view(buf, static_cast<size_t>(n)));

  std::filesystem::remove(path);
}
```

```text title="実行結果"
開く前: false
開いた後: true
5 文字: hello
```

`sputn` と `sgetn` は、`ostream` の `write` と `istream` の `read` の元になる関数です。`binary` を付けて、改行の変換が起きないようにしています。

## ゲームでの使いどころ

ファイルの中身を、別のストリームにそのまま流したいときに便利です。

```cpp
std::ifstream in("log.txt");
std::cout << in.rdbuf();   // ファイルの中身を全部、画面に出す
```

`in.rdbuf()` が返す `filebuf*` を `<<` に渡すと、終端までを丸ごとコピーします。1 文字ずつ読む処理を書く必要はありません。ただし、ファイルが空だと、`cout` が失敗状態になります。

## よくあるミス

??? failure "空のファイルで out << in.rdbuf() すると、出力が止まる"
    読む文字が 1 つもないと、`<<` が失敗扱いになり、`cout` の `failbit` が立ちます。以降の出力が全部無視されます。`cout.clear()` で戻すか、`in.peek() != EOF` で空でないことを確かめてから流します。

??? failure "バッファの書き出しを忘れて、ファイルが空のまま"
    プログラムが `close` もデストラクターも通らずに終わると、最後の分が書かれません。異常終了の直前まで確実に残したいログは、`flush` を呼びます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stringbuf`](stringbuf.md) | メモリ上の文字列を入出力先にする |
| [`std::ofstream`](ofstream.md) | `filebuf` を内部に持つ、書き込み用のストリーム |
| [`std::ifstream`](ifstream.md) | 同じく、読み込み用 |
| [`std::basic_streambuf`](basic_streambuf.md) | 親クラス |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `filebuf` は、`ofstream` などの内部にある、ファイルを担当するバッファ
    - [x] `open` は失敗すると `nullptr` を返す。例外は投げない
    - [x] `out << in.rdbuf()` で、ファイルの中身を丸ごと流せる

## 関連ページ

- [cpprefjp: std::filebuf](https://cpprefjp.github.io/reference/fstream/basic_filebuf.html)
- [cppreference: std::filebuf](https://en.cppreference.com/w/cpp/io/basic_filebuf)

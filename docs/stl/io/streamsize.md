---
title: std::streamsize
summary: "ストリームで読み書きする文字数を表す符号付き整数型。"
order: 900
tags:
  - 入出力・文字列
---

# std::streamsize

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <ios>`
</div>

`read(buf, n)` に渡す `n` や、`gcount()` が返す「読んだ文字数」は、何の型でしょうか。`int` でも `size_t` でもなく、`std::streamsize` という専用の型です。符号付きの整数で、入出力で扱う文字数の大きさを表します。

!!! tip "ポイント"
    - 入出力の文字数を表す、符号付きの整数型
    - `read`・`write`・`gcount`・`precision`・`width` などの引数と戻り値に出てくる
    - `size_t`（符号なし）と混ぜると、符号の比較で警告が出る
    - 最大値は `std::numeric_limits<std::streamsize>::max()`。`ignore` に「行末まで全部」を頼むときに使う

!!! info "このページを読む前に"
    [`std::ios_base`](ios_base.md) を先に読んでください。

## 関数の詳しい説明

### std::streamsize {#streamsize}

```cpp
using streamsize = /* 実装定義の符号付き整数型 */;
```

`<ios>` で定義されます。実装が決める符号付き整数型で、64 ビット版の MSVC では 8 バイト（`long long`）です。

符号付きなのは、エラーを表す負の値を返せるようにするためです。たとえば `std::streambuf` の一部の関数は、失敗したときに `-1` を返します。一方、C の `size_t` は符号なしなので、`-1` は巨大な正の値になります。

## 実際に動かしてみる

```cpp
#include <ios>
#include <limits>
#include <print>
#include <sstream>
#include <string>
#include <type_traits>

int main() {
  std::println("streamsize: {} バイト、符号付き={}", sizeof(std::streamsize), std::is_signed_v<std::streamsize>);

  std::istringstream in("0123456789\nabc\n");
  char skip[4];
  in.read(skip, 4);
  std::streamsize n = in.gcount();        // 読んだ文字数
  std::println("gcount={}", static_cast<long long>(n));

  // 最大値を渡して、改行まで読み捨てる
  in.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
  std::string line;
  std::getline(in, line);
  std::println("2 行目: {}", line);
}
```

```text title="実行結果"
streamsize: 8 バイト、符号付き=true
gcount=4
2 行目: abc
```

`in.read(skip, 4)` の 4 は `streamsize` で、`gcount()` も `streamsize` を返します。`ignore` の第 1 引数に `numeric_limits<streamsize>::max()` を渡すと、「文字数の上限なし」で、区切り文字（ここでは `'\n'`）まで読み捨てます。行の残りを捨てて、次の行から読みたいときの、定番の書き方です。

## ゲームでの使いどころ

ファイルの読み込みで、バイナリのデータを `read` で読むとき、サイズを `streamsize` で渡します。ファイル全体を読むために、ファイルの大きさ（`std::filesystem::file_size` は `uintmax_t`）を `read` に渡すとき、型を合わせる `static_cast` が要ります。

設定ファイルのパーサーで、コメント行を捨てる `ignore(max, '\n')` もよく書きます。

## よくあるミス

??? failure "`int` で受けて、大きなファイルで桁あふれした"
    `gcount()` や `streamsize` の値を `int` に入れると、2 GB を超えたとき、桁があふれます。`auto` か `std::streamsize` で受けます。

??? failure "`size_t` と比べて、符号の警告が出る"
    `streamsize` は符号付き、`size_t` は符号なしです。比べる前に、どちらかを `static_cast` で合わせます。負の値を比べる可能性があるなら、`streamsize` に合わせるのが安全です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`streamoff`](streamoff.md) | ストリーム上の位置のずれ（オフセット）を表す整数型 |
| [`streampos`](streampos.md) | ストリーム上の位置を表す型 |
| `size_t` | メモリ上の大きさを表す符号なしの整数型 |

## コンパイラ対応

C++98 から使えます。手元の MSVC（Visual Studio 2026）で動作を確かめました。型の大きさは処理系で違います。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `streamsize` は、入出力の文字数を表す符号付きの整数型
    - [x] `gcount()`、`read`、`ignore` の引数や戻り値に出てくる
    - [x] `size_t` と混ぜるときは、`static_cast` で符号を合わせる

## 関連ページ

- [cpprefjp: std::streamsize](https://cpprefjp.github.io/reference/ios/streamsize.html)
- [cppreference: std::streamsize](https://en.cppreference.com/w/cpp/io/streamsize)

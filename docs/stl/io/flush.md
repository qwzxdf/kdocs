---
title: std::flush
summary: "出力のバッファにたまった中身を、すぐ書き出す。"
order: 75
tags:
  - 入出力・文字列
---

# std::flush

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ostream>`
</div>

出力は、ストリームのバッファーに溜められてから、まとめて書き出されます。プロンプトを出して入力を待つとき、「>」が画面に出てこない。クラッシュの直前のログが、ファイルに残っていない。そんなときは、溜まっている内容を今すぐ書き出す必要があります。それが `std::flush` です。

!!! tip "ポイント"
    - `std::cout << std::flush` で、バッファーの内容を今すぐ書き出す
    - 改行は出さない。`endl` から改行を除いたもの
    - `os.flush()` と同じ。`<<` でつなげて書ける
    - 対話型の入出力、クラッシュ ログ、進捗表示で使う

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::flush {#flush}

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& flush(std::basic_ostream<CharT, Traits>& os);
```

`os.flush()` を呼ぶ操作子です。バッファーに溜まっている出力を、OS に渡します。

`std::cout` は、`std::cin` から読む前に、自動で書き出されるように結び付けられています（`cin.tie()`）。そのため、普通の対話型プログラムでは、プロンプトの `flush` を意識する必要はありません。必要になるのは、ファイルのストリームや、改行のない進捗表示（`\r` で上書きする表示）などです。

`flush` が成功しても、データがディスクに物理的に届いたとは限りません。OS のキャッシュに残っていることがあります。電源断にも耐えたい書き込みには、OS の機能（`FlushFileBuffers` や `fsync`）まで使います。

C++20 の `std::osyncstream` を使うと、複数のスレッドからの出力が混ざらないよう、まとめて書き出せます（[`emit_on_flush`](emit_on_flush.md) も参照）。

## 実際に動かしてみる

```cpp
#include <fstream>
#include <iostream>
#include <string>

int main() {
  std::ofstream log("crash.log");
  log << "starting..." << std::flush;   // 改行なしで、すぐ書き出す

  std::ifstream peek("crash.log");
  std::string line;
  std::getline(peek, line);
  std::cout << "別のハンドルから読めた: " << line << '\n';
}
```

```text title="実行結果"
別のハンドルから読めた: starting...
```

## ゲームでの使いどころ

クラッシュの原因を調べるためのログで、書いた直後に `flush` しておくと、直後にクラッシュしても内容が残ります。進捗を `\r` で上書き表示するときも、`flush` で即座に見せます。

## よくあるミス

??? failure "毎回 `flush` して、出力が遅くなる"
    必要な行だけにします。

??? failure "`flush` したから、ディスクに確実に届いたと思う"
    OS のキャッシュに残る場合があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`endl`](endl.md) | 改行 + 書き出し |
| [`ends`](ends.md) | `'\0'` を出す |
| [`unitbuf`](unitbuf.md) | 毎回、自動で書き出す設定 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] バッファーを今すぐ書き出す
    - [x] 改行は出さない
    - [x] `endl` は改行も出す

## 関連ページ

- [cpprefjp: std::flush](https://cpprefjp.github.io/reference/ostream/flush.html)
- [cppreference: std::flush](https://en.cppreference.com/w/cpp/io/manip/flush)

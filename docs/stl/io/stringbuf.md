---
title: std::stringbuf
summary: "メモリ上の文字列への読み書きを担当するストリームバッファ。"
order: 900
tags:
  - 入出力・文字列
---

# std::stringbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <sstream>`
</div>

`cout` に出す予定だった文字を、テストで確かめたい。ファイルを作らずに、メモリの上だけで書いて読みたい。そんなとき、出力先に使えるのが `stringbuf` です。`std::stringstream` の内部にいる部品で、書き込まれた文字を `std::string` の形で溜めておき、`str()` で取り出せます。

`stringbuf` を直接使う場面は少なく、たいていは `stringstream` を使います。それでも `rdbuf()` と組み合わせると、`cout` の出力を一時的に横取りできます。

!!! tip "ポイント"
    - `stringstream` の内部にある。`rdbuf()` で取り出せる
    - `str()` で溜まった文字列を取り出し、`str("...")` で中身を入れ替える
    - `cout.rdbuf(sb.rdbuf())` で、`cout` の出力を文字列として取り込める。戻すのを忘れない
    - 読む位置と書く位置が別々。書いたあとに先頭から読める

!!! info "このページを読む前に"
    [`std::basic_streambuf`](basic_streambuf.md) でストリームバッファの役割を、[`std::stringstream`](stringstream.md) で文字列ストリームの使い方を先に読んでください。

## 関数の詳しい説明

### std::stringbuf {#stringbuf}

```cpp
using stringbuf = basic_stringbuf<char>;
```

`basic_streambuf` を継承した、メモリ上の文字列用のバッファです。`char` 版が `stringbuf`、`wchar_t` 版が `wstringbuf` です。

作るとき、初期の文字列を渡せます（`std::stringbuf sb("abc");`）。モードを省略すると、読み書きの両方が使えます。`std::ios::in` だけを指定すると、読み取り専用になります。

### str {#str}

```cpp
std::string str() const;
void str(const std::string& s);
```

引数なしの `str()` は、いま溜まっている文字列のコピーを返します。引数ありの `str(s)` は、バッファの中身を `s` に入れ替えて、読み書きの位置を先頭に戻します。

`str()` はコピーを返すので、大きな文字列を何度も取り出すと、そのたびにコピーが起きます。C++20 では、右辺値で取り出す `std::move(sb).str()` が使え、コピーしません。C++20 の `view()` は、コピーせずに `string_view` を返します。

## 実際に動かしてみる

```cpp
#include <print>
#include <sstream>

int main() {
  std::stringbuf sb("abc");  // 初期の文字列
  std::println("読める文字数: {}", sb.in_avail());
  std::println("先頭の文字: {}", static_cast<char>(sb.sgetc()));

  std::ostream os(&sb);  // sb を出力先にするストリーム
  os << "XYZ";
  std::println("str(): {}", sb.str());
}
```

```text title="実行結果"
読める文字数: 3
先頭の文字: a
str(): XYZ
```

初期値を `abc` で作ると、書き込みは先頭から上書きされます。`XYZ` を書いたので、`str()` は `XYZ` になりました。もとの文字列の続きに足したいときは、`std::ios::ate` か `app` を付けて作ります。

## ゲームでの使いどころ

`cout` の出力を文字列として取り込み、テストで検査するのが定番です。

```cpp
std::stringbuf captured;
auto* old = std::cout.rdbuf(&captured);  // 出力先を差し替える
Run();                                   // 内部で cout に出す関数
std::cout.rdbuf(old);                    // 必ず戻す
std::println("{}", captured.str());
```

スコープから抜けたときに自動で戻したいなら、デストラクターで元に戻す小さなクラスを書くと、途中で例外が出ても安全です。

## よくあるミス

??? failure "元に戻さずに stringbuf を破棄する"
    `cout.rdbuf(&sb)` のまま `sb` が消えると、`cout` が存在しないバッファを指します。プログラムの終了時にクラッシュします。付け替えたら、同じスコープで元に戻します。

??? failure "初期値を渡して作ったのに、書くと上書きされる"
    `std::stringbuf sb("abc")` で作って書くと、先頭から上書きします。続きに足すなら、`std::stringbuf sb("abc", std::ios::out | std::ios::ate)` のように、モードを付けます。

??? failure "str() を何度も呼んで遅くなる"
    `str()` は毎回コピーを作ります。大きなログを、ループの中で毎回取り出すと、時間がかかります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::stringstream`](stringstream.md) | `stringbuf` に `<<` と `>>` を付けたもの。普段はこちら |
| [`std::filebuf`](filebuf.md) | ファイルを入出力先にする |
| [`std::spanbuf`](spanbuf.md) | 自分で用意したメモリ領域を使う。確保しない |
| [`std::basic_streambuf`](basic_streambuf.md) | 親クラス |

## コンパイラ対応

C++98 から使えます。`view()` と、`str()` の右辺値版は C++20 以降です。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `stringbuf` は、メモリ上の文字列を入出力先にするバッファ
    - [x] `str()` で取り出し、`str(s)` で入れ替える
    - [x] `cout.rdbuf(...)` で出力を横取りしたら、必ず元に戻す

## 関連ページ

- [cpprefjp: std::stringbuf](https://cpprefjp.github.io/reference/sstream/basic_stringbuf.html)
- [cppreference: std::stringbuf](https://en.cppreference.com/w/cpp/io/basic_stringbuf)

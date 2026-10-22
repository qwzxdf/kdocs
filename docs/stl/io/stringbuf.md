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
`#include <streambuf>`
</div>

`stringstream` の裏にあるのが `stringbuf` です。`cout` の出力先を一時的に `stringbuf` に付け替えると、出力を文字列として取り込めます（テストで便利）。

!!! tip "ポイント"
    - ストリームの裏で実際に読み書きを行う。
    - `rdbuf()` で取り出し・付け替えができる。
    - 自作するときは、`underflow`・`overflow` などを書く。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::stringbuf {#stringbuf}

```cpp
using stringbuf = basic_stringbuf<char>;  // 実際は派生クラス
```

- 戻り値: ストリームバッファとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <ios>
#include <print>
#include <sstream>
#include <streambuf>
#include <fstream>

int main() {
  std::stringbuf sb;
  std::ostream os(&sb);
  os << "hello";
  std::println("{}", sb.str());
}
```

```text title="実行結果"
hello
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| `cout` の出力を文字列として取り込む | `auto* old = std::cout.rdbuf(sb.rdbuf());` のあと、`std::cout.rdbuf(old);` で戻す |

## よくあるミス

??? failure "付け替えたまま戻さない"
    `rdbuf` で付け替えたら、スコープを抜ける前に必ず元に戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`streambuf`](streambuf.md) | char 版の別名 |
| [`stringstream`](stringstream.md) | 文字列ストリーム |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] メモリ上の文字列への読み書きを担当するストリームバッファ
    - [x] rdbuf() で付け替えられる
    - [x] 自作の土台にもなる

## 関連ページ

- [cpprefjp: std::stringbuf](https://cpprefjp.github.io/reference/streambuf/stringbuf.html)
- [cppreference: std::stringbuf](https://en.cppreference.com/w/cpp/io/stringbuf)

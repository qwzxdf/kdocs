---
title: std::basic_streambuf
summary: "ストリームバッファの元になるテンプレート（`streambuf` の元）。"
order: 900
tags:
  - 入出力・文字列
---

# std::basic_streambuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <streambuf>`
</div>

ストリームは、文字の入出力の窓口です。実際にファイルや文字列に読み書きするのは、その裏にある「ストリームバッファ」です。`std::streambuf` は `basic_streambuf<char>` の別名で、自作のバッファ（ネットワークやログ）を作るときの土台になります。

!!! tip "ポイント"
    - ストリームの裏で実際に読み書きを行う。
    - `rdbuf()` で取り出し・付け替えができる。
    - 自作するときは、`underflow`・`overflow` などを書く。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::basic_streambuf {#basic_streambuf}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class basic_streambuf;
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
  std::stringbuf buf("ab");
  std::basic_streambuf<char>* p = &buf;
  std::println("{}", static_cast<char>(p->sgetc()));
}
```

```text title="実行結果"
a
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
    - [x] ストリームバッファの元になるテンプレート（`streambuf` の元）
    - [x] rdbuf() で付け替えられる
    - [x] 自作の土台にもなる

## 関連ページ

- [cpprefjp: std::basic_streambuf](https://cpprefjp.github.io/reference/streambuf/basic_streambuf.html)
- [cppreference: std::basic_streambuf](https://en.cppreference.com/w/cpp/io/basic_streambuf)

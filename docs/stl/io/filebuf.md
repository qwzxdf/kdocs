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
`#include <streambuf>`
</div>

`ifstream`・`ofstream`・`fstream` の裏にあるのが `filebuf` です。`rdbuf()` で取り出して、別のストリームに付け替えると、出力先を切り替えられます。

!!! tip "ポイント"
    - ストリームの裏で実際に読み書きを行う。
    - `rdbuf()` で取り出し・付け替えができる。
    - 自作するときは、`underflow`・`overflow` などを書く。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::filebuf {#filebuf}

```cpp
using filebuf = basic_filebuf<char>;  // 実際は派生クラス
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
  std::filebuf fb;
  std::println("{}", fb.is_open());
}
```

```text title="実行結果"
false
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
    - [x] ファイルへの読み書きを担当するストリームバッファ
    - [x] rdbuf() で付け替えられる
    - [x] 自作の土台にもなる

## 関連ページ

- [cpprefjp: std::filebuf](https://cpprefjp.github.io/reference/streambuf/filebuf.html)
- [cppreference: std::filebuf](https://en.cppreference.com/w/cpp/io/filebuf)

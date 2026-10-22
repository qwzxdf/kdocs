---
title: std::spanbuf
summary: "`span` の上にあるメモリを使うストリームバッファ。"
order: 900
tags:
  - 入出力・文字列
---

# std::spanbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <spanstream>`
</div>

`ispanstream` と `ospanstream` の裏にある、ストリームバッファです。固定のバッファに対して、読み書きを行います。直接使うことは少なく、`ispanstream`・`ospanstream` を使います。

!!! tip "ポイント"
    - コピーやヒープ確保が起きない。
    - バッファは自分で用意し、生きている間だけ使える。
    - C++23 の機能。

!!! info "このページを読む前に"
    [`std::spanstream`](spanstream.md) を先に読んでください。

## 関数の詳しい説明

### std::spanbuf {#spanbuf}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class basic_spanbuf;
using spanbuf = basic_spanbuf<char>;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <print>
#include <span>
#include <spanstream>

int main() {
  char buf[8] = "abc";
  std::spanbuf sb{std::span<char>(buf)};
  std::println("{}", sb.span().size());
}
```

```text title="実行結果"
8
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定のバッファを解析・書き込みする | `std::spanbuf` |

## よくあるミス

??? failure "バッファが先に消える"
    ストリームはバッファを借りるだけです。バッファより先にストリームを破棄します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`spanstream`](spanstream.md) | 読み書き両用 |
| [`std::span`](../containers/span.md) | メモリの範囲を表す型 |

## コンパイラ対応

C++23 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `span` の上にあるメモリを使うストリームバッファ
    - [x] コピーしない
    - [x] C++23

## 関連ページ

- [cpprefjp: std::spanbuf](https://cpprefjp.github.io/reference/spanstream/spanbuf.html)
- [cppreference: std::spanbuf](https://en.cppreference.com/w/cpp/io/spanbuf)

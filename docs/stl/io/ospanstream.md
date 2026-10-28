---
title: std::ospanstream
summary: "`span` の上にあるメモリに、書き込むストリーム。"
order: 900
tags:
  - 入出力・文字列
---

# std::ospanstream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <spanstream>`
</div>

`ostringstream` は内部でメモリを確保します。`ospanstream` は、あらかじめ用意したバッファ（`span<char>`）に**そのまま**書き込むので、確保が起きません。ヒープを使いたくない場面（ゲームの毎フレームのログ）に向きます。

!!! tip "ポイント"
    - コピーやヒープ確保が起きない。
    - バッファは自分で用意し、生きている間だけ使える。
    - C++23 の機能。

!!! info "このページを読む前に"
    [`std::spanstream`](spanstream.md) を先に読んでください。

## 関数の詳しい説明

### std::ospanstream {#ospanstream}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class basic_ospanstream;
using ospanstream = basic_ospanstream<char>;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <print>
#include <span>
#include <spanstream>

int main() {
  char buf[16] = {};
  std::ospanstream out{std::span<char>(buf)};
  out << 42;
  std::println("{}", buf);
}
```

```text title="実行結果"
42
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定のバッファを解析・書き込みする | `std::ospanstream` |

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
    - [x] `span` の上にあるメモリに書き込むストリーム
    - [x] コピーしない
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ospanstream](https://cpprefjp.github.io/reference/spanstream/ospanstream.html)
- [cppreference: std::ospanstream](https://en.cppreference.com/w/cpp/io/ospanstream)

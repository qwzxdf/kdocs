---
title: std::ispanstream
summary: "`span` の上にあるメモリから、読み込むストリーム。"
order: 900
tags:
  - 入出力・文字列
---

# std::ispanstream

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-23">C++23</span>
`#include <spanstream>`
</div>

`istringstream` は、文字列の**コピー**を持ちます。`ispanstream` は、すでにあるバッファ（`span<const char>`）を**そのまま**読むので、コピーが起きません。固定のバッファを解析するときに使います。

!!! tip "ポイント"
    - コピーやヒープ確保が起きない。
    - バッファは自分で用意し、生きている間だけ使える。
    - C++23 の機能。

!!! info "このページを読む前に"
    [`std::spanstream`](spanstream.md) を先に読んでください。

## 関数の詳しい説明

### std::ispanstream {#ispanstream}

```cpp
template <class CharT, class Traits = char_traits<CharT>>
class basic_ispanstream;
using ispanstream = basic_ispanstream<char>;
```

- 戻り値: ストリームとして使う
- 計算量: 操作による


## 実際に動かしてみる

```cpp
#include <print>
#include <span>
#include <spanstream>

int main() {
  std::ispanstream in(std::span<const char>("42 7", 4));
  int a = 0;
  int b = 0;
  in >> a >> b;
  std::println("{} {}", a, b);
}
```

```text title="実行結果"
42 7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 固定のバッファを解析・書き込みする | `std::ispanstream` |

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
    - [x] `span` の上にあるメモリから、読み込むストリーム
    - [x] コピーしない
    - [x] C++23

## 関連ページ

- [cpprefjp: std::ispanstream](https://cpprefjp.github.io/reference/spanstream/ispanstream.html)
- [cppreference: std::ispanstream](https://en.cppreference.com/w/cpp/io/ispanstream)

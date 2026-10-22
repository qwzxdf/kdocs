---
title: std::emit_on_flush
summary: "osyncstream で、フラッシュのたびに出力を確定する設定にする。"
order: 900
tags:
  - 入出力・文字列
---

# std::emit_on_flush

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <iostream>`
</div>

`osyncstream` は、普通は破棄されるときにまとめて出力します。`emit_on_flush` を設定すると、`flush` のたびに出力が確定します。

!!! tip "ポイント"
    - `noemit_on_flush` で解除する。
    - 既定はオフ（破棄時にまとめて出力）。
    - `flush_emit` は、1 回だけ確定してフラッシュする。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::emit_on_flush {#emit_on_flush}

```cpp
template <class CharT, class Traits>
std::basic_ostream<CharT, Traits>& emit_on_flush(std::basic_ostream<CharT, Traits>& os);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `os` | ostream& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iostream>
#include <syncstream>

int main() {
  std::osyncstream out(std::cout);
  out << std::emit_on_flush << "x\n" << std::flush;
}
```

```text title="実行結果"
x
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "既定でオンだと思う"
    既定はオフです。

## 類似

| 名前 | 違い |
| --- | --- |
| [`flush_emit`](flush_emit.md) | 1 回だけ確定する |
| [`osyncstream`](osyncstream.md) | 同期出力 |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] osyncstream で、フラッシュのたびに出力を確定する設定にする
    - [x] `noemit_on_flush` で解除する
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::emit_on_flush](https://cpprefjp.github.io/reference/ios/emit_on_flush.html)
- [cppreference: std::emit_on_flush](https://en.cppreference.com/w/cpp/io/manip/emit_on_flush)

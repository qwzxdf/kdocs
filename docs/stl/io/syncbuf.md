---
title: std::syncbuf
summary: "出力を溜めておき、emit() でまとめて書き出すストリームバッファ。"
order: 900
tags:
  - 入出力・文字列
---

# std::syncbuf

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-20">C++20</span>
`#include <syncstream>`
</div>

複数のスレッドが同じ `cout` に書くと、行が混ざります。`syncbuf` は、書き込みを自分のバッファに溜めておき、`emit()` を呼んだときに、まとめて（途中に他のスレッドの出力を挟まず）出力先に書き出します。`osyncstream` の内部で使われている部品です。

!!! tip "ポイント"
    - `emit()` を呼ぶまで、書き込みは出力先に出ない。
    - デストラクタでも `emit()` される。
    - ふつうは `osyncstream` を使う。

!!! info "このページを読む前に"
    [`std::osyncstream`](osyncstream.md) を先に読んでください。

## 関数の詳しい説明

### std::syncbuf {#syncbuf}

```cpp
template <class CharT, class Traits = char_traits<CharT>, class Allocator = allocator<CharT>>
class basic_syncbuf;
using syncbuf = basic_syncbuf<char>;
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `sbuf` | streambuf* | 最終的な出力先のバッファ |

- 戻り値: ストリームバッファとして使う
- 計算量: 溜めた量に比例


## 実際に動かしてみる

```cpp
#include <iostream>
#include <syncstream>

int main() {
  std::syncbuf sb(std::cout.rdbuf());
  std::ostream os(&sb);
  os << "hi\n";
  sb.emit();
}
```

```text title="実行結果"
hi
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 複数のスレッドのログの行が混ざらないようにする | `std::syncbuf sb(std::cout.rdbuf());` |

## よくあるミス

??? failure "`emit()` を呼ばずに破棄を待つ"
    デストラクタで出力されますが、タイミングが遅れます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`osyncstream`](osyncstream.md) | ストリームとして使えるラッパー |

## コンパイラ対応

C++20 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 出力を溜めて emit でまとめて出す
    - [x] 行が混ざらない
    - [x] ふつうは osyncstream

## 関連ページ

- [cpprefjp: std::syncbuf](https://cpprefjp.github.io/reference/syncstream/basic_syncbuf.html)
- [cppreference: std::syncbuf](https://en.cppreference.com/w/cpp/io/basic_syncbuf)

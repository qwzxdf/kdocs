---
title: std::showbase
summary: "整数の出力に、進数の接頭辞（`0x` や `0`）を付ける。"
order: 900
tags:
  - 入出力・文字列
---

# std::showbase

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

16 進数で `ff` と出ただけでは、`ff` という文字列なのか、10 進の何かなのか、紛らわしい。`0xff` のように、基数の印を付けて出したい。そのための操作子が `std::showbase` です。

!!! tip "ポイント"
    - `std::showbase` で、16 進数に `0x`、8 進数に `0` を付ける
    - 10 進数には付かない
    - `std::uppercase` を併用すると `0X` と大文字になる
    - 設定は残る。戻すには `std::noshowbase`

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::showbase {#showbase}

```cpp
std::ios_base& showbase(std::ios_base& str);
```

整数を [`hex`](hex.md) で出すとき、`0x` の接頭辞を付けます。[`oct`](oct.md) では先頭に `0` が付きます。10 進数には何も付きません。

値が 0 のときは、`0` だけが出て、`0x0` にはなりません。16 進数のゼロ埋めで `0x00` と出したいときは、`internal` と `setfill('0')` を併用します。

プログラマー向けのログでは、16 進数に必ず `0x` を付けると、10 進数との区別が付きます。メモリのアドレスや、フラグの値を出すときの、基本の設定です。

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << std::hex << 255 << '\n';               // ff
  std::cout << std::showbase << 255 << '\n';          // 0xff
  std::cout << std::oct << 8 << '\n';                 // 010
  std::cout << std::hex << 0 << '\n';                 // 0（0x は付かない）
  std::cout << std::dec << 255 << '\n';               // 255（10 進数には付かない）
}
```

```text title="実行結果"
ff
0xff
010
0
255
```

## ゲームでの使いどころ

メモリのアドレスやハンドルの値をログに出すときに使います。10 進数と区別がつくよう、`0x` を付けます。

## よくあるミス

??? failure "ゼロ埋めで `0x` が欠ける"
    `internal` と `setfill('0')` を併用します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数にする |
| [`uppercase`](uppercase.md) | 大文字にする |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 基数の印（`0x`、`0`）を付ける
    - [x] 10 進数には付かない
    - [x] 戻すのは `noshowbase`

## 関連ページ

- [cpprefjp: std::showbase](https://cpprefjp.github.io/reference/ios/showbase.html)
- [cppreference: std::showbase](https://en.cppreference.com/w/cpp/io/manip/showbase)

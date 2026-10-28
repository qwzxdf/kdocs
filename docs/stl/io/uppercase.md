---
title: std::uppercase
summary: "16 進数や指数表記の英字を、大文字で出力する。"
order: 900
tags:
  - 入出力・文字列
---

# std::uppercase

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

16 進数の `ff8800` を、`FF8800` と大文字で出したい。浮動小数点数の指数表記の `e` も、`E` にしたい。出力に出る英字を大文字にする操作子が `std::uppercase` です。

!!! tip "ポイント"
    - `std::uppercase` で、16 進数の `a`〜`f`、`0x`、指数表記の `e` を大文字にする
    - `showbase` と組み合わせると、`0XFF` になる（`0x` の x も大文字）
    - 設定は残る。戻すには `std::nouppercase`
    - 文字列には効かない（文字列の英字は変換されない）

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::uppercase {#uppercase}

```cpp
std::ios_base& uppercase(std::ios_base& str);
```

数値の出力に現れる英字を大文字にします。対象は、16 進数の桁（`a`〜`f`）、基数の接頭辞（`0x` の `x`）、浮動小数点数の指数部（`e`）、`inf` や `nan` です。

`"hello"` のような文字列には効きません。文字列を大文字にするには、`std::toupper` などで変換します。

色コードを `#FF8800` のように大文字で出すのが一般的なので、16 進数の出力では、ほぼセットで使います。

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << std::hex << 0xFF8800 << '\n';           // ff8800
  std::cout << std::uppercase << 0xFF8800 << '\n';     // FF8800
  std::cout << std::showbase << 255 << '\n';           // 0XFF
  std::cout << std::scientific << 1234.5 << '\n';      // 1.234500E+03
}
```

```text title="実行結果"
ff8800
FF8800
0XFF
1.234500E+03
```

## ゲームでの使いどころ

色コードやハッシュ値、アドレスの表示で使います。16 進数を大文字にそろえると、見た目が整います。

## よくあるミス

??? failure "文字列が大文字になると期待する"
    数値の英字だけが対象です。

??? failure "`showbase` と併用して `0X` になって驚く"
    `x` も大文字になります。`0x` を保ちたいなら、`uppercase` を使わず、桁だけ自前で大文字にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数にする |
| [`showbase`](showbase.md) | 基数の印を付ける |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 数値の英字を大文字にする
    - [x] `0x` も `0X` になる
    - [x] 戻すのは `nouppercase`

## 関連ページ

- [cpprefjp: std::uppercase](https://cpprefjp.github.io/reference/ios/uppercase.html)
- [cppreference: std::uppercase](https://en.cppreference.com/w/cpp/io/manip/uppercase)

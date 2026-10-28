---
title: std::hex
summary: "整数を 16 進数で出力・入力するように切り替える（dec / oct も同じ仲間）。"
order: 79
tags:
  - 入出力・文字列
---

# std::hex

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ios>`
</div>

ピクセルの色を 16 進数で `FF8800` と表示したい。メモリのアドレスやフラグの値を、16 進数で確かめたい。`std::cout << 255` は、10 進数の `255` を出します。ストリームの基数を切り替える操作子の 1 つが `std::hex` です。

<strong>以降の整数の出力と入力を、16 進数にする</strong>操作子です。`std::cout << std::hex << 255` で `ff` と出ます。

!!! tip "ポイント"
    - `std::hex` を流すと、そのストリームの整数の基数が 16 進数に変わる
    - 設定は残り続ける。戻すには `std::dec`
    - 英字は小文字。大文字にするには `std::uppercase`、`0x` を付けるには `std::showbase`
    - 負の数は、符号なしとして解釈されたビット列（`ffffffff` など）で出る

!!! info "このページを読む前に"
    [`std::cout`](cout.md) などの出力ストリームの設定です。新しいコードでは [`std::println`](../utilities/print.md) の書式が簡単です。

## 関数の詳しい説明

### std::hex {#hex}

```cpp
std::ios_base& hex(std::ios_base& str);
```

`std::cout << std::hex` のように、ストリームに流して使います。引数は、ストリームの書式フラグで、`basefield`（基数のグループ）を 16 進数に設定します。10 進数なら [`dec`](dec.md)、8 進数なら [`oct`](oct.md)です。

効果は、<strong>設定を戻すまで続きます</strong>。1 回の出力で終わりではないので、`hex` の後に出した整数は、すべて 16 進数になります。ログの途中で `hex` を使って、戻し忘れると、その後の数値が全部 16 進数で出て、混乱します。

標準では、`hex` で出る英字は小文字です。`std::uppercase` を併用すると大文字になり、`std::showbase` を併用すると、先頭に `0x` が付きます。

`bool` や `char` には効きません。`char` はそのまま文字として出るので、バイトを 16 進数で見たいときは、`int` に変換して出します。

C++23 の `std::print` では、`{:x}` のように書式で指定できて、設定が残る問題がありません。新しいコードでは、そちらのほうが安全です。

## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  int color = 0xFF8800;

  std::cout << std::hex << color << '\n';                       // ff8800
  std::cout << std::uppercase << color << '\n';                 // FF8800
  std::cout << std::showbase << 255 << '\n';                    // 0XFF
  std::cout << std::dec << std::nouppercase << std::noshowbase;  // 元に戻す
  std::cout << 255 << '\n';                                     // 255

  // バイトを 16 進数で見たいときは、int に変換する
  unsigned char byte = 0x7F;
  std::cout << std::hex << static_cast<int>(byte) << '\n';
}
```

```text title="実行結果"
ff8800
FF8800
0XFF
255
7f
```

## ゲームでの使いどころ

色コード、メモリのアドレス、フラグのビット列を、ログや画面に出すときに使います。ゲーム エンジンのデバッグ出力で、ハンドルや ID を 16 進数で出すのは定番です。

設定が残る性質のため、ログ関数の中で使うときは、出力のあとで必ず `dec` に戻すか、ストリームの状態を保存・復元します。`std::format` や `std::print` なら、この問題はありません。

## よくあるミス

??? failure "`hex` を戻さず、その後の数値が全部 16 進数になる"
    `std::dec` で戻します。ログ関数ごとに状態を戻す習慣をつけます。

??? failure "`char` を `hex` で出しても、文字のまま出る"
    `static_cast<int>` で整数にします。

??? failure "`std::cout << std::hex << 255.0` が効かない"
    基数は整数だけに効きます。浮動小数点数の 16 進表記は `hexfloat` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`dec`](dec.md) | 10 進数にする |
| [`oct`](oct.md) | 8 進数にする |
| [`setbase`](setbase.md) | 基数を数値で指定する |
| [`showbase`](showbase.md) | `0x` を付ける |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 以降の整数を 16 進数にする
    - [x] 戻すまで続く
    - [x] 大文字は `uppercase`、`0x` は `showbase`

## 関連ページ

- [cpprefjp: std::hex](https://cpprefjp.github.io/reference/ios/hex.html)
- [cppreference: std::hex](https://en.cppreference.com/w/cpp/io/manip/hex)

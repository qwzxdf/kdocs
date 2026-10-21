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

`std::hex` は、**整数を 16 進数で出力・入力するようにストリームの設定を切り替える**マニピュレーターです。仲間に 10 進数の `std::dec`、8 進数の `std::oct` があります。**設定は残り続ける**ので、出力のあとに `std::dec` で戻します。`std::println("{:x}", n)` のほうが、設定が残らず簡単です。

!!! tip "ポイント"
    - `std::cout << std::hex << 255;` → `ff`。
    - 一度指定すると以降ずっと有効。元に戻すのは `std::dec`。
    - 新しいコードでは `std::println("{:x}", n)`。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) などの出力ストリームの設定です。新しいコードでは [`std::println`](../utilities/print.md) の書式が簡単です。

## 関数の詳しい説明

### std::hex {#hex}

```cpp
std::ios_base& hex(std::ios_base& str);
std::ios_base& dec(std::ios_base& str);
std::ios_base& oct(std::ios_base& str);
```

- 戻り値: `str`（`<<` で続けて書ける）
- 計算量: O(1)

```cpp
#include <iostream>

int main() {
  std::cout << std::hex << 255 << '\n';   // ff
  std::cout << std::dec << 255 << '\n';   // 255 に戻す
}
```

```text title="実行結果"
ff
255
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 古いコードで、アドレスや色コードを 16 進数で出す | `std::cout << std::hex << color;` |

## よくあるミス

??? failure "設定が残って、後の出力が 16 進数のまま"
    出力の最後に `std::dec` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../utilities/print.md) | `{:x}` で 16 進数、設定が残らない |
| [`setw`](setw.md) | 幅を決める |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数の進数を切り替える
    - [x] 設定は残り続ける
    - [x] 新しいコードは `{:x}`

## 関連ページ

- [cpprefjp: std::hex](https://cpprefjp.github.io/reference/ios/hex.html)
- [cppreference: std::hex](https://en.cppreference.com/w/cpp/io/manip/hex)

---
title: std::dec
summary: "整数を 10 進数で出力・入力する（既定）。"
order: 900
tags:
  - 入出力・文字列
---

# std::dec

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`std::hex` や `std::oct` に切り替えたあと、元の 10 進数に戻すときに使います。何も設定しなければ、すでに 10 進数です。

!!! tip "ポイント"
    - 既定は 10 進数。
    - `hex`・`oct` のあとに戻すときに使う。
    - 設定はストリームに残る。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::dec {#dec}

```cpp
std::ios_base& dec(std::ios_base& str);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `str` | ios_base& | 対象のストリーム |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iostream>

int main() {
  std::cout << std::hex << 255 << ' ' << std::dec << 255 << '\n';
}
```

```text title="実行結果"
ff 255
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "戻し忘れる"
    `hex` のまま後続の出力が続きます。`dec` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数 |
| [`oct`](oct.md) | 8 進数 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数を 10 進数で出力・入力する（既定）
    - [x] 既定は 10 進数
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::dec](https://cpprefjp.github.io/reference/ios/dec.html)
- [cppreference: std::dec](https://en.cppreference.com/w/cpp/io/manip/dec)

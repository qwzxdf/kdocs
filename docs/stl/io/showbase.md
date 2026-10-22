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

`std::hex` で 16 進数を出力しても、ふつうは `ff` のように接頭辞が付きません。`showbase` を設定すると、`0xff` のように、進数が分かる接頭辞が付きます。

!!! tip "ポイント"
    - `hex` で `0x`、`oct` で `0` が付く。
    - `noshowbase` で解除する。
    - 大文字にするなら `uppercase`。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::showbase {#showbase}

```cpp
std::ios_base& showbase(std::ios_base& str);
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
  std::cout << std::showbase << std::hex << 255 << '\n';
}
```

```text title="実行結果"
0xff
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式を、ストリームに設定する |

## よくあるミス

??? failure "設定が残り続ける"
    ストリームの書式は設定したら残ります。必要なら `noshowbase` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数にする |
| [`uppercase`](uppercase.md) | 大文字にする |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数の出力に、進数の接頭辞（`0x` や `0`）を付ける
    - [x] `hex` で `0x`、`oct` で `0` が付く
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::showbase](https://cpprefjp.github.io/reference/ios/showbase.html)
- [cppreference: std::showbase](https://en.cppreference.com/w/cpp/io/manip/showbase)

---
title: std::setbase
summary: "整数の基数（8・10・16）を設定する。"
order: 900
tags:
  - 入出力・文字列
---

# std::setbase

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`hex`・`dec`・`oct` を数値で切り替えます。基数を変数で決めたいときに便利です。

!!! tip "ポイント"
    - 8・10・16 のどれか（それ以外は 10 に戻る）。
    - `hex`・`dec`・`oct` と同じ効果。
    - `<iomanip>` が必要。

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::setbase {#setbase}

```cpp
/* 実装定義 */ setbase(int base);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `base` | int | 8・10・16 のどれか |

- 戻り値: ストリームへの参照
- 計算量: 定数


## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setbase(16) << 255 << '\n';
}
```

```text title="実行結果"
ff
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| 使いどころ | 出力の書式をストリームに設定する |

## よくあるミス

??? failure "2 進数を指定する"
    `setbase(2)` はできません（10 になります）。2 進数は `std::bitset` です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`hex`](hex.md) | 16 進数 |
| [`std::bitset`](../containers/bitset.md) | 2 進数の表示 |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 整数の基数（8・10・16）を設定する
    - [x] 8・10・16 のどれか（それ以外は 10 に戻る）
    - [x] 戻り値と失敗時の動きを確かめて使う

## 関連ページ

- [cpprefjp: std::setbase](https://cpprefjp.github.io/reference/ios/setbase.html)
- [cppreference: std::setbase](https://en.cppreference.com/w/cpp/io/manip/setbase)

---
title: std::setfill
summary: "幅を埋める文字を決める。"
order: 78
tags:
  - 入出力・文字列
---

# std::setfill

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <iomanip>`
</div>

`std::setfill(c)` は、**`setw` で決めた幅の余りを埋める文字**を決めるマニピュレーターです。`0` で埋めて「007」のように出したいときなどに使います。**一度指定すると、以降ずっと有効**です。

!!! tip "ポイント"
    - `std::setfill('0') << std::setw(3) << 7` で「007」。
    - 指定は残り続ける。
    - 新しいコードは `std::println("{:03}", 7)`。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::setfill {#setfill}

```cpp
/* unspecified */ setfill(char c);  // <iomanip>
```

- `setw` で余った部分を埋める文字。以後ずっと効きます

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setfill('0') << std::setw(3) << 7 << "\n";
}
```

```text title="実行結果"
007
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ステータス表を桁をそろえて出す | `std::cout << std::setfill(...)` |

## よくあるミス

??? failure "指定が残り続けて、後の出力が崩れる"
    設定は出力の状態に残ります。出力の最後に、元に戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../utilities/print.md) | 書式 `{:>6}` `{:.2f}` `{:03}` で同じことができる |
| [`std::cout`](cout.md) | 出力先 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 幅を埋める文字を決める。
    - [x] 一部は設定が残り続ける
    - [x] 新しいコードは `println`

## 関連ページ

- [cpprefjp: std::setfill](https://cpprefjp.github.io/reference/iomanip/setfill.html)
- [cppreference: std::setfill](https://en.cppreference.com/w/cpp/io/manip/setfill)

---
title: std::setw
summary: "次に出す値の「幅」を決める（右寄せでそろえる）。"
order: 76
tags:
  - 入出力・文字列
---

# std::setw

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <iomanip>`
</div>

`std::setw(n)` は、**次に出す 1 つの値を幅 n 文字で出す**マニピュレーターです。表を縦にそろえて出すときに使います。**効くのは次の 1 つの出力だけ**です。

!!! tip "ポイント"
    - 幅は次の 1 回だけ有効。表の各列ごとに指定する。
    - 埋める文字は [`setfill`](setfill.md)。
    - 新しいコードは `std::println("{:>6}", x)`。

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::setw {#setw}

```cpp
/* unspecified */ setw(int n);  // <iomanip>
```

- **次の 1 つだけ**、最低 `n` 文字の幅で出力します（右寄せ）

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setw(5) << 42 << "|" << std::setw(5) << 7 << "\n";   // 幅 5 で右寄せ
}
```

```text title="実行結果"
   42|    7
```

## ゲームでの使いどころ

| 場面 | 書き方 |
| --- | --- |
| ステータス表を桁をそろえて出す | `std::cout << std::setw(...)` |

## よくあるミス

??? failure "setw が次の 1 つにしか効かない"
    複数の列を出すときは、列ごとに `setw` を付けます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::println`](../utilities/print.md) | 書式 `{:>6}` `{:.2f}` `{:03}` で同じことができる |
| [`std::cout`](cout.md) | 出力先 |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 次に出す値の「幅」を決める（右寄せでそろえる）。
    - [x] 一部は設定が残り続ける
    - [x] 新しいコードは `println`

## 関連ページ

- [cpprefjp: std::setw](https://cpprefjp.github.io/reference/iomanip/setw.html)
- [cppreference: std::setw](https://en.cppreference.com/w/cpp/io/manip/setw)

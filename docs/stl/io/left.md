---
title: std::left
summary: "出力を、幅の中で左寄せにする。"
order: 900
tags:
  - 入出力・文字列
---

# std::left

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`setw` で幅を決めた欄に、内容が収まるとき、余りの空白は、左と右のどちらに入るのでしょう。既定では、内容が右に寄り、空白は左に入ります。名前の列のように、左に寄せたいときは、`std::left` を使います。

!!! tip "ポイント"
    - `std::left` で、幅の欄の内容を左に寄せ、余りを右に詰める
    - 設定は残り続ける。戻すには `std::right`
    - `setw` で幅を決めた欄にだけ効く
    - 文字列にも数値にも効く

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::left {#left}

```cpp
std::ios_base& left(std::ios_base& str);
```

[`setw`](setw.md) で決めた幅の中で、内容を左端に置きます。余った分は、右側に詰め物（既定は空白）で埋められます。

名前や説明のような文字列の列は左そろえ、数値の列は右そろえ、が表の見やすい基本です。そのため、表の中で `left` と `right` を切り替える場面が出てきます。

設定が残るので、列ごとに切り替えるなら、その都度流します。`internal` は、符号や基数の印を左に、数字を右に寄せる、数値専用の指定です。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::left  << std::setw(8) << "name" << '|' << '\n';
  std::cout << std::right << std::setw(8) << "name" << '|' << '\n';
}
```

```text title="実行結果"
name    |
    name|
```

## ゲームでの使いどころ

コンソール表示の表で、名前の列を左にそろえるときに使います。数値の列は `right` にして、桁をそろえます。

## よくあるミス

??? failure "`setw` なしで使って、効果が見えない"
    幅を決めた欄の中でだけ意味があります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`right`](right.md) | 右に寄せる |
| [`internal`](internal.md) | 符号と数字の間を埋める |
| [`setw`](setw.md) | 幅を決める |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 幅の欄で左に寄せる
    - [x] 設定は残る
    - [x] 名前の列に向く

## 関連ページ

- [cpprefjp: std::left](https://cpprefjp.github.io/reference/ios/left.html)
- [cppreference: std::left](https://en.cppreference.com/w/cpp/io/manip/left)

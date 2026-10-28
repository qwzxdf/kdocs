---
title: std::right
summary: "出力を、幅の中で右寄せにする（既定）。"
order: 900
tags:
  - 入出力・文字列
---

# std::right

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

数値の列は、桁をそろえるために、右にそろえたい。`std::right` は、`setw` で決めた幅の欄で、<strong>内容を右に寄せ、余りを左に詰め</strong>ます。出力ストリームの既定の状態でもあります。

!!! tip "ポイント"
    - `std::right` で、幅の欄の内容を右に寄せ、余りを左に詰める
    - ストリームの既定は右そろえ。`left` の後に戻すときに使う
    - 設定は残り続ける
    - `setw` で幅を決めた欄にだけ効く

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::right {#right}

```cpp
std::ios_base& right(std::ios_base& str);
```

[`setw`](setw.md) で決めた幅の中で、内容を右端に置きます。余った分は、左側が詰め物で埋まります。

数値の列は、桁数が違っても、1 の位がそろうほうが、読みやすくなります。名前の列を `left`、数値の列を `right` にして表を作るのが、基本の形です。

出力の既定が右そろえなので、何も指定しなくても同じ見た目になりますが、前に `left` を流した後なら、`right` で戻す必要があります。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::right;
  std::cout << std::setw(6) << 1 << '\n';
  std::cout << std::setw(6) << 100 << '\n';
  std::cout << std::setw(6) << 12345 << '\n';
}
```

```text title="実行結果"
     1
   100
 12345
```

## ゲームでの使いどころ

数値の列を右にそろえて、桁を見やすくするときに使います。プロファイラーの結果、スコアのランキング、ダメージの一覧などです。

## よくあるミス

??? failure "`left` を流したまま、数値の列もずれる"
    数値の列の前に `right` を流します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`left`](left.md) | 左に寄せる |
| [`internal`](internal.md) | 符号と数字の間を埋める |
| [`setw`](setw.md) | 幅を決める |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 幅の欄で右に寄せる
    - [x] 既定の状態
    - [x] 数値の列に向く

## 関連ページ

- [cpprefjp: std::right](https://cpprefjp.github.io/reference/ios/right.html)
- [cppreference: std::right](https://en.cppreference.com/w/cpp/io/manip/right)

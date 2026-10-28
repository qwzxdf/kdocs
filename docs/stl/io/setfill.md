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

スコアを `00042` のように、ゼロ埋めで表示したい。`setw` で幅を指定すると、足りない分は空白で埋まります。その詰め物を、ほかの文字に変えるのが `std::setfill` です。

!!! tip "ポイント"
    - `std::setfill('0')` で、詰め物をゼロにする。`setw` と組み合わせて使う
    - <strong>`setw` と違い、設定が残り続ける</strong>。戻すには `setfill(' ')`
    - `setw` で決めた幅に対して効く。幅がないと、詰め物は使われない
    - 引数は `char`（ワイド ストリームなら `wchar_t`）

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::setfill {#setfill}

```cpp
template <class CharT>
/* 未規定 */ setfill(CharT c);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `c` | 文字型 | 詰め物にする文字 |

[`setw`](setw.md) で幅を決めたとき、内容が幅に足りない分を、`c` で埋めます。既定は空白です。

`setw` の効果は 1 回の出力で解除されますが、`setfill` は、変えるまで残り続けます。ゼロ埋めの表示をしたあと、`setfill('0')` を戻さないと、その後の `setw` を使った出力が、すべてゼロ埋めになります。

数値のゼロ埋めには、`std::internal` と組み合わせて、符号を左に、数字を右に寄せる使い方もあります（`-0042`）。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setfill('0') << std::setw(5) << 42 << '\n';     // 00042
  std::cout << std::setw(5) << 7 << '\n';                          // setfill が残るので 00007

  std::cout << std::setfill('*') << std::left << std::setw(8) << "hi" << "|\n";   // hi******|

  // 元に戻す
  std::cout << std::setfill(' ') << std::right << std::setw(5) << 7 << '\n';
}
```

```text title="実行結果"
00042
00007
hi******|
    7
```

## ゲームでの使いどころ

連番のファイル名（`shot_0001.png`）、タイマーの表示（`03:07`）、スコアの桁そろえで使います。

C++20 以降なら、`std::format("{:05}", 42)` のように、書式の中でゼロ埋めを指定できます。設定が残らないので、安全です。

## よくあるミス

??? failure "`setfill` が残って、あとの出力がずっと埋まる"
    使い終わったら `setfill(' ')` に戻します。

??? failure "`setw` なしで使って、効果がない"
    `setw` で幅を決めた欄にだけ使われます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`setw`](setw.md) | 幅を決める |
| [`internal`](internal.md) | 符号と数字の間を埋める |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 詰め物の文字を決める
    - [x] 設定は残り続ける
    - [x] `setw` と組み合わせる

## 関連ページ

- [cpprefjp: std::setfill](https://cpprefjp.github.io/reference/iomanip/setfill.html)
- [cppreference: std::setfill](https://en.cppreference.com/w/cpp/io/manip/setfill)

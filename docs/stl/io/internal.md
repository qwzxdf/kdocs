---
title: std::internal
summary: "符号や接頭辞を左に、数字を右に寄せる（間を埋める）。"
order: 900
tags:
  - 入出力・文字列
---

# std::internal

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

負の数をゼロ埋めで表示すると、`00-42` のように、符号が数字の間に入って見づらくなります。符号は左端に、数字は右端に置いて、その間を詰め物で埋めたい。そのための寄せ方が `std::internal` です。

!!! tip "ポイント"
    - `std::internal` で、符号や基数の印（`0x`）を左端に、数字を右端に置き、間を埋める
    - `setfill('0')` と組み合わせて、`-0042` や `0x00ff` の形にする
    - 数値にだけ意味がある。文字列では右そろえと同じ
    - 設定は残り続ける

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::internal {#internal}

```cpp
std::ios_base& internal(std::ios_base& str);
```

`setw` で決めた幅の中で、符号（`-`、`+`）と基数の印（`0x`）を左端に、数字の部分を右端に置き、間を詰め物で埋めます。

`std::right` と `setfill('0')` の組み合わせだと、詰め物は数値全体の左に入るので、`-42` が `000-42` になります。`internal` なら、`-0042` になります。符号つきの数値をゼロ埋めするときの、正しい形です。

16 進数で `showbase` を併用すると、`0x` が左に残り、数字がゼロで埋まります（`0x00ff`）。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::setfill('0');

  std::cout << std::right << std::setw(6) << -42 << '\n';      // 000-42
  std::cout << std::internal << std::setw(6) << -42 << '\n';   // -00042

  std::cout << std::hex << std::showbase << std::setw(8) << 255 << '\n';   // 0x0000ff
}
```

```text title="実行結果"
000-42
-00042
0x0000ff
```

## ゲームでの使いどころ

符号つきの数値や、16 進数のアドレスを、固定の幅でゼロ埋めして表示するときに使います。メモリのダンプや、座標の表示で見かけます。

C++20 以降の `std::format("{:+06}", -42)` でも、同じ形（`-00042`）が書けます。

## よくあるミス

??? failure "`right` とゼロ埋めで、符号が間に入る"
    `internal` を使います。

??? failure "文字列に使って、効果がないと思う"
    文字列では右そろえと同じです。数値向けの指定です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`left`](left.md) | 左に寄せる |
| [`right`](right.md) | 右に寄せる |
| [`setfill`](setfill.md) | 詰め物を決める |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 符号と数字の間を埋める
    - [x] ゼロ埋めの数値に向く
    - [x] 設定は残る

## 関連ページ

- [cpprefjp: std::internal](https://cpprefjp.github.io/reference/ios/internal.html)
- [cppreference: std::internal](https://en.cppreference.com/w/cpp/io/manip/internal)

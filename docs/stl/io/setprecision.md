---
title: std::setprecision
summary: "小数の桁数を決める。"
order: 77
tags:
  - 入出力・文字列
---

# std::setprecision

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <iomanip>`
</div>

`std::cout << 3.14159265` は、既定では `3.14159` と出ます。小数点以下 2 桁で出したい。有効数字を 10 桁出したい。浮動小数点数の「桁数」を決めるのが `std::setprecision` です。

!!! tip "ポイント"
    - `std::setprecision(n)` で、浮動小数点数の精度（桁数）を `n` にする
    - <strong>既定の書式では「有効数字の桁数」、`fixed` や `scientific` と併用すると「小数点以下の桁数」</strong>になる
    - 設定は残り続ける
    - `<iomanip>` が必要

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::setprecision {#setprecision}

```cpp
/* 未規定 */ setprecision(int n);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `n` | `int` | 精度。書式によって意味が変わる |

精度の意味が、書式のフラグによって変わるのが、いちばん混乱するところです。

何も指定しない既定の書式（`defaultfloat`）では、`n` は<strong>有効数字の桁数</strong>です。`setprecision(3)` で `3.14159` は `3.14`、`314.159` は `314`、`3141.59` は `3.14e+03` になります。整数部が長いと、指数表記に切り替わります。

[`fixed`](fixed.md) と併用すると、`n` は<strong>小数点以下の桁数</strong>になります。`fixed << setprecision(2)` で `3.14159` は `3.14`、`314.159` は `314.16` です。固定の小数点以下の桁数で表示したいなら、この形です。

[`scientific`](scientific.md) と併用しても、小数点以下の桁数です。

既定の精度は 6 です。`double` を完全に往復できる桁数にするには、17 桁（`std::numeric_limits<double>::max_digits10`）が必要です。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  double v = 3.14159265;

  std::cout << std::setprecision(3) << v << '\n';                       // 有効数字 3 桁: 3.14
  std::cout << std::setprecision(3) << 314.159 << '\n';                 // 314
  std::cout << std::fixed << std::setprecision(2) << v << '\n';         // 小数点以下 2 桁: 3.14
  std::cout << std::fixed << std::setprecision(2) << 314.159 << '\n';   // 314.16
}
```

```text title="実行結果"
3.14
314
3.14
314.16
```

## ゲームでの使いどころ

座標、スコア、時間の表示で、小数点以下の桁数をそろえるときに使います。`fixed` と組み合わせて、`std::fixed << std::setprecision(2)` と書くのが定番です。

C++20 以降では、`std::format("{:.2f}", v)` で同じことが、設定を残さずに書けます。

## よくあるミス

??? failure "`fixed` なしで使って、有効数字になる"
    小数点以下の桁数が欲しいなら、`fixed` を併用します。

??? failure "設定が残って、あとの表示が変わる"
    使い終わったら、元の精度（6）と `defaultfloat` に戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fixed`](fixed.md) | 小数点以下の桁数にする |
| [`scientific`](scientific.md) | 指数表記にする |
| [`defaultfloat`](defaultfloat.md) | 既定の書式に戻す |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点数の桁数を決める
    - [x] `fixed` だと小数点以下
    - [x] 設定は残る

## 関連ページ

- [cpprefjp: std::setprecision](https://cpprefjp.github.io/reference/iomanip/setprecision.html)
- [cppreference: std::setprecision](https://en.cppreference.com/w/cpp/io/manip/setprecision)

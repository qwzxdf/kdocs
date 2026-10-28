---
title: std::fixed
summary: "小数を「固定小数点の形」（小数点以下の桁数を指定）で出力する。"
order: 80
tags:
  - 入出力・文字列
---

# std::fixed

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ios>`
</div>

座標を `10.5` と `10.50` のどちらで出すか。桁をそろえて、小数点以下を必ず 2 桁出したい。浮動小数点数を、指数表記ではなく、固定小数点の形で出すのが `std::fixed` です。

!!! tip "ポイント"
    - `std::fixed` で、`123.456000` のような固定小数点の形で出す
    - `setprecision(n)` と組み合わせると、小数点以下 `n` 桁になる
    - 精度の既定は 6 桁。`fixed` だけなら、`3.140000` と出る
    - 設定は残り続ける。戻すには `defaultfloat`

!!! info "このページを読む前に"
    [`std::cout`](cout.md) などの出力ストリームの設定です。新しいコードでは [`std::println`](../utilities/print.md) の書式が簡単です。

## 関数の詳しい説明

### std::fixed {#fixed}

```cpp
std::ios_base& fixed(std::ios_base& str);
```

浮動小数点数を、`123.456` のような固定小数点の形で出します。桁が大きくても小さくても、指数表記（`1.23e+10`）には切り替わりません。

[`setprecision`](setprecision.md) との組み合わせが前提です。`fixed` を流すと、精度の意味が「小数点以下の桁数」に変わります。`fixed` だけで精度を指定しないと、既定の 6 桁になり、`3.140000` のように末尾のゼロが並びます。

表示が必要な桁数を超えた部分は、四捨五入されます。`std::fixed << std::setprecision(1) << 0.25` は、`0.2` か `0.3` のどちらかになります。浮動小数点数の内部表現が 2 進数のため、0.25 は正確に表せますが、丸め方は偶数丸めが一般的で `0.2` です。

整数には効きません。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::fixed;
  std::cout << 3.14 << '\n';                         // 3.140000（既定の精度 6）
  std::cout << std::setprecision(2) << 3.14159 << '\n';   // 3.14
  std::cout << 1e10 << '\n';                         // 指数表記にならない
  std::cout << 0.5 << '\n';                          // 0.50
}
```

```text title="実行結果"
3.140000
3.14
10000000000.00
0.50
```

## ゲームでの使いどころ

座標、体力の割合、経過時間の表示で、小数点以下の桁数をそろえるときに使います。桁がそろうと、一覧表が読みやすくなります。

C++20 の `std::format("{:.2f}", v)` なら、設定を残さずに同じ表示ができます。

## よくあるミス

??? failure "`fixed` を流したまま、あとの数値が全部固定小数点になる"
    `std::defaultfloat` で戻します。

??? failure "`setprecision` を忘れて、`3.140000` が出る"
    桁数を指定します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`scientific`](scientific.md) | 指数表記にする |
| [`defaultfloat`](defaultfloat.md) | 既定の書式に戻す |
| [`setprecision`](setprecision.md) | 桁数を決める |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 固定小数点の形で出す
    - [x] `setprecision` で小数点以下の桁数
    - [x] 戻すのは `defaultfloat`

## 関連ページ

- [cpprefjp: std::fixed](https://cpprefjp.github.io/reference/ios/fixed.html)
- [cppreference: std::fixed](https://en.cppreference.com/w/cpp/io/manip/fixed)

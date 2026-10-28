---
title: std::defaultfloat
summary: "浮動小数点数の出力を、既定の形式に戻す。"
order: 900
tags:
  - 入出力・文字列
---

# std::defaultfloat

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <iostream>`
</div>

`fixed` や `scientific` を使ったあと、元の「ちょうどよく選ぶ」書式に戻したい。`std::defaultfloat` は、<strong>浮動小数点数の書式を、既定の状態に戻す</strong>操作子です。値の大きさで、固定小数点と指数表記を自動で選びます。

!!! tip "ポイント"
    - `fixed` と `scientific` の両方を解除する。ストリームの初期状態の書式
    - 精度は「有効数字の桁数」になる（既定は 6）
    - 値が大きすぎる、または小さすぎると、指数表記に自動で切り替わる
    - 末尾の 0 は省かれる（`3.5` が `3.500000` にならない）

!!! info "このページを読む前に"
    [`std::cout`](cout.md) と [`std::cin`](cin.md) を先に読んでください。

## 関数の詳しい説明

### std::defaultfloat {#defaultfloat}

```cpp
std::ios_base& defaultfloat(std::ios_base& str);
```

`fixed` と `scientific` のフラグを両方消します。出力は `printf` の `%g` に相当する書式になります。精度の桁数の有効数字で、値に応じて固定小数点か指数表記かを選び、末尾の不要な 0 は出しません。

`std::cout << 3.5` が `3.5` と出て、`3.500000` にならないのは、この書式のためです。

`fixed` / `scientific` の設定は残るので、使ったあとの後始末に `defaultfloat` を流します。精度も変えていたなら、`std::setprecision(6)` で戻します。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::fixed << std::setprecision(2) << 3.14159 << '\n';   // 3.14
  std::cout << std::defaultfloat << std::setprecision(6);                // 元に戻す
  std::cout << 3.5 << '\n';                                             // 3.5
  std::cout << 1234567.0 << '\n';                                       // 1.23457e+06
  std::cout << 0.0001 << '\n';                                          // 0.0001
}
```

```text title="実行結果"
3.14
3.5
1.23457e+06
0.0001
```

## ゲームでの使いどころ

ログ関数が、`fixed` などを使った後に、呼び出し側のストリームの状態を壊さないよう、最後に戻すために使います。

## よくあるミス

??? failure "`defaultfloat` だけで精度が戻ると思う"
    精度は別の設定です。`setprecision(6)` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fixed`](fixed.md) | 固定小数点にする |
| [`scientific`](scientific.md) | 指数表記にする |
| [`hexfloat`](hexfloat.md) | 16 進の浮動小数点表記にする |

## コンパイラ対応

C++11 以前から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 浮動小数点の書式を既定に戻す
    - [x] 値の大きさで自動選択
    - [x] 精度は別に戻す

## 関連ページ

- [cpprefjp: std::defaultfloat](https://cpprefjp.github.io/reference/ios/defaultfloat.html)
- [cppreference: std::defaultfloat](https://en.cppreference.com/w/cpp/io/manip/defaultfloat)

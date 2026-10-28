---
title: std::scientific
summary: "浮動小数を指数表記（`1.5e+03`）で出す。"
order: 85
tags:
  - 入出力・文字列
---

# std::scientific

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++98〜</span>
`#include <ios>`
</div>

とても大きい値や小さい値（`6.02e23` や `1e-9`）を、桁数に悩まずに、指数表記で出したい。浮動小数点数を、`1.234560e+03` の形で出すのが `std::scientific` です。

!!! tip "ポイント"
    - `std::scientific` で、`d.ddddde+XX` の形（仮数と指数）で出す
    - `setprecision(n)` と組み合わせると、仮数の小数点以下 `n` 桁になる
    - 大文字の `E` にするなら `std::uppercase`
    - 設定は残り続ける。戻すには `defaultfloat`

!!! info "このページを読む前に"
    - [STL](../index.md)（STL 全体の地図（どこに何があるか））

## 関数の詳しい説明

### std::scientific {#scientific}

```cpp
std::ios_base& scientific(std::ios_base& str);
```

浮動小数点数を、仮数部が 1 以上 10 未満の、指数表記で出します。`1234.5` は `1.234500e+03` です。

[`setprecision`](setprecision.md) と組み合わせると、精度は<strong>仮数部の小数点以下の桁数</strong>になります。`setprecision(2)` なら `1.23e+03` です。

科学計算やログで、桁の大きさをそろえて比べたいとき、極端な値を見やすく出したいときに使います。ゲームでは、物理シミュレーションの誤差や、確率の小さな値の表示などで出てきます。

既定の書式（`defaultfloat`）でも、桁数が多いと自動で指数表記に切り替わります。`scientific` は、それを常に強制する指定です。

## 実際に動かしてみる

```cpp
#include <iomanip>
#include <iostream>

int main() {
  std::cout << std::scientific;
  std::cout << 1234.5 << '\n';                           // 1.234500e+03
  std::cout << std::setprecision(2) << 1234.5 << '\n';   // 1.23e+03
  std::cout << 0.000123 << '\n';                         // 1.23e-04
  std::cout << std::uppercase << 1234.5 << '\n';         // 1.23E+03
}
```

```text title="実行結果"
1.234500e+03
1.23e+03
1.23e-04
1.23E+03
```

## ゲームでの使いどころ

物理演算の誤差、確率、非常に大きな座標など、桁の幅が広い値のデバッグ出力で使います。

`std::format("{:.2e}", v)` でも書けて、設定が残りません。

## よくあるミス

??? failure "戻し忘れて、あとの数値が全部指数表記になる"
    `std::defaultfloat` で戻します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fixed`](fixed.md) | 固定小数点にする |
| [`defaultfloat`](defaultfloat.md) | 既定の書式に戻す |
| [`hexfloat`](hexfloat.md) | 16 進の浮動小数点表記にする |

## コンパイラ対応

C++98 から使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] 指数表記で出す
    - [x] `setprecision` で仮数部の桁数
    - [x] 戻すのは `defaultfloat`

## 関連ページ

- [cpprefjp: std::scientific](https://cpprefjp.github.io/reference/ios/scientific.html)
- [cppreference: std::scientific](https://en.cppreference.com/w/cpp/io/manip/fixed)

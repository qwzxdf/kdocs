---
title: std::nearbyint
summary: "現在の丸めモード（既定は偶数丸め）で整数値にする。"
order: 39
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::nearbyint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

`std::round` は、0.5 のとき常に切り上げる四捨五入です。ところが、金融計算や統計では、0.5 を偶数側に丸める方法（銀行丸め）が使われます。偏りが出にくいからです。

`std::nearbyint` は、<strong>現在の丸めモードに従って整数に丸め</strong>、既定の丸めモードでは、0.5 の端数を偶数に寄せます。

!!! tip "ポイント"
    - `std::nearbyint(2.5)` は 2、`std::nearbyint(3.5)` は 4（偶数へ）
    - `std::round(2.5)` は 3。0.5 のとき切り上げる点が違う
    - 丸めモード（`fesetround`）で挙動が変わる
    - 戻り値は浮動小数点数。整数型に直接ほしいときは `lrint`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nearbyint {#nearbyint}

<span class="ver ver-11">C++11</span>

```cpp
float nearbyint(float x);
double nearbyint(double x);
long double nearbyint(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 丸めたい値 |

戻り値は、`x` に最も近い整数（浮動小数点数の型のまま）です。既定の丸めモード（最近接偶数）では、小数部がちょうど 0.5 のときは偶数の側に丸めます。2.5 は 2、3.5 は 4、−2.5 は −2 です。

丸めモードは `std::fesetround` で変えられ、切り上げ、切り捨て、0 方向への切り捨てにもできます。`nearbyint` はその設定に従います。

`std::rint` との違いは、不正確な結果を返したときに浮動小数点例外（`FE_INEXACT`）を立てないことです。例外のフラグを使わない普通のプログラムでは、違いは見えません。

`std::round` は丸めモードに関係なく「0.5 は絶対値の大きい方へ」と決まっています。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("nearbyint(2.5) = {}", std::nearbyint(2.5));   // 偶数の 2 へ
  std::println("nearbyint(3.5) = {}", std::nearbyint(3.5));   // 偶数の 4 へ
  std::println("round(2.5)     = {}", std::round(2.5));       // 3（遠い方へ）
  std::println("nearbyint(2.4) = {}", std::nearbyint(2.4));
}
```

```text title="実行結果"
nearbyint(2.5) = 2
nearbyint(3.5) = 4
round(2.5)     = 3
nearbyint(2.4) = 2
```

## ゲームでの使いどころ

統計や報酬の計算で、丸めによる偏りを避けたいときに使います。0.5 が半分は切り上げ、半分は切り捨てになるので、大量の値を丸めて足しても合計が偏りません。

```cpp
// 平均値の丸め。偶数丸めで偏りを抑える
const int rounded = static_cast<int>(std::nearbyint(average));
```

見た目の四捨五入が必要なら `round` を使います。

## よくあるミス

??? failure "`round` と同じだと思って、2.5 が 2 になって驚く"
    偶数丸めです。四捨五入が必要なら `std::round` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`round`](round.md) | 0.5 を常に絶対値の大きい方へ |
| [`lrint`](lrint.md) | 丸めて `long` で返す |
| [`floor`](floor.md) | 切り捨て（負の無限大方向） |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `nearbyint(x)` は現在の丸めモードで整数に丸める
    - [x] 既定では 0.5 を偶数側へ（2.5 は 2、3.5 は 4）
    - [x] 四捨五入は `round`、整数型で欲しいなら `lrint`

## 関連ページ

- [`std::round`](round.md)
- [cpprefjp: std::nearbyint](https://cpprefjp.github.io/reference/cmath/nearbyint.html)
- [cppreference: std::nearbyint](https://en.cppreference.com/w/cpp/numeric/math/nearbyint)

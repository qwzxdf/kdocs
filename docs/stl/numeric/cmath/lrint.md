---
title: std::lrint
summary: "現在の丸めモードで整数に丸める（long で返す）。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::lrint

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

座標を画面のピクセルに変換するとき、浮動小数点数を最も近い整数に丸め、そのまま `int` として使いたくなります。`static_cast<int>(std::round(x))` と書くこともできますが、`std::lrint` を使えば、丸めと整数への変換を 1 回で済ませます。

!!! tip "ポイント"
    - `std::lrint(2.7)` は 3（`long` 型）
    - 現在の丸めモードに従う。既定では 0.5 を偶数側へ
    - 戻り値が整数なので、`int` へ変換する手間が少ない
    - 結果が `long` に収まらないと、結果は不定

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::lrint {#lrint}

<span class="ver ver-11">C++11</span>

```cpp
long lrint(float x);
long lrint(double x);
long lrint(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 丸めたい値 |

戻り値は `x` を現在の丸めモードで整数に丸めた `long` の値です。既定の最近接偶数では、2.5 は 2、3.5 は 4 になります。

多くの CPU に、丸めと整数変換を 1 命令で行う命令があり、コンパイラはそれを使います。`static_cast<int>(x)` の切り捨てと、`round` の四捨五入のどちらとも違う動きなので、結果の意味に注意します。

`long` に収まらない値（大きすぎる値、NaN、無限大）を渡すと、結果は不定です。Windows の `long` は 32 ビットなので、約 21 億を超える値は危険です。大きな値には `llrint`（`long long`）を使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("lrint(2.7)  = {}", std::lrint(2.7));
  std::println("lrint(-2.7) = {}", std::lrint(-2.7));
  std::println("lrint(2.5)  = {}", std::lrint(2.5));    // 偶数の 2 へ
  std::println("lrint(3.5)  = {}", std::lrint(3.5));    // 偶数の 4 へ
}
```

```text title="実行結果"
lrint(2.7)  = 3
lrint(-2.7) = -3
lrint(2.5)  = 2
lrint(3.5)  = 4
```

## ゲームでの使いどころ

座標やスコアを丸めて整数にするときに使います。

```cpp
// 画面の座標（浮動小数点数）を最も近いピクセルに
const int px = static_cast<int>(std::lrint(position.x));
```

切り捨てが目的なら `static_cast<int>(x)` で足ります。四捨五入が必要なら `lround` が、0.5 の動きで期待どおりです。

## よくあるミス

??? failure "Windows の `long` は 32 ビットで、大きな値があふれる"
    `llrint` を使います。

??? failure "0.5 の端数が偶数に寄って、四捨五入と違う"
    `std::lround` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`llrint`](llrint.md) | `long long` で返す |
| [`nearbyint`](nearbyint.md) | 浮動小数点数のまま丸める |
| [`round`](round.md) | 四捨五入 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `lrint(x)` は丸めて `long` で返す
    - [x] 既定では 0.5 を偶数側へ。四捨五入とは違う
    - [x] Windows の `long` は 32 ビット。大きな値は `llrint`

## 関連ページ

- [`std::llrint`](llrint.md)
- [cpprefjp: std::lrint](https://cpprefjp.github.io/reference/cmath/lrint.html)
- [cppreference: std::lrint](https://en.cppreference.com/w/cpp/numeric/math/rint)

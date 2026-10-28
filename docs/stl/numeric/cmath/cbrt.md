---
title: std::cbrt
summary: "立方根（3 乗根）を求める。"
order: 21
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::cbrt

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

体積から、立方体の一辺の長さを求めたい。球の体積から半径を逆算したい。3 乗根が必要なとき、`pow(x, 1.0 / 3.0)` と書きたくなりますが、負の数を渡すと NaN になる落とし穴があります。

`std::cbrt` は、<strong>立方根を負の数も含めて正しく求める</strong>関数です。

!!! tip "ポイント"
    - `std::cbrt(27.0)` は 3、`std::cbrt(-8.0)` は −2
    - 負の数も受け取れる。`pow(-8.0, 1.0 / 3.0)` は NaN になる
    - `pow` より正確で、立方根専用の最適化もある
    - C++11 で追加

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::cbrt {#cbrt}

<span class="ver ver-11">C++11</span>

```cpp
float cbrt(float x);
double cbrt(double x);
long double cbrt(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 立方根を求めたい値。負の数でもよい |

戻り値は、3 乗すると `x` になる実数です。負の数に対しては、負の立方根を返します。`cbrt(0.0)` は 0、`cbrt(1.0)` は 1 です。無限大は無限大のまま、NaN は NaN を返します。

`pow(x, 1.0 / 3.0)` との違いは 2 つあります。1 つは負の数の扱いで、`pow` は負の底と非整数の指数で NaN を返します。もう 1 つは精度で、`1.0 / 3.0` は 3 分の 1 を正確に表せないため、`pow(27.0, 1.0 / 3.0)` が 3 ちょうどにならず、3.0000000000000004 のようになることがあります。`cbrt(27.0)` は 3 を返します。

定義域のエラーはありません。どの実数でも結果が定まるためです。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("cbrt(27)  = {}", std::cbrt(27.0));
  std::println("cbrt(-8)  = {}", std::cbrt(-8.0));
  std::println("cbrt(0.125) = {}", std::cbrt(0.125));

  // 体積 1000 の立方体の一辺
  std::println("一辺 = {}", std::cbrt(1000.0));
}
```

```text title="実行結果"
cbrt(27)  = 3
cbrt(-8)  = -2
cbrt(0.125) = 0.5
一辺 = 10
```

## ゲームでの使いどころ

体積から長さを求める場面で使います。ゲームでは、ダメージや範囲を体積に比例させたい場合に半径や一辺に戻すときなどです。

```cpp
// 体積 volume の球の半径
const float radius = std::cbrt(volume * 3.0f / (4.0f * std::numbers::pi_v<float>));
```

そのほか、色空間（Oklab など）の変換で立方根を使う式があります。負の値が混ざる計算でも `cbrt` は安全です。

## よくあるミス

??? failure "`pow(x, 1.0 / 3.0)` で立方根を求めて、負の数が NaN になる"
    `std::cbrt` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sqrt`](sqrt.md) | 平方根。負の数は NaN |
| [`pow`](pow.md) | 任意の累乗。負の底と小数の指数は NaN |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `cbrt(x)` は立方根。負の数も扱える
    - [x] `pow(x, 1.0 / 3.0)` より正確で、負の数も安全
    - [x] C++11 で追加

## 関連ページ

- [`std::sqrt`](sqrt.md)
- [cpprefjp: std::cbrt](https://cpprefjp.github.io/reference/cmath/cbrt.html)
- [cppreference: std::cbrt](https://en.cppreference.com/w/cpp/numeric/math/cbrt)

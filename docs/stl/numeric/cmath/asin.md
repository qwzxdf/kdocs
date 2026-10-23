---
title: std::asin
summary: "アークサイン（逆正弦）を求める。結果はラジアン。"
order: 6
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::asin

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

2 つの向きのなす角度を調べるとき、内積を取ると cos の値が手に入ります。正弦の値（例えば高さ ÷ 斜辺）から角度に戻したいなら、逆正弦の `std::asin` です。

`asin` が扱えるのは −1 〜 +1 の入力だけです。ゲームでは、計算の誤差で 1.0000001 のような値が混ざり、その瞬間に NaN が返って画面が壊れる、という事故がよく起きます。

!!! tip "ポイント"
    - `std::asin(1.0)` は π/2（約 1.571）。戻り値はラジアン
    - 定義域は −1 〜 +1。外れると NaN（定義域エラー）
    - 戻り値の範囲は −π/2 〜 +π/2
    - 誤差ではみ出すことがあるので、渡す前に `std::clamp(x, -1.0, 1.0)` で挟む

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::asin {#asin}

```cpp
float asin(float x);
double asin(double x);
long double asin(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 正弦の値。−1 〜 +1 の範囲 |

戻り値は、正弦が `x` になる角度で、ラジアンです。範囲は −π/2 〜 +π/2 になります。`asin(0)` は 0、`asin(1)` は π/2、`asin(-1)` は −π/2 です。

`x` が −1 〜 +1 を外れると、結果は NaN になります。`math_errhandling` の設定によっては `errno` に `EDOM` が入りますが、NaN を返すのが共通の動作です。

落とし穴は、正規化したベクトルから計算した値が、浮動小数点の誤差で 1 をわずかに超えることです。見た目は 1 なのに NaN が返るため、原因に気づきにくいバグになります。この誤差は避けられないので、渡す直前で範囲に収めます。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <cmath>
#include <print>

int main() {
  std::println("asin(0)   = {}", std::asin(0.0));
  std::println("asin(1)   = {}", std::asin(1.0));            // π/2
  // 誤差で 1 を超えた値でも、clamp で挟めば安全
  const double dot = 1.0000001;
  std::println("安全版   = {}", std::asin(std::clamp(dot, -1.0, 1.0)));
}
```

```text title="実行結果"
asin(0)   = 0
asin(1)   = 1.5707963267948966
安全版   = 1.5707963267948966
```

## ゲームでの使いどころ

「高さ ÷ 斜辺」のような比から、斜面や視線の仰角を求めるときに使います。

```cpp
// 視線ベクトル (正規化済み) の仰角。y 成分がそのまま sin(仰角)
const float pitch = std::asin(std::clamp(look.y, -1.0f, 1.0f));
```

2 本のベクトルのなす角を求めるときは、`asin` より `acos` を使うほうが一般的です（内積が cos になるため）。

## よくあるミス

??? failure "範囲外の値で NaN になり、画面が壊れる"
    `std::clamp(x, -1.0, 1.0)` を通してから渡します。

??? failure "2 本のベクトルの角度に `asin` を使い、鈍角を取り違える"
    `asin` の範囲は −π/2 〜 π/2 で、鈍角を表せません。内積と `acos` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`acos`](acos.md) | 逆余弦。内積から角度を求める。範囲は 0 〜 π |
| [`atan2`](atan2.md) | 2 成分から象限まで区別して角度を求める |
| [`sin`](sin.md) | 正弦。`asin` の逆 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `asin(x)` は正弦が `x` になる角度（ラジアン、−π/2 〜 π/2）
    - [x] 定義域は −1 〜 +1。外れると NaN
    - [x] 誤差ではみ出すので、`clamp` で挟んでから渡す

## 関連ページ

- [`std::acos`](acos.md)
- [cpprefjp: std::asin](https://cpprefjp.github.io/reference/cmath/asin.html)
- [cppreference: std::asin](https://en.cppreference.com/w/cpp/numeric/math/asin)

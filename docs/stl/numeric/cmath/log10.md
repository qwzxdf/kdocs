---
title: std::log10
summary: "底が 10 の対数を求める。"
order: 20
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::log10

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

スコアを画面に出すとき、桁数が分かれば表示の幅が決まります。音の大きさを表すデシベルは、10 を底とする対数で定義されています。「10 を何乗したらこの値になるか」を返すのが、常用対数の `std::log10` です。

!!! tip "ポイント"
    - `std::log10(1000.0)` は 3、`std::log10(0.01)` は −2
    - `x` は正の数。0 は −∞、負の数は NaN
    - 正の整数の桁数は `floor(log10(n)) + 1`
    - 音量（デシベル）への換算は `20 * log10(振幅比)`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::log10 {#log10}

```cpp
float log10(float x);
double log10(double x);
long double log10(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 正の数。底 10 の対数を取りたい値 |

戻り値は、10 を何乗すると `x` になるかです。1 のとき 0、10 のとき 1、100 のとき 2、0.1 のとき −1 になります。`x` が 0 なら −∞、負の値なら NaN です。

10 の累乗では、結果がちょうど整数になります。`log(x) / log(10)` では誤差で 2.9999999999999996 になるような場合でも、`log10` は 3 を返します。桁数を求める式では、この違いで結果が 1 ずれるため、必ず `log10` を使います。

桁数は、`n` が 1 以上の整数なら、`static_cast<int>(std::log10(n)) + 1` で求まります。ただし 0 の桁数は特別に扱います。`log10(0)` が −∞ になるためです。

デシベルは、振幅の比の対数で、`20 * log10(a / a0)` です。電力の比なら係数が 10 になります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("log10(1000) = {}", std::log10(1000.0));
  std::println("log10(0.01) = {}", std::log10(0.01));

  // スコアの桁数（0 は 1 桁として別に扱う）
  const int score = 12345;
  const int digits = score == 0 ? 1 : static_cast<int>(std::log10(score)) + 1;
  std::println("{} は {} 桁", score, digits);
}
```

```text title="実行結果"
log10(1000) = 3
log10(0.01) = -2
12345 は 5 桁
```

## ゲームでの使いどころ

スコア表示の桁数と、音量のデシベル換算が主な用途です。

```cpp
// 振幅の比（1.0 が基準）をデシベルに変換
const float db = 20.0f * std::log10(amplitude);   // 半分の振幅なら約 −6 dB
```

デシベルは、振幅が 0 のとき −∞ になります。ミュートの扱いが必要なら、小さな下限値を設けて計算します。

## よくあるミス

??? failure "0 を渡して −∞ になり、桁数が壊れる"
    0 は別に扱い、1 桁とします。

??? failure "`log(x) / log(10)` で桁数がずれる"
    `std::log10` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log`](log.md) | 自然対数（底 e） |
| [`log2`](log2.md) | 底 2 の対数 |
| [`to_string`](../../containers/to_string.md) | 文字列にしてから長さを数える方法もある |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `log10(x)` は底 10 の対数。`log10(1000)` は 3
    - [x] 桁数は `log10(n)` を切り捨てて 1 を足す（0 は別扱い）
    - [x] デシベルは `20 * log10(振幅比)`

## 関連ページ

- [`std::log`](log.md)
- [cpprefjp: std::log10](https://cpprefjp.github.io/reference/cmath/log10.html)
- [cppreference: std::log10](https://en.cppreference.com/w/cpp/numeric/math/log10)

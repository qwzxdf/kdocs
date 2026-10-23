---
title: std::log2
summary: "底が 2 の対数を求める。"
order: 19
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::log2

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

256 は 2 を何回掛けた数か。テクスチャの一辺が 1024 なら、ミップマップは何段か。「2 を何乗したらこの値になるか」を知りたい場面は、グラフィックスで頻繁に出てきます。

`std::log2` は、<strong>底が 2 の対数</strong>を返します。`log(x) / log(2)` と書くこともできますが、`log2` を使えば 2 の累乗でぴったりの整数が返ります。

!!! tip "ポイント"
    - `std::log2(8.0)` は 3、`std::log2(1024.0)` は 10
    - `x` は正の数。0 は −∞、負の数は NaN
    - 2 の累乗の入力では、結果がちょうど整数になる（`log(x) / log(2)` では誤差が出ることがある）
    - 整数のビット数を知りたいだけなら `std::bit_width` のほうが速く確実

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::log2 {#log2}

<span class="ver ver-11">C++11</span>

```cpp
float log2(float x);
double log2(double x);
long double log2(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 正の数。底 2 の対数を取りたい値 |

戻り値は、2 を何乗すると `x` になるかです。`log2(1.0)` は 0、`log2(2.0)` は 1、`log2(0.5)` は −1 になります。

`x` が 0 のときは −∞、負の値のときは NaN です。`log` と同じ扱いです。

`log(x) / log(2.0)` との違いは精度です。この式だと、`x` が 2 の累乗でも、割り算の丸め誤差で 2.9999999999999996 のような値になることがあり、整数に切り捨てると 1 小さくなります。`log2` はこの問題を避けるよう作られているので、2 の累乗でちょうどの値が返ります。

ミップマップの段数のように、結果を整数に切り捨てて使う場合は、`log2` の値を `floor` で丸めます。ただし、整数の `x` に対しては、`std::bit_width(x) - 1` のほうが誤差の心配がなく、速いです。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("log2(8)    = {}", std::log2(8.0));
  std::println("log2(1024) = {}", std::log2(1024.0));
  std::println("log2(0.5)  = {}", std::log2(0.5));

  // 1024x1024 のテクスチャのミップマップの段数（1024, 512, ..., 1 の 11 段）
  const int size = 1024;
  std::println("ミップの段数 = {}", static_cast<int>(std::log2(size)) + 1);
}
```

```text title="実行結果"
log2(8)    = 3
log2(1024) = 10
log2(0.5)  = -1
ミップの段数 = 11
```

## ゲームでの使いどころ

テクスチャの大きさからミップマップの段数を求めるのが代表的な使い方です。

```cpp
// 幅と高さのうち大きいほうから、ミップの段数を決める
const int mip_levels = static_cast<int>(std::log2(std::max(width, height))) + 1;
```

そのほか、2 倍ごとに 1 段上がる量（レベル、音階の 1 オクターブ）を扱うときにも使います。

## よくあるミス

??? failure "`log(x) / log(2)` で、ちょうどの整数にならない"
    `std::log2` を使います。

??? failure "0 や負の値を渡して −∞ や NaN になる"
    呼ぶ前に 1 以上であることを確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`log`](log.md) | 自然対数（底 e） |
| [`log10`](log10.md) | 底 10 の対数 |
| [`bit_width`](../bit/bit_width.md) | 整数を表すのに必要なビット数。整数なら誤差なし |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `log2(x)` は底 2 の対数。2 の累乗でちょうどの整数が返る
    - [x] `x` が 0 は −∞、負は NaN
    - [x] 整数のビット数なら `std::bit_width` を使う

## 関連ページ

- [`std::log`](log.md)
- [cpprefjp: std::log2](https://cpprefjp.github.io/reference/cmath/log2.html)
- [cppreference: std::log2](https://en.cppreference.com/w/cpp/numeric/math/log2)

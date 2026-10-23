---
title: std::remainder
summary: "小数の余り。商を四捨五入で決めるので、負になることがある。"
order: 29
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::remainder

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

角度を −180 度〜+180 度の範囲に収めたい。`fmod(angle, 360)` では 0〜360 になってしまい、−180〜180 にするには場合分けが要ります。

`std::remainder` は、<strong>割り算の商を最も近い整数に丸めたときの余り</strong>を返します。結果は −y/2 〜 +y/2 の範囲に収まるので、角度の正規化にぴったりです。

!!! tip "ポイント"
    - `std::remainder(7.0, 2.0)` は −1（商 3.5 を偶数 4 に丸め、7 − 4×2）
    - 結果の範囲は −|y|/2 〜 +|y|/2
    - `fmod` は商を 0 方向へ切り捨てる。余りの符号が x に従う
    - 角度の正規化（−180°〜+180°）に便利

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::remainder {#remainder}

<span class="ver ver-11">C++11</span>

```cpp
float remainder(float x, float y);
double remainder(double x, double y);
long double remainder(long double x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 割られる数 |
| `y` | 浮動小数点数 | 割る数。0 だと NaN |

戻り値は `x - n * y` で、`n` は `x / y` に最も近い整数です。`x / y` がちょうど 0.5 の端数のときは、偶数側の `n` を選びます。

`fmod` との違いは `n` の決め方です。`fmod` は `x / y` を 0 方向へ切り捨てた整数を `n` にするため、余りの符号は `x` に従い、範囲は 0 〜 `y` の手前です。`remainder` は最も近い整数なので、範囲は −y/2 〜 +y/2 に収まります。

`y` が 0 のとき、または `x` が無限大のときは NaN を返します。

偶数側に丸める規則のせいで、`remainder(7.0, 2.0)` は −1、`remainder(5.0, 2.0)` は 1 と、見かけが揃いません。商がちょうど 0.5 の端数になる値を渡すときだけ起きます。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("remainder(7, 2)     = {}", std::remainder(7.0, 2.0));     // 3.5 → 4 に丸め → 7 - 8
  std::println("remainder(5, 2)     = {}", std::remainder(5.0, 2.0));     // 2.5 → 2 に丸め → 5 - 4
  std::println("fmod(7, 2)          = {}", std::fmod(7.0, 2.0));           // 切り捨て → 7 - 6
  // 角度を −180 〜 +180 に収める
  std::println("remainder(270, 360) = {}", std::remainder(270.0, 360.0));
}
```

```text title="実行結果"
remainder(7, 2)     = -1
remainder(5, 2)     = 1
fmod(7, 2)          = 1
remainder(270, 360) = -90
```

## ゲームでの使いどころ

角度の正規化に使います。270 度は −90 度と同じ向きで、−180 〜 +180 の範囲で表すと、回転の差を最短経路で扱えます。

```cpp
// 現在の向きと目標の向きの差を、最短の回転量（−180〜+180 度）で求める
const float diff = std::remainder(target - current, 360.0f);
```

## よくあるミス

??? failure "`fmod` と同じだと思って使い、符号が違って驚く"
    `fmod` は切り捨て、`remainder` は最も近い整数に丸めます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`fmod`](fmod.md) | 商を 0 方向へ切り捨てた余り |
| [`remquo`](remquo.md) | 余りと商の下位ビットを同時に返す |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `remainder(x, y)` は商を最も近い整数に丸めた余り
    - [x] 結果は −y/2 〜 +y/2。角度の正規化向き
    - [x] `fmod` は切り捨て

## 関連ページ

- [`std::fmod`](fmod.md)
- [cpprefjp: std::remainder](https://cpprefjp.github.io/reference/cmath/remainder.html)
- [cppreference: std::remainder](https://en.cppreference.com/w/cpp/numeric/math/remainder)

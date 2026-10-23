---
title: std::fmod
summary: "小数の割り算の余りを求める。"
order: 16
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fmod

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

整数の剰余 `%` は、浮動小数点数には使えません。角度を 360 度の範囲に収める、時間を周期で折り返す。小数の余りが必要なときに使うのが `std::fmod` です。

!!! tip "ポイント"
    - `std::fmod(7.0, 2.0)` は 1
    - 商を 0 方向に切り捨てた余り。符号は割られる数に従う
    - `y` が 0 なら NaN
    - 負の値を 0 以上に収めたいときは、`fmod` のあとに `y` を足して、もう一度 `fmod`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fmod {#fmod}

```cpp
float fmod(float x, float y);
double fmod(double x, double y);
long double fmod(long double x, long double y);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 割られる数 |
| `y` | 浮動小数点数 | 割る数。0 は不可 |

戻り値は `x - n * y` で、`n` は `x / y` を 0 方向に切り捨てた整数です。余りの符号は `x` と同じで、絶対値は `y` の絶対値より小さくなります。

整数の `%` と同じ規則です。`fmod(-7.0, 2.0)` は −1 で、0 以上の余りにはなりません。角度を 0〜360 に収めたいときは、負の値の面倒を見る必要があります。

```cpp
float Wrap360(float degrees) {
  float r = std::fmod(degrees, 360.0f);
  return r < 0 ? r + 360.0f : r;     // 負なら 360 を足して 0 以上にする
}
```

`y` が 0 のとき、`x` が無限大のとき、いずれかが NaN のときは NaN です。

最も近い整数で丸めた余り（−y/2 〜 +y/2）が欲しいときは、[`remainder`](remainder.md) です。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("fmod(7, 2)     = {}", std::fmod(7.0, 2.0));
  std::println("fmod(-7, 2)    = {}", std::fmod(-7.0, 2.0));     // 符号は x に従う
  std::println("fmod(5.5, 2)   = {}", std::fmod(5.5, 2.0));
  std::println("fmod(450, 360) = {}", std::fmod(450.0, 360.0));  // 角度の折り返し
}
```

```text title="実行結果"
fmod(7, 2)     = 1
fmod(-7, 2)    = -1
fmod(5.5, 2)   = 1.5
fmod(450, 360) = 90
```

## ゲームでの使いどころ

回転角が 360 度を超えたら折り返す、アニメーションの時間を周期でループさせる、といった処理で使います。

```cpp
// 経過時間を 2 秒の周期で折り返し、0〜2 の範囲にする
const float phase = std::fmod(elapsed, 2.0f);
```

## よくあるミス

??? failure "負の値が 0 以上の余りになると思う"
    `r < 0` のときに `y` を足して補正します。

??? failure "`y` が 0 で NaN になる"
    周期が 0 にならないか確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`remainder`](remainder.md) | 最も近い整数で丸めた余り |
| [`floor`](floor.md) | 切り捨て |
| [`div`](../cstdlib/div.md) | 整数の商と余り |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fmod(x, y)` は小数の余り。符号は `x` に従う
    - [x] `y` が 0 なら NaN
    - [x] 負の値を 0 以上に収めるには補正が要る

## 関連ページ

- [cpprefjp: std::fmod](https://cpprefjp.github.io/reference/cmath/fmod.html)
- [cppreference: std::fmod](https://en.cppreference.com/w/cpp/numeric/math/fmod)

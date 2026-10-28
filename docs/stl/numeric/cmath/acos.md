---
title: std::acos
summary: "アークコサイン（逆余弦）を求める。結果はラジアン。"
order: 7
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::acos

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

2 本のベクトルのなす角を求めたい。敵が自分の正面から何度ずれた方向にいるか、視野に入っているか。正規化した 2 本のベクトルの内積は、そのなす角の余弦（cos）になります。内積から角度に戻すのが、逆余弦の `std::acos` です。

!!! tip "ポイント"
    - `std::acos(1.0)` は 0、`std::acos(0.0)` は π/2、`std::acos(-1.0)` は π
    - 定義域は −1 〜 +1。外れると NaN
    - 戻り値の範囲は 0 〜 π（0 度〜180 度）
    - 誤差ではみ出すことがあるので、`std::clamp(x, -1.0, 1.0)` で挟んでから渡す

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::acos {#acos}

```cpp
float acos(float x);
double acos(double x);
long double acos(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 余弦の値。−1 〜 +1 の範囲 |

戻り値は、余弦が `x` になる角度で、単位はラジアン、範囲は 0 〜 π です。`acos(1)` は 0（同じ向き）、`acos(0)` は π/2（直角）、`acos(-1)` は π（逆向き）です。

`x` が −1 〜 +1 を外れると NaN になります。正規化したはずのベクトルでも、計算の誤差で内積が 1.0000001 になることがあり、その瞬間に NaN が返って角度の計算が壊れます。呼ぶ直前に `std::clamp` で挟むのが定石です。

範囲が 0 〜 π なので、返るのは「ずれの大きさ」だけで、右にずれたか左にずれたかは分かりません。向き（符号）まで必要なら、外積の符号を別に調べるか、`atan2` を使います。

## 実際に動かしてみる

```cpp
#include <algorithm>
#include <cmath>
#include <numbers>
#include <print>

int main() {
  // (1,0) と (0,1) のなす角: 内積は 0
  const double dot = 1.0 * 0.0 + 0.0 * 1.0;
  const double angle = std::acos(std::clamp(dot, -1.0, 1.0));
  std::println("ラジアン = {}", angle);
  std::println("度       = {:.1f}", angle * 180.0 / std::numbers::pi);
  std::println("acos(1)  = {}", std::acos(1.0));
}
```

```text title="実行結果"
ラジアン = 1.5707963267948966
度       = 90.0
acos(1)  = 0
```

## ゲームでの使いどころ

視野の判定に使います。自分の正面と、敵の方向のなす角が視野角の半分以内なら「見えている」と判定します。

```cpp
// forward と to_enemy は正規化済み
const float angle = std::acos(std::clamp(Dot(forward, to_enemy), -1.0f, 1.0f));
const bool visible = angle < fov_half;
```

角度そのものが要らず、「視野内か」の判定だけなら、`acos` を呼ばずに内積と `cos(fov_half)` を比べるほうが速くなります。

## よくあるミス

??? failure "範囲外の値で NaN になり、画面や判定が壊れる"
    `std::clamp(x, -1.0, 1.0)` を通してから渡します。

??? failure "符号つきの角度（左右の区別）を期待する"
    範囲は 0 〜 π です。左右の区別には外積か `atan2` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`asin`](asin.md) | 逆正弦 |
| [`atan2`](atan2.md) | 2 成分から符号つきの角度を求める |
| [`cos`](cos.md) | 余弦。`acos` の逆 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `acos(x)` は余弦が `x` になる角度（ラジアン、0 〜 π）
    - [x] 定義域は −1 〜 +1。外れると NaN。`clamp` で挟む
    - [x] 2 本のベクトルのなす角は `acos(dot)`

## 関連ページ

- [cpprefjp: std::acos](https://cpprefjp.github.io/reference/cmath/acos.html)
- [cppreference: std::acos](https://en.cppreference.com/w/cpp/numeric/math/acos)

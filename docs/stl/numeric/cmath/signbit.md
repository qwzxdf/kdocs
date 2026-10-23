---
title: std::signbit
summary: "符号ビットが立っているか（負か）を調べる。"
order: 27
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::signbit

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`x < 0` で負かどうかは判定できますが、`-0.0` は `0` と等しいので、`-0.0 < 0` は偽になります。符号つきゼロや NaN の符号まで正しく調べたいときに使うのが `std::signbit` です。

!!! tip "ポイント"
    - `std::signbit(-1.0)` は `true`、`std::signbit(1.0)` は `false`
    - `-0.0` に対しても `true` を返す
    - NaN の符号ビットも調べられる
    - 通常の「負か」の判定は `x < 0` で足りる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::signbit {#signbit}

<span class="ver ver-11">C++11</span>

```cpp
bool signbit(float x);
bool signbit(double x);
bool signbit(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 符号ビットを調べたい値 |

戻り値は、符号ビットが立っていれば `true`、立っていなければ `false` です。IEEE 754 の浮動小数点数は、最上位の 1 ビットが符号で、これを直接見る関数です。

`x < 0` との違いは、`-0.0` です。`-0.0` は `0.0` と比較して等しいので `-0.0 < 0` は偽ですが、符号ビットは立っているので `signbit(-0.0)` は `true` です。また NaN は、すべての大小比較が偽になりますが、`signbit` は NaN の符号ビットを返します。

この違いが効くのは、符号つきゼロの意味を保つ必要がある計算（極限の向き、`atan2` の結果の分岐など）です。ゲームの普通の計算では、`x < 0` で十分です。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("signbit(-1.0) = {}", std::signbit(-1.0));
  std::println("signbit(1.0)  = {}", std::signbit(1.0));
  std::println("signbit(-0.0) = {}", std::signbit(-0.0));   // 符号つきゼロも拾う
  std::println("-0.0 < 0     = {}", -0.0 < 0.0);             // 比較では偽になる
}
```

```text title="実行結果"
signbit(-1.0) = true
signbit(1.0)  = false
signbit(-0.0) = true
-0.0 < 0     = false
```

## ゲームでの使いどころ

符号つきゼロを区別したいとき、または符号ビットだけを分岐に使うときに登場します。

```cpp
// 速度がゼロでも、-0.0 なら「左向きに止まった」とみなす
const bool facing_left = std::signbit(velocity.x);
```

通常の判定では `x < 0` のほうが読みやすいので、符号つきゼロを気にする理由がなければそちらを使います。

## よくあるミス

??? failure "`-0.0` を負でないと判定してしまう"
    `x < 0` は `-0.0` に対して偽です。必要なら `signbit` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`copysign`](copysign.md) | 符号をコピーする |
| [`fabs`](fabs.md) | 絶対値 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `signbit(x)` は符号ビットが立っているか
    - [x] `-0.0` と NaN の符号も調べられる
    - [x] 普通の「負か」の判定は `x < 0` で十分

## 関連ページ

- [`std::copysign`](copysign.md)
- [cpprefjp: std::signbit](https://cpprefjp.github.io/reference/cmath/signbit.html)
- [cppreference: std::signbit](https://en.cppreference.com/w/cpp/numeric/math/signbit)

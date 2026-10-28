---
title: std::ilogb
summary: "x の指数部（2 を底とした対数の整数部分）を int で返す。"
order: 900
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::ilogb

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

浮動小数点数の値が 2 の何乗くらいの大きさか。`log2` で求めて切り捨てる方法は、浮動小数点の誤差があります。`std::ilogb` は、<strong>値の指数部を誤差なく整数で取り出し</strong>ます。

!!! tip "ポイント"
    - `std::ilogb(8.0)` は 3、`std::ilogb(0.5)` は −1
    - `floor(log2(|x|))` を誤差なく求める
    - 0 は `FP_ILOGB0`、NaN は `FP_ILOGBNAN` を返す
    - 戻り値は `int`。浮動小数点数の `logb` もある

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::ilogb {#ilogb}

<span class="ver ver-11">C++11</span>

```cpp
int ilogb(float x);
int ilogb(double x);
int ilogb(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 指数を調べたい値 |

戻り値は、`x` を `m × 2^e`（`m` は 1 以上 2 未満）の形に表したときの `e` です。`ilogb(8.0)` は 3（8 = 1.0 × 2³）、`ilogb(10.0)` は 3（10 = 1.25 × 2³）、`ilogb(0.5)` は −1 です。

`x` が 0 のときは `FP_ILOGB0`、NaN のときは `FP_ILOGBNAN`、無限大のときは `INT_MAX` を返す、といった特別な値になります。これらを区別したいときは、定数と比べます。

`log2` と違い、指数部を直接読むだけなので、誤差がなく、とても速いです。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("ilogb(8)    = {}", std::ilogb(8.0));
  std::println("ilogb(10)   = {}", std::ilogb(10.0));
  std::println("ilogb(0.5)  = {}", std::ilogb(0.5));
}
```

```text title="実行結果"
ilogb(8)    = 3
ilogb(10)   = 3
ilogb(0.5)  = -1
```

## ゲームでの使いどころ

値の大きさの桁（2 の何乗か）を誤差なく求めたいときに使います。

```cpp
// 距離がどの 2 の累乗の範囲にあるか（LOD の段の決定など）
const int level = std::ilogb(distance / near_distance);
```

## よくあるミス

??? failure "0 を渡して特別な値が返る"
    `FP_ILOGB0` を確かめます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`logb`](logb.md) | 指数を浮動小数点数で返す |
| [`log2`](log2.md) | 底 2 の対数 |
| [`frexp`](frexp.md) | 仮数と指数に分ける |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `ilogb(x)` は指数部を整数で返す
    - [x] `floor(log2(|x|))` を誤差なく求める
    - [x] 0 と NaN は特別な値

## 関連ページ

- [cpprefjp: std::ilogb](https://cpprefjp.github.io/reference/cmath/ilogb.html)
- [cppreference: std::ilogb](https://en.cppreference.com/w/cpp/numeric/math/ilogb)

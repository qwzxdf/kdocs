---
title: std::isnan
summary: "値が NaN（数ではない）かを調べる。"
order: 23
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::isnan

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

0 を 0 で割る、負の数の平方根を取る、無限大から無限大を引く。そうした計算の失敗は、浮動小数点数では NaN（Not a Number）という特別な値になり、以降の計算に広がります。NaN は、自分自身とも等しくない（`nan == nan` が偽）ので、普通の比較では検出できません。

`std::isnan` は、<strong>値が NaN か</strong>を調べる関数です。

!!! tip "ポイント"
    - `std::isnan(x)` は NaN のとき `true`
    - `x == x` が偽になるのが NaN の性質
    - `x == NAN` では検出できない（常に偽）
    - 無限大も一緒に調べるなら `isfinite`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::isnan {#isnan}

<span class="ver ver-11">C++11</span>

```cpp
bool isnan(float x);
bool isnan(double x);
bool isnan(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 調べたい値 |

戻り値は、`x` が NaN なら `true`、そうでなければ `false` です。無限大は NaN ではないので `false` です。

NaN は、すべての比較（`<`、`>`、`==`）が偽になります。`nan == nan` も偽です。そのため、`if (x == NAN)` のような比較では絶対に検出できません。必ず `isnan` を使います。

NaN は伝染します。NaN を含む計算の結果は NaN になるので、ある時点で入り込むと、画面の座標や物理の値が壊れて、原因の場所が分からなくなります。デバッグ中は、更新のたびに `isnan` を確かめる `assert` を置くと、早い段階で場所を絞れます。

`-ffast-math` を指定すると、コンパイラが NaN が出ないと仮定して、`isnan` が常に `false` になることがあります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <limits>
#include <print>

int main() {
  const double nan = std::numeric_limits<double>::quiet_NaN();
  std::println("isnan(nan) = {}", std::isnan(nan));
  std::println("isnan(1.0) = {}", std::isnan(1.0));
  std::println("nan == nan = {}", nan == nan);      // 比較では検出できない
}
```

```text title="実行結果"
isnan(nan) = true
isnan(1.0) = false
nan == nan = false
```

## ゲームでの使いどころ

計算結果の検証に使います。

```cpp
position += velocity * dt;
assert(!std::isnan(position.x));   // NaN が混ざったら、この場所で止まる
```

リリース版では `assert` が外れます。外部から読むデータは、`if` で検査してエラーにします。

## よくあるミス

??? failure "`x == NAN` で検出しようとして、常に偽になる"
    `std::isnan(x)` を使います。

??? failure "`-ffast-math` で検出できなくなる"
    この最適化は NaN を仮定から外すので、検出が必要なコードでは使いません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`isinf`](isinf.md) | 無限大か |
| [`isfinite`](isfinite.md) | NaN でも無限大でもないか |
| [`nan`](nan.md) | NaN を作る |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `isnan(x)` は NaN のとき `true`
    - [x] NaN は自分自身とも等しくない。`==` では検出できない
    - [x] `-ffast-math` では検出できなくなる

## 関連ページ

- [cpprefjp: std::isnan](https://cpprefjp.github.io/reference/cmath/isnan.html)
- [cppreference: std::isnan](https://en.cppreference.com/w/cpp/numeric/math/isnan)

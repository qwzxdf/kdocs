---
title: std::fetestexcept
summary: "浮動小数点例外のフラグを調べる。"
order: 900
group: 浮動小数点環境（<cfenv>）
tags:
  - 数値
---

# std::fetestexcept

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cfenv>`
</div>

0 で割った、オーバーフローした、結果が不正確だった。浮動小数点の計算は、こうした異常を例外にせず、結果の値（無限大や NaN）にして流します。ただし、CPU は異常が起きたことをフラグに記録しています。`std::fetestexcept` は、<strong>そのフラグを読み取り</strong>ます。

!!! tip "ポイント"
    - `std::fetestexcept(FE_DIVBYZERO)` で 0 除算が起きたかを調べる
    - 戻り値は、立っていたフラグのビット（0 なら何も起きていない）
    - 調べたいフラグを `|` でまとめて渡せる
    - 調べる前に `feclearexcept` で消しておく

!!! info "このページを読む前に"
    [STL](../index.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fetestexcept {#fetestexcept}

<span class="ver ver-11">C++11</span>

```cpp
int fetestexcept(int excepts);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `excepts` | `int` | 調べたいフラグ。`FE_DIVBYZERO`、`FE_INEXACT`、`FE_INVALID`、`FE_OVERFLOW`、`FE_UNDERFLOW` の組み合わせ（`FE_ALL_EXCEPT` で全部） |

`excepts` で指定したフラグのうち、現在立っているものをビットで返します。何も立っていなければ 0 です。

フラグは、立つと自動では消えません。計算の前に `feclearexcept` で消してから、計算をして、`fetestexcept` で調べる、という手順が基本です。

見張れる異常は 5 つです。`FE_DIVBYZERO` は 0 除算、`FE_INVALID` は無効な演算（0/0、負の平方根など）、`FE_OVERFLOW` は結果が大きすぎる、`FE_UNDERFLOW` は結果が小さすぎる、`FE_INEXACT` は丸めが発生した（ほぼ常に立つ）です。

計算の途中で NaN や無限大が出たかをあとで 1 回だけ確かめられるので、各計算に `isnan` を書くより簡潔になる場面があります。


浮動小数点環境を変えたり、例外フラグを読んだりするコードは、コンパイラの最適化で並べ替えられたり、定数に畳み込まれたりすることがあります。結果が期待と違うときは、`volatile` を使うか、最適化に関するオプション（上のコンパイラ対応を参照）を確かめます。

## 実際に動かしてみる

```cpp
#include <cfenv>
#include <print>

int main() {
  std::feclearexcept(FE_ALL_EXCEPT);
  volatile double zero = 0.0;
  const double r = 1.0 / zero;                       // 0 除算（結果は無限大）
  (void)r;
  std::println("0 除算が起きた: {}", std::fetestexcept(FE_DIVBYZERO) != 0);

  std::feclearexcept(FE_ALL_EXCEPT);
  std::println("消したあと     : {}", std::fetestexcept(FE_DIVBYZERO) != 0);
}
```

```text title="実行結果"
0 除算が起きた: true
消したあと     : false
```

## ゲームでの使いどころ

物理シミュレーションの 1 ステップが終わったあとに、不正な計算が起きなかったかを確かめます。

```cpp
std::feclearexcept(FE_ALL_EXCEPT);
StepPhysics(dt);
if (std::fetestexcept(FE_INVALID | FE_DIVBYZERO)) {
  LogWarning("物理の計算で不正な演算が発生");
}
```

## よくあるミス

??? failure "フラグを消さずに調べて、前の計算の結果を拾う"
    計算の前に `feclearexcept` を呼びます。

??? failure "`FE_INEXACT` を異常だと思う"
    ほぼ全ての計算で立ちます。異常の検出には使いません。

## 類似

| 名前 | 違い |
| --- | --- |
| [`feclearexcept`](feclearexcept.md) | フラグを消す |
| [`feraiseexcept`](feraiseexcept.md) | フラグを立てる |
| [`isnan`](cmath/isnan.md) | 個々の値が NaN か |

## コンパイラ対応

C++11 から使えます。`<cfenv>` で宣言されます。主要なコンパイラのすべてで使えます。ただし、浮動小数点環境へのアクセスを最適化に伝えるため、GCC は `-frounding-math`、MSVC は `#pragma fenv_access(on)` が必要な場面があります。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fetestexcept` は浮動小数点の異常フラグを読む
    - [x] 計算の前に `feclearexcept` で消しておく
    - [x] 5 種類のフラグ。`FE_INEXACT` は異常ではない

## 関連ページ

- [cpprefjp: std::fetestexcept](https://cpprefjp.github.io/reference/cfenv/fetestexcept.html)
- [cppreference: std::fetestexcept](https://en.cppreference.com/w/cpp/numeric/fenv/fetestexcept)

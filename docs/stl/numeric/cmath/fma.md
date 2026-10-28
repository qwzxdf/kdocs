---
title: std::fma
summary: "`x * y + z` を、丸めを 1 回だけで計算する。"
order: 22
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::fma

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

`a * b + c` は、ゲームのあらゆる場所に出てくる形です。ベクトルの内積、線形補間、行列の掛け算。普通に書くと、掛け算の結果を一度丸めてから、足し算をもう一度丸めます。

`std::fma`（fused multiply-add）は、<strong>掛け算と足し算を 1 回の丸めでまとめて</strong>行います。丸めが 1 回少ないぶん正確で、対応した CPU では 1 命令で済むため速いこともあります。

!!! tip "ポイント"
    - `std::fma(2.0, 3.0, 4.0)` は 10（2 × 3 + 4）
    - 途中の掛け算を丸めないので、`a * b + c` より誤差が小さい
    - ハードウェアの FMA 命令があれば 1 命令。なければソフトウェアで遅くなる
    - 結果が `a * b + c` とわずかに違うことがある

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::fma {#fma}

<span class="ver ver-11">C++11</span>

```cpp
float fma(float x, float y, float z);
double fma(double x, double y, double z);
long double fma(long double x, long double y, long double z);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 掛ける 1 つ目 |
| `y` | 浮動小数点数 | 掛ける 2 つ目 |
| `z` | 浮動小数点数 | 足す値 |

戻り値は `x * y + z` を途中で丸めずに計算してから最後に 1 回だけ丸めた値です。

普通の `x * y + z` は、掛け算の結果を型の精度に丸めて、そのあと足し算の結果をもう一度丸めます。2 回の丸めで誤差が生じます。`fma` は、掛け算の結果を無限の精度で保ってから足すので、誤差が最大でも 1 回分で済みます。

速度は環境によります。FMA 命令を持つ CPU（近年の x86-64、ARM）では、コンパイラが 1 命令に置き換えます。持たない環境では、ソフトウェアで同じ精度を再現するため、かなり遅くなります。ゲームの計算で使う場合は、対象の CPU が FMA に対応しているかを確かめます。

コンパイラは、`a * b + c` と書かれたコードを最適化の設定によって自動で `fma` に変えることがあります（`-ffp-contract`）。その場合、同じソースでもコンパイラや設定によって結果が少し異なります。結果がビット単位で一致する必要がある場面（ネットワークの同期など）では、この違いに注意します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("fma(2, 3, 4)   = {}", std::fma(2.0, 3.0, 4.0));    // 2 * 3 + 4
  std::println("fma(0.5, 8, 1) = {}", std::fma(0.5, 8.0, 1.0));    // 0.5 * 8 + 1
}
```

```text title="実行結果"
fma(2, 3, 4)   = 10
fma(0.5, 8, 1) = 5
```

## ゲームでの使いどころ

線形補間（lerp）を誤差を抑えて書くときに使えます。

```cpp
// a から b へ t の割合だけ進む。fma 1 回で書ける
float Lerp(float a, float b, float t) {
  return std::fma(t, b - a, a);   // t * (b - a) + a
}
```

多項式の評価（ホーナー法）でも、各段に `fma` を使うと、精度と速度の両方が上がります。

## よくあるミス

??? failure "FMA 非対応の環境で、ソフトウェア実装になって極端に遅くなる"
    対象 CPU が FMA に対応しているかを確かめます。

??? failure "`a * b + c` と結果が少し違うのでバグと勘違いする"
    丸めの回数が違うため、最後の桁がずれることがあります。仕様どおりの動作です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`lerp`](lerp.md) | 補間専用の関数（C++20） |
| [`pow`](pow.md) | 累乗 |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `fma(x, y, z)` は `x * y + z` を丸め 1 回で計算する
    - [x] 誤差が小さい。対応 CPU では 1 命令で速い
    - [x] 非対応環境では遅く、通常の式と結果が少し違うことがある

## 関連ページ

- [`std::sqrt`](sqrt.md)
- [cpprefjp: std::fma](https://cpprefjp.github.io/reference/cmath/fma.html)
- [cppreference: std::fma](https://en.cppreference.com/w/cpp/numeric/math/fma)

---
title: std::exp2
summary: "2 の x 乗を求める。"
order: 33
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::exp2

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <cmath>`
</div>

2 の累乗は、コンピューターの世界でとてもよく出てきます。1 オクターブ上がると周波数が 2 倍、ミップマップが 1 段下がると解像度が半分。`pow(2.0, x)` と書いてもよいのですが、底が 2 と決まっているなら、`std::exp2` のほうが速く、正確です。

!!! tip "ポイント"
    - `std::exp2(10.0)` は 1024、`std::exp2(-1.0)` は 0.5
    - 整数の指数では、結果がぴったりの 2 の累乗になる
    - `pow(2.0, x)` と同じ意味で、専用に最適化されている
    - 整数だけで 2 の累乗が欲しいなら、シフト演算 `1 << n` のほうが速い

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::exp2 {#exp2}

<span class="ver ver-11">C++11</span>

```cpp
float exp2(float x);
double exp2(double x);
long double exp2(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 指数。2 の何乗かを指定する |

戻り値は 2 の `x` 乗です。`x` が整数なら、結果は 2 の累乗の値がちょうど表されます。`exp2(0)` は 1、`exp2(0.5)` は √2 に近い値です。

`double` では `x` が 1024 以上になると無限大に、`float` では 128 以上で無限大になります。`x` がとても小さい負の値だと 0 に潰れます。

`pow(2.0, x)` との違いは、実装が専用であることです。多くの環境で `pow` より速く、整数の `x` での誤差が小さくなります。

落とし穴は、整数の 2 の累乗に浮動小数点数の関数を使うことです。`1 << n` のようなシフトのほうが、速く、型もそのまま整数で済みます。`exp2` は、指数が小数のとき（音階の周波数など）に使います。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("exp2(10) = {}", std::exp2(10.0));
  std::println("exp2(-1) = {}", std::exp2(-1.0));

  // 音階の周波数: A4 (440 Hz) から n 半音上
  for (int n : {0, 12, 24}) {
    std::println("{} 半音上: {} Hz", n, 440.0 * std::exp2(n / 12.0));
  }
}
```

```text title="実行結果"
exp2(10) = 1024
exp2(-1) = 0.5
0 半音上: 440 Hz
12 半音上: 880 Hz
24 半音上: 1760 Hz
```

## ゲームでの使いどころ

音の高さと周波数の変換に使います。12 平均律では、1 半音上がるごとに周波数が 2 の 12 分の 1 乗倍になります。

```cpp
// 半音の差 semitones から、再生速度（ピッチ）の倍率を求める
const float pitch = std::exp2(semitones / 12.0f);
```

ミップマップのレベルから解像度の倍率を求める、といった用途でも使います。

## よくあるミス

??? failure "整数の 2 の累乗に `exp2` を使う"
    `1 << n` のようにシフトで書きます。

??? failure "大きな指数で無限大になる"
    `double` で 1024、`float` で 128 を超えないようにします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exp`](exp.md) | 底が e |
| [`pow`](pow.md) | 任意の底 |
| [`log2`](log2.md) | 底 2 の対数（逆の関数） |

## コンパイラ対応

C++11 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `exp2(x)` は 2 の `x` 乗
    - [x] `pow(2.0, x)` より速く正確
    - [x] 音の高さの倍率などで使う。整数ならシフトで書く

## 関連ページ

- [`std::log2`](log2.md)
- [cpprefjp: std::exp2](https://cpprefjp.github.io/reference/cmath/exp2.html)
- [cppreference: std::exp2](https://en.cppreference.com/w/cpp/numeric/math/exp2)

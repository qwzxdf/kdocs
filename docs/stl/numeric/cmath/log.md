---
title: std::log
summary: "自然対数（底が e の対数）を求める。"
order: 18
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::log

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

「経験値が 2 倍になるごとにレベルが 1 上がる」ゲームで、経験値からレベルを逆算したい。音の大きさ（デシベル）を振幅から求めたい。指数的に増える値から「何回掛けたか」を取り出すのが、対数です。

`std::log(x)` は、ネイピア数 e を底とする自然対数を返します。`exp` の逆の関数です。

!!! tip "ポイント"
    - `std::log(1.0)` は 0、`std::log(e)` は 1
    - `x` は正の数。0 は −∞（−無限大）、負の数は NaN
    - 底が 2 なら `log2`、底が 10 なら `log10` を使うほうが正確で読みやすい
    - 任意の底 b の対数は、`log(x) / log(b)`

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::log {#log}

```cpp
float log(float x);
double log(double x);
long double log(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 正の数。対数を取りたい値 |

戻り値は、e を何乗すると `x` になるか、です。`x` が 1 なら 0、e なら 1、1 より大きければ正、0 と 1 の間なら負になります。

`x` が 0 のときは −∞ を返します（極の誤り）。負の値を渡すと NaN を返します（定義域の誤り）。どちらも `errno` が設定されることがありますが、戻り値で判別できます。

任意の底 b の対数は、底の変換公式で `log(x) / log(b)` と求められます。ただし、底が 2 や 10 なら、`log2`・`log10` が専用に用意されていて、丸め誤差が少なく、`log2(8)` がちょうど 3 になるといった利点があります。

落とし穴は、引数が 0 や負になりうる場合の扱いです。経験値が 0 のときに `log(exp)` を呼ぶと −∞ が返り、そのあとの計算（レベルへの変換）を台無しにします。呼ぶ前に 1 以上に補正します。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <numbers>
#include <print>

int main() {
  std::println("log(1)  = {}", std::log(1.0));
  std::println("log(e)  = {}", std::log(std::numbers::e));    // 底 e の対数なので 1
  // 経験値が 2 倍になるごとにレベルが 1 上がる場合のレベル（底 2 の対数）
  const double exp_points = 1000.0;
  std::println("レベル = {}", static_cast<int>(std::log(exp_points) / std::log(2.0)));
}
```

```text title="実行結果"
log(1)  = 0
log(e)  = 1
レベル = 9
```

## ゲームでの使いどころ

指数的に増えるものを人間が感じる大きさ（等間隔）に直すときに使います。音量のデシベル換算、経験値からのレベル、ズーム倍率のスライダーなどです。

```cpp
// ズーム倍率 (0.1 〜 10) をスライダー位置 (−1 〜 +1) に変換
const float slider = std::log10(zoom);
```

底が 2 や 10 のときは `log2`・`log10` を使うほうが読みやすく、正確です。

## よくあるミス

??? failure "0 や負の値を渡して −∞ や NaN になる"
    呼ぶ前に `std::max(x, 1e-6)` などで正の値に補正します。

??? failure "底 2 の対数を `log(x) / log(2)` で求めて、ぴったり整数にならない"
    `std::log2` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`exp`](exp.md) | 指数関数。`log` の逆 |
| [`log2`](log2.md) | 底 2 の対数 |
| [`log10`](log10.md) | 底 10 の対数 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `log(x)` は自然対数。`log(1)` は 0
    - [x] 0 は −∞、負の数は NaN。呼ぶ前に補正する
    - [x] 底 2 や 10 は `log2`・`log10` を使う

## 関連ページ

- [`std::exp`](exp.md)
- [cpprefjp: std::log](https://cpprefjp.github.io/reference/cmath/log.html)
- [cppreference: std::log](https://en.cppreference.com/w/cpp/numeric/math/log)

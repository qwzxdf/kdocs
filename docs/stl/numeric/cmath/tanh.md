---
title: std::tanh
summary: "双曲線正接（tanh）を求める。−1〜1 になだらかに収まる。"
order: 32
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::tanh

<div class="page-badges" markdown>
<span class="rank rank-sometimes">たまに</span>
`#include <cmath>`
</div>

入力がどれだけ大きくても、出力を −1 〜 +1 に収めたい。ニューラルネットの活性化関数、滑らかな上限のかかった加速。そのような S 字型の関数が、双曲線正接 `std::tanh` です。

!!! tip "ポイント"
    - `std::tanh(0.0)` は 0、`std::tanh(1.0)` は約 0.7616
    - 出力は常に −1 〜 +1 に収まる
    - `x` が大きいと ±1 に近づく（飽和）
    - オーバーフローしない

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::tanh {#tanh}

```cpp
float tanh(float x);
double tanh(double x);
long double tanh(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 入力 |

戻り値は `sinh(x) / cosh(x)` で、`(exp(x) - exp(-x)) / (exp(x) + exp(-x))` と同じです。奇関数で、0 のとき 0、大きな正の値で +1、大きな負の値で −1 に近づきます。

`sinh` や `cosh` と違って、出力が有限の範囲に収まるので、オーバーフローしません。実装では、`x` が大きいときに内部でオーバーフローしないよう処理されています。

原点付近の傾きが 1 で、入力を小さい範囲で滑らかに通し、大きい入力は押さえ込む特性があります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("tanh(0)   = {}", std::tanh(0.0));
  std::println("tanh(1)   = {}", std::tanh(1.0));
  std::println("tanh(100) = {}", std::tanh(100.0));   // 飽和して 1
}
```

```text title="実行結果"
tanh(0)   = 0
tanh(1)   = 0.7615941559557649
tanh(100) = 1
```

## ゲームでの使いどころ

入力を滑らかに頭打ちさせる「ソフト クリップ」に使います。たとえば、ゲームパッドのスティックの入力や、ダメージの上限を滑らかにかけます。

```cpp
// 速度を max_speed に滑らかに近づける（上限を超えない）
const float limited = max_speed * std::tanh(speed / max_speed);
```

## よくあるミス

??? failure "範囲を 0〜1 と思う"
    範囲は −1 〜 +1 です。0〜1 にしたいなら、`0.5 * (tanh(x) + 1)`。

## 類似

| 名前 | 違い |
| --- | --- |
| [`sinh`](sinh.md) | 双曲線正弦 |
| [`cosh`](cosh.md) | 双曲線余弦 |
| [`atanh`](atanh.md) | 逆双曲線正接 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `tanh(x)` は −1 〜 +1 に収まる S 字型の関数
    - [x] 大きな入力は ±1 に飽和する
    - [x] ソフト クリップに使える

## 関連ページ

- [cpprefjp: std::tanh](https://cpprefjp.github.io/reference/cmath/tanh.html)
- [cppreference: std::tanh](https://en.cppreference.com/w/cpp/numeric/math/tanh)

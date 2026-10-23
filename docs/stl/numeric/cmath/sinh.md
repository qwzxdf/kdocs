---
title: std::sinh
summary: "双曲線正弦（sinh）を求める。"
order: 30
group: 数学関数（<cmath>）
tags:
  - 数値
---

# std::sinh

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
`#include <cmath>`
</div>

鎖を両端でつるすと、放物線ではなく懸垂線（カテナリー）という曲線になります。吊り橋のケーブルや電線の垂れ下がりを描くとき、この曲線の式に双曲線関数が出てきます。

`std::sinh` は、<strong>双曲線正弦</strong>で、`(exp(x) - exp(-x)) / 2` と定義されます。

!!! tip "ポイント"
    - `std::sinh(0.0)` は 0、`std::sinh(1.0)` は約 1.1752
    - 奇関数: `sinh(-x) = -sinh(x)`
    - `x` が大きいと急激に増え、オーバーフローする
    - 懸垂線の式や、波の計算に出てくる

!!! info "このページを読む前に"
    [`<cmath>`](../cmath.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::sinh {#sinh}

```cpp
float sinh(float x);
double sinh(double x);
long double sinh(long double x);
```

| 引数 | 型 | 意味 |
| --- | --- | --- |
| `x` | 浮動小数点数 | 入力。ラジアンではなく、指数に使われる値 |

戻り値は `(exp(x) - exp(-x)) / 2` です。0 のとき 0、正のとき正、負のとき負で、原点について点対称です。`x` が大きくなると `exp(x) / 2` に近づき、急速に増加します。

`sin` と名前が似ていますが、周期的な関数ではありません。角度ではなく、指数的な増減を表します。

`double` では `x` が約 710 を超えると結果が無限大になります。

## 実際に動かしてみる

```cpp
#include <cmath>
#include <print>

int main() {
  std::println("sinh(0)  = {}", std::sinh(0.0));
  std::println("sinh(1)  = {}", std::sinh(1.0));
  std::println("sinh(-1) = {}", std::sinh(-1.0));
}
```

```text title="実行結果"
sinh(0)  = 0
sinh(1)  = 1.1752011936438014
sinh(-1) = -1.1752011936438014
```

## ゲームでの使いどころ

吊り橋のケーブルの形（懸垂線）は `a * cosh(x / a)` で表されますが、傾きの計算に `sinh` が出てきます。ゲームで使う頻度は高くありません。

## よくあるミス

??? failure "`sin` と同じ周期関数だと思って使う"
    `sinh` は周期を持たず、指数的に増えます。

## 類似

| 名前 | 違い |
| --- | --- |
| [`cosh`](cosh.md) | 双曲線余弦 |
| [`tanh`](tanh.md) | 双曲線正接。−1 〜 1 に収まる |
| [`sin`](sin.md) | 三角関数の正弦 |

## コンパイラ対応

C++98 から使えます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `sinh(x)` は `(exp(x) - exp(-x)) / 2`
    - [x] 奇関数で、大きな `x` では指数的に増える
    - [x] 懸垂線などに出てくる。使う機会は少ない

## 関連ページ

- [`std::cosh`](cosh.md)
- [cpprefjp: std::sinh](https://cpprefjp.github.io/reference/cmath/sinh.html)
- [cppreference: std::sinh](https://en.cppreference.com/w/cpp/numeric/math/sinh)

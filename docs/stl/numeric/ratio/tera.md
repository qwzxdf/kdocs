---
title: std::tera
summary: "SI 接頭辞「tera」（1 兆倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::tera

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

GPU の性能は TFLOPS（1 秒に何兆回の浮動小数点演算ができるか）で表されます。単位に「テラ」が付く量を、1 兆倍の関係として型で扱いたいときに、`std::tera`（テラ、1 兆倍）を使います。`ratio<1000000000000, 1>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1000000000000, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::tera {#tera}

<span class="ver ver-11">C++11</span>

```cpp
using tera = ratio<1000000000000, 1>;
```

`std::tera` は、`std::ratio<1000000000000, 1>` の別名で、値は 1 兆倍 を表します。`std::tera::num` が 1000000000000、`std::tera::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `tera` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ratio>

int main() {
  // GPU の性能 20 TFLOPS のとき、60 fps の 1 フレームあたりの演算回数
  constexpr double flops = 20.0 * std::tera::num;
  std::println("1 秒: {:.3e} 回", flops);
  std::println("1 フレーム (60 fps): {:.3e} 回", flops / 60.0);
  std::println("tera = {}/{}", std::tera::num, std::tera::den);
}
```

```text title="実行結果"
1 秒: 2.000e+13 回
1 フレーム (60 fps): 3.333e+11 回
tera = 1000000000000/1
```

20 TFLOPS の GPU は、1 秒間に 2 × 10^13 回、60 fps なら 1 フレームあたり約 3.3 × 10^11 回の演算ができる計算です。

## ゲームでの使いどころ

GPU 性能の比較や、1 フレームに使える演算量の見積もりで、桁の大きい数を扱うときに使えます。

## よくあるミス

??? failure "int で tera を扱う"
    1 兆は `int` に収まりません。`std::tera::num` の型は `std::intmax_t` です。

??? failure "TFLOPS を実際の速度だと思う"
    理論上の最大値です。メモリの転送などで、実際の速度は大きく下がります。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::tera` は `ratio<1000000000000, 1>` の別名（1 兆倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::tera](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::tera](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

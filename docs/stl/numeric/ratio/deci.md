---
title: std::deci
summary: "SI 接頭辞「deci」（10 分の 1）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::deci

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

長さや時間、容量の単位に「デシ」を付けるとき、`ratio<1, 10>` と数字を書くと、桁の数え間違いを起こしやすくなります。`std::deci` は、SI 接頭辞の「デシ」（10 分の 1）をそのまま表す `std::ratio` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1, 10>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::deci {#deci}

<span class="ver ver-11">C++11</span>

```cpp
using deci = ratio<1, 10>;
```

`std::deci` は、`std::ratio<1, 10>` の別名で、値は 10 分の 1 を表します。`std::deci::num` が 1、`std::deci::den` が 10 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `deci` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <ratio>
#include <print>

int main() {
  std::println("num = {}, den = {}", std::deci::num, std::deci::den);
  // 1000000 に接頭辞の倍率を掛ける（整数で計算するため、分母で割る）
  constexpr long long value = 1000000LL * std::deci::num / std::deci::den;
  std::println("1000000 の deci = {}", value);
}
```

```text title="実行結果"
num = 1, den = 10
1000000 の deci = 100000
```

## ゲームでの使いどころ

日常のゲームのコードでは使う機会が少なく、`std::ratio` の学習や、単位のテンプレートを作るときに登場します。

```cpp
// 3 デシ を、基本単位に直す
constexpr long long value = 3LL * std::deci::num / std::deci::den;
```

## よくあるミス

??? failure "分母・分子を自分で書いて桁を間違える"
    `std::deci` のような名前の付いた別名を使います。

??? failure "バイトの 1024 倍と混同する"
    SI 接頭辞は 1000 倍の系列です。1024 倍の単位は別に定義します。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::deci` は `ratio<1, 10>` の別名（10 分の 1）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::deci](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::deci](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

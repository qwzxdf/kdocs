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

デシベル（dB）の「デシ」は、10 分の 1 を表す接頭辞です。10 分の 1 の関係を型で表したいときに、`std::deci`（デシ、10 分の 1）を使います。`ratio<1, 10>` の別名です。

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
#include <chrono>
#include <print>
#include <ratio>

int main() {
  using DeciSecond = std::chrono::duration<int, std::deci>;   // 1 単位が 0.1 秒

  DeciSecond t{15};
  auto ms = std::chrono::duration_cast<std::chrono::milliseconds>(t);
  std::println("15 デシ秒 = {} ミリ秒", ms.count());

  double seconds = std::chrono::duration<double>(t).count();
  std::println("15 デシ秒 = {} 秒", seconds);
}
```

```text title="実行結果"
15 デシ秒 = 1500 ミリ秒
15 デシ秒 = 1.5 秒
```

15 デシ秒は 1.5 秒、つまり 1500 ミリ秒です。

## ゲームでの使いどころ

0.1 秒刻みのタイマー（連打の受付時間など）を、整数で持ちたいときに使えます。整数で持てば、浮動小数点の誤差が溜まりません。

## よくあるミス

??? failure "deci と deca を取り違える"
    `deci` は 1/10、`deca` は 10 倍です。

??? failure "duration<int, deci> に小数を入れようとする"
    `int` の `duration` に `0.5` は入りません。小数なら `duration<double, ...>` にします。

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

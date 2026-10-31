---
title: std::nano
summary: "SI 接頭辞「nano」（10 億分の 1）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::nano

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

高精度のタイマーは、ナノ秒（10 億分の 1 秒）の刻みで時間を返します。この 10 億分の 1 の関係を型で扱いたいときに、`std::nano`（ナノ、10 億分の 1）を使います。`ratio<1, 1000000000>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1, 1000000000>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::nano {#nano}

<span class="ver ver-11">C++11</span>

```cpp
using nano = ratio<1, 1000000000>;
```

`std::nano` は、`std::ratio<1, 1000000000>` の別名で、値は 10 億分の 1 を表します。`std::nano::num` が 1、`std::nano::den` が 1000000000 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

`std::chrono` では、時間の単位を `duration<double, std::nano>` のように指定します。1 つの単位から別の単位への変換は、分数の掛け算としてコンパイル時に計算されます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `nano` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <ratio>

int main() {
  // steady_clock の刻み(period)が何秒か
  using Period = std::chrono::steady_clock::period;
  std::println("steady_clock の刻み: {}/{} 秒", Period::num, Period::den);
  std::println("ナノ秒単位か: {}", Period::den == std::nano::den);

  // 1 秒は何ナノ秒か
  std::chrono::duration<long long, std::nano> one = std::chrono::seconds(1);
  std::println("1 秒 = {} ナノ秒", one.count());
}
```

```text title="実行結果"
steady_clock の刻み: 1/1000000000 秒
ナノ秒単位か: true
1 秒 = 1000000000 ナノ秒
```

MSVC の `steady_clock` は、刻みがナノ秒です。環境によって刻みは違い、たとえば Linux の GCC / Clang でも、通常はナノ秒ですが、仕様では保証されません。

## ゲームでの使いどころ

`std::chrono::steady_clock` の刻みを調べたり、ナノ秒単位の計測値を、整数のまま持ったりするときに使います。ただし、実際に測れる精度は、刻みより粗いことが普通です。

## よくあるミス

??? failure "刻みがナノ秒だから、ナノ秒の精度で測れると思う"
    `period` は表現の刻みで、時計の精度ではありません。実際の精度は、OS とハードウェア次第です。

??? failure "nanoseconds を int に入れて桁あふれ"
    10 億ナノ秒で 1 秒です。`int` は約 2 秒で超えます。`long long` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::nano` は `ratio<1, 1000000000>` の別名（10 億分の 1）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::nano](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::nano](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

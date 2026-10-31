---
title: std::milli
summary: "SI 接頭辞「milli」（1000 分の 1）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::milli

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

1 フレームは 16.7 ミリ秒、ネットワークの遅延は 30 ミリ秒。ゲームの時間は、ミリ秒で語ることが多く、その 1/1000 の関係を型で扱いたいときに、`std::milli`（ミリ、1000 分の 1）を使います。`ratio<1, 1000>` の別名です。`std::chrono::milliseconds` の正体は `duration<..., std::milli>` です。

!!! tip "ポイント"
    - 中身は `std::ratio<1, 1000>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::milli {#milli}

<span class="ver ver-11">C++11</span>

```cpp
using milli = ratio<1, 1000>;
```

`std::milli` は、`std::ratio<1, 1000>` の別名で、値は 1000 分の 1 を表します。`std::milli::num` が 1、`std::milli::den` が 1000 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

`std::chrono` では、時間の単位を `duration<double, std::milli>` のように指定します。1 つの単位から別の単位への変換は、分数の掛け算としてコンパイル時に計算されます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `milli` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <ratio>
#include <type_traits>

int main() {
  // std::chrono::milliseconds は、milli を単位にした duration
  static_assert(std::is_same_v<std::chrono::milliseconds::period, std::milli>);

  // 60 fps の 1 フレームの長さ(ミリ秒、小数あり)
  std::chrono::duration<double, std::milli> frame(1000.0 / 60.0);
  std::println("1 フレーム = {:.2f} ミリ秒", frame.count());

  // 秒への換算
  std::chrono::duration<double> sec = frame;
  std::println("= {:.5f} 秒", sec.count());
}
```

```text title="実行結果"
1 フレーム = 16.67 ミリ秒
= 0.01667 秒
```

`std::chrono::milliseconds` は、`milli` を単位にした `duration` の別名です。小数のミリ秒が欲しいときは、`duration<double, std::milli>` を使います。

## ゲームでの使いどころ

フレーム時間の表示（16.67 ms）や、ネットワークの遅延の記録、タイムアウトの設定など、ゲームでは最もよく使う SI 接頭辞です。

## よくあるミス

??? failure "milliseconds に小数を入れて切り捨てられる"
    `std::chrono::milliseconds` は整数です。`16.67` ms を入れると、切り捨てられて 16 ms になります。`duration<double, std::milli>` を使います。

??? failure "milli と micro を取り違える"
    `milli` は 1/1000、`micro` は 1/1000000 です。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::milli` は `ratio<1, 1000>` の別名（1000 分の 1）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::milli](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::milli](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

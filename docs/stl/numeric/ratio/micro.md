---
title: std::micro
summary: "SI 接頭辞「micro」（100 万分の 1）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::micro

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

プロファイラの計測結果や、1 回の関数呼び出しの時間は、マイクロ秒（100 万分の 1 秒）で語ります。この 100 万分の 1 の関係を型で扱いたいときに、`std::micro`（マイクロ、100 万分の 1）を使います。`ratio<1, 1000000>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1, 1000000>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::micro {#micro}

<span class="ver ver-11">C++11</span>

```cpp
using micro = ratio<1, 1000000>;
```

`std::micro` は、`std::ratio<1, 1000000>` の別名で、値は 100 万分の 1 を表します。`std::micro::num` が 1、`std::micro::den` が 1000000 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

`std::chrono` では、時間の単位を `duration<double, std::micro>` のように指定します。1 つの単位から別の単位への変換は、分数の掛け算としてコンパイル時に計算されます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `micro` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <chrono>
#include <print>
#include <ratio>

int main() {
  // 処理にかかった時間を、マイクロ秒の小数で持つ
  std::chrono::duration<double, std::micro> cost(250.5);
  std::println("処理時間: {} マイクロ秒", cost.count());

  // ミリ秒に直す (1000 マイクロ秒 = 1 ミリ秒)
  std::chrono::duration<double, std::milli> in_ms = cost;
  std::println("= {} ミリ秒", in_ms.count());

  // 1 マイクロ秒は、1 秒の何分の 1 か
  std::println("micro = {}/{}", std::micro::num, std::micro::den);
}
```

```text title="実行結果"
処理時間: 250.5 マイクロ秒
= 0.2505 ミリ秒
micro = 1/1000000
```

250.5 マイクロ秒は 0.2505 ミリ秒です。`duration` どうしの換算は、`ratio` の割り算で、コンパイル時に決まります。

## ゲームでの使いどころ

`std::chrono::steady_clock` で計測した 1 回の処理の時間を、マイクロ秒で表示するときに使います。1 フレームのうち、更新、描画などの内訳を出す、簡易プロファイラで役に立ちます。

## よくあるミス

??? failure "micro を μ（ミュー）と別物だと思う"
    マイクロ秒の記号は μs ですが、`std::micro` は同じ意味です。文字として `μ` を使うときは、UTF-8 の扱いに注意します。

??? failure "microseconds に小数の値を入れて切り捨て"
    `std::chrono::microseconds` は整数です。小数が必要なら、`duration<double, std::micro>` にします。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::micro` は `ratio<1, 1000000>` の別名（100 万分の 1）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::micro](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::micro](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

---
title: std::kilo
summary: "SI 接頭辞「kilo」（1000 倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::kilo

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

長さや時間、容量の単位に「キロ」を付けるとき、`ratio<1000, 1>` と数字を書くと、桁の数え間違いを起こしやすくなります。`std::kilo` は、SI 接頭辞の「キロ」（1000 倍）をそのまま表す `std::ratio` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1000, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::kilo {#kilo}

<span class="ver ver-11">C++11</span>

```cpp
using kilo = ratio<1000, 1>;
```

`std::kilo` は、`std::ratio<1000, 1>` の別名で、値は 1000 倍 を表します。`std::kilo::num` が 1000、`std::kilo::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

`std::chrono` では、時間の単位を `duration<double, std::kilo>` のように指定します。1 つの単位から別の単位への変換は、分数の掛け算としてコンパイル時に計算されます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `kilo` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <ratio>
#include <print>

int main() {
  std::println("num = {}, den = {}", std::kilo::num, std::kilo::den);
  constexpr long long value = 3LL * std::kilo::num / std::kilo::den;
  std::println("3 kilo = {}", value);
}
```

```text title="実行結果"
num = 1000, den = 1
3 kilo = 3000
```

## ゲームでの使いどころ

データの大きさや周波数など、大きな量を扱うときに、桁の数え間違いを避けるために使います。ただし、バイトの単位としての 1024 倍（KiB、MiB）は、SI 接頭辞の 1000 倍とは別なので、`std::kilo` はそのまま使えません。

```cpp
// 3 キロ を基本単位に直す
constexpr long long value = 3LL * std::kilo::num / std::kilo::den;
```

## よくあるミス

??? failure "分母・分子を自分で書いて桁を間違える"
    `std::kilo` のような名前の付いた別名を使います。

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
    - [x] `std::kilo` は `ratio<1000, 1>` の別名（1000 倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::kilo](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::kilo](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

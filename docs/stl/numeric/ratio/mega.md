---
title: std::mega
summary: "SI 接頭辞「mega」（100 万倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::mega

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

長さや時間、容量の単位に「メガ」を付けるとき、`ratio<1000000, 1>` と数字を書くと、桁の数え間違いを起こしやすくなります。`std::mega` は、SI 接頭辞の「メガ」（100 万倍）をそのまま表す `std::ratio` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1000000, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::mega {#mega}

<span class="ver ver-11">C++11</span>

```cpp
using mega = ratio<1000000, 1>;
```

`std::mega` は、`std::ratio<1000000, 1>` の別名で、値は 100 万倍 を表します。`std::mega::num` が 1000000、`std::mega::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `mega` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <ratio>
#include <print>

int main() {
  std::println("num = {}, den = {}", std::mega::num, std::mega::den);
  constexpr long long value = 3LL * std::mega::num / std::mega::den;
  std::println("3 mega = {}", value);
}
```

```text title="実行結果"
num = 1000000, den = 1
3 mega = 3000000
```

## ゲームでの使いどころ

データの大きさや周波数など、大きな量を扱うときに、桁の数え間違いを避けるために使います。ただし、バイトの単位としての 1024 倍（KiB、MiB）は、SI 接頭辞の 1000 倍とは別なので、`std::kilo` はそのまま使えません。

```cpp
// 3 メガ を基本単位に直す
constexpr long long value = 3LL * std::mega::num / std::mega::den;
```

## よくあるミス

??? failure "分母・分子を自分で書いて桁を間違える"
    `std::mega` のような名前の付いた別名を使います。

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
    - [x] `std::mega` は `ratio<1000000, 1>` の別名（100 万倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::mega](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::mega](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

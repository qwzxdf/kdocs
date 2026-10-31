---
title: std::peta
summary: "SI 接頭辞「peta」（1000 兆倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::peta

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

大規模なサービスのログや、ゲームのサーバーの統計は、ペタバイト（PB）の規模で語られることがあります。単位に「ペタ」が付く量を、1000 兆倍の関係として型で扱いたいときに、`std::peta`（ペタ、1000 兆倍）を使います。`ratio<1000000000000000, 1>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1000000000000000, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::peta {#peta}

<span class="ver ver-11">C++11</span>

```cpp
using peta = ratio<1000000000000000, 1>;
```

`std::peta` は、`std::ratio<1000000000000000, 1>` の別名で、値は 1000 兆倍 を表します。`std::peta::num` が 1000000000000000、`std::peta::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `peta` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ratio>

int main() {
  // 1 ペタバイトは何バイトか
  constexpr long long bytes = std::peta::num;
  std::println("1 PB = {} バイト", bytes);

  // 1 日 100 TB のログが出るサービスが、1 PB に達するまでの日数
  constexpr long long per_day = 100LL * 1'000'000'000'000LL;
  std::println("1 PB まで {} 日", bytes / per_day);
}
```

```text title="実行結果"
1 PB = 1000000000000000 バイト
1 PB まで 10 日
```

1 日に 100 TB のログを出すサービスでも、1 PB に達するまでに 10 日かかります。

## ゲームでの使いどころ

ゲーム本体のコードに出てくることはほとんどありません。運営側のログの集計や、容量の見積もりを扱うツールで、桁の大きさを、型で表すときに使えます。

## よくあるミス

??? failure "peta の計算がすぐあふれる"
    `peta` は 10 の 15 乗です。`std::intmax_t` の範囲（約 9.2 × 10^18）には、9000 倍までしか収まりません。

??? failure "PB と PiB を同じだと思う"
    `peta` は 10 の 15 乗、PiB は 2 の 50 乗で、約 13% 違います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::peta` は `ratio<1000000000000000, 1>` の別名（1000 兆倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::peta](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::peta](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)

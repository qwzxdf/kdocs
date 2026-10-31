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

オーディオのサンプリング周波数 48 kHz や、距離 1.5 km のように、単位に「キロ」が付く量を、1000 倍の関係として型で扱いたいときに、`std::kilo`（キロ、1000 倍）を使います。`ratio<1000, 1>` の別名です。

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
#include <chrono>
#include <print>
#include <ratio>

int main() {
  // 周波数: 48 kHz のサンプル数/秒
  constexpr long long hz = 48LL * std::kilo::num / std::kilo::den;
  std::println("48 kHz = {} Hz", hz);

  // 1 キロ秒 (1000 秒)
  std::chrono::duration<int, std::kilo> ks{2};
  std::println("2 キロ秒 = {} 秒", std::chrono::duration_cast<std::chrono::seconds>(ks).count());

  // 容量: SI 接頭辞の 1 kB は 1000 バイト。1024 バイトは KiB(キビバイト)
  std::println("1 kB = {} バイト", std::kilo::num);
}
```

```text title="実行結果"
48 kHz = 48000 Hz
2 キロ秒 = 2000 秒
1 kB = 1000 バイト
```

`kilo` は 1000 倍です。ストレージの容量表示で見かける 1 KB = 1024 バイトは、SI 接頭辞とは別の 2 進接頭辞で、`kilo` では表せません。

## ゲームでの使いどころ

サンプリング周波数やファイルのサイズを扱うコードで、「千」の関係を書くときに使います。ファイルのサイズを 1024 で換算するコードに `kilo` を使うと、誤差が出ます。

## よくあるミス

??? failure "1 KB を 1024 バイトとして kilo で換算する"
    `std::kilo` は 1000 倍です。1024 倍は、`ratio<1024, 1>` と自分で書くか、定数にします。

??? failure "kilo を duration の単位にして秒だと思う"
    `duration<int, std::kilo>` の 1 単位は 1000 秒です。

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

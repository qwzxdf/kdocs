---
title: std::giga
summary: "SI 接頭辞「giga」（10 億倍）を表す `ratio` の別名。"
order: 900
tags:
  - 数値
---

# std::giga

<div class="page-badges" markdown>
<span class="rank rank-rare">知ってるだけ</span>
<span class="ver ver-11">C++11</span>
`#include <ratio>`
</div>

VRAM が 8 GB、CPU が 3 GHz。単位に「ギガ」が付く量を、10 億倍の関係として型で扱いたいときに、`std::giga`（ギガ、10 億倍）を使います。`ratio<1000000000, 1>` の別名です。

!!! tip "ポイント"
    - 中身は `std::ratio<1000000000, 1>`
    - `::num`（分子）と `::den`（分母）をコンパイル時の定数として取り出せる
    - `std::chrono::duration` の単位（第 2 テンプレート引数）として使う
    - 型の別名であり、関数ではない（値は持たない）

!!! info "このページを読む前に"
    [`<ratio>`](../ratio.md) の概要を先に読むと分かりやすいです。

## 関数の詳しい説明

### std::giga {#giga}

<span class="ver ver-11">C++11</span>

```cpp
using giga = ratio<1000000000, 1>;
```

`std::giga` は、`std::ratio<1000000000, 1>` の別名で、値は 10 億倍 を表します。`std::giga::num` が 1000000000、`std::giga::den` が 1 で、いずれもコンパイル時の定数です。実行時のコストはありません。

`std::ratio` は分数を型で表す仕組みで、分子・分母は約分された形で保持されます。接頭辞の別名は、よく使う分数に名前を付けたものです。

単位の変換を型で表したいとき、この別名を `std::ratio_multiply` などと組み合わせて使えます。

分母や分子が `std::intmax_t` に収まらない接頭辞（`yotta`、`zetta` など）は、環境によっては定義されません。このページの `giga` は、64 ビットの範囲に収まるので、どの環境でも使えます。

## 実際に動かしてみる

```cpp
#include <print>
#include <ratio>

int main() {
  // メーカー表示の 8 GB (SI 接頭辞 = 10^9) と、OS が数える 8 GiB (2^30) は、別の量
  constexpr long long gb = 8LL * std::giga::num;
  constexpr long long gib = 8LL * (1LL << 30);
  std::println("8 GB  = {} バイト", gb);
  std::println("8 GiB = {} バイト", gib);
  std::println("差: {} バイト ({:.1f}%)", gib - gb, 100.0 * (gib - gb) / gb);
}
```

```text title="実行結果"
8 GB  = 8000000000 バイト
8 GiB = 8589934592 バイト
差: 589934592 バイト (7.4%)
```

メーカーの「8 GB」と、OS が数える「8 GiB」は、約 7% の違いがあります。`std::giga` は前者の 10 億倍で、後者は 1024 の累乗です。

## ゲームでの使いどころ

VRAM やストレージの容量の換算で、メーカー表示と OS 表示のずれを、説明するときに使えます。クロック周波数（GHz）を扱う処理にも出てきます。

## よくあるミス

??? failure "1 GB を 1024 × 1024 × 1024 バイトだと思う"
    `std::giga` は 10 億です。2 進接頭辞の GiB を使うなら、`1LL << 30` と書きます。

??? failure "int で受けて桁あふれ"
    10 億は `int` に収まりますが、数 GB の掛け算はあふれます。`long long` を使います。

## 類似

| 名前 | 違い |
| --- | --- |
| [`std::ratio`](../ratio.md) | 分数を型で表す基本の仕組み |
| [`std::chrono::duration`](../../utilities/chrono/duration.md) | 時間を単位つきで表す |

## コンパイラ対応

C++11 から使えます。`<ratio>` で宣言されます。主要なコンパイラのすべてで使えます。

## これだけ覚える

!!! abstract "まとめ"
    - [x] `std::giga` は `ratio<1000000000, 1>` の別名（10 億倍）
    - [x] `::num` と `::den` が定数として取れる
    - [x] `duration` の単位などに使う

## 関連ページ

- [cpprefjp: std::giga](https://cpprefjp.github.io/reference/ratio/ratio.html)
- [cppreference: std::giga](https://en.cppreference.com/w/cpp/numeric/ratio/ratio)
